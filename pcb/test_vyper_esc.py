"""Mechanical, voltage-margin and first-order loss checks for VYPER-55A EVT.

Run from the repository root:  python3 pcb/test_vyper_esc.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import vyper_esc_layout as L

fails = []


def check(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        fails.append(name)


def rect(pos, wh):
    x, y = pos
    w, h = wh
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def overlap(a, b, gap=0.0):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0]
                or a[3] + gap <= b[1] or b[3] + gap <= a[1])


def rect_circle_overlap(r, cx, cy, radius):
    nx = min(max(cx, r[0]), r[2])
    ny = min(max(cy, r[1]), r[3])
    return math.hypot(cx - nx, cy - ny) < radius


def inside_rounded_outline(r):
    w2, h2, cr = L.BOARD_W / 2, L.BOARD_H / 2, L.CORNER_R
    for x, y in ((r[0], r[1]), (r[0], r[3]), (r[2], r[1]), (r[2], r[3])):
        if abs(x) > w2 or abs(y) > h2:
            return False
        if abs(x) > w2 - cr and abs(y) > h2 - cr:
            if math.hypot(abs(x) - (w2 - cr), abs(y) - (h2 - cr)) > cr:
                return False
    return True


print("=== board and airframe ===")
corner_reach = math.sqrt(2) * (L.BOARD_W / 2 - L.CORNER_R) + L.CORNER_R
check("rounded board fits fuselage", corner_reach <= L.FUSE_CAVITY_R - 0.4,
      f"corner reach {corner_reach:.2f} mm vs cavity R{L.FUSE_CAVITY_R:.1f}")
check("mount pattern matches FC and shelf", L.HOLE_PITCH == 30.5,
      f"{L.HOLE_PITCH} x {L.HOLE_PITCH} mm")
check("six-layer power stack declared", L.LAYERS == 6 and L.OUTER_COPPER_OZ >= 2,
      f"{L.LAYERS} layers, {L.OUTER_COPPER_OZ} oz outer copper")

edge_clearance = 0.5
bad = 0
for channel, pads in L.MOTOR_PADS.items():
    radial_size = L.MOTOR_PAD_SIZE[1]
    for x, y in pads:
        radial_edge = max(abs(x), abs(y)) + radial_size / 2
        if radial_edge > L.BOARD_W / 2 - edge_clearance:
            bad += 1
check("motor pads clear board edge", bad == 0,
      f"12 pads retain >= {edge_clearance:.1f} mm copper clearance")

bad = 0
for name, spec in L.PARTS.items():
    if not inside_rounded_outline(rect(spec["pos"], spec["courtyard"])):
        print(f"[FAIL] {name} leaves rounded board")
        bad += 1
check("all courtyards inside outline", bad == 0, f"{len(L.PARTS)} parts checked")

print("\n=== placement interactions ===")
names = list(L.PARTS)
bad = 0
for i, a in enumerate(names):
    A = L.PARTS[a]
    for b in names[i + 1:]:
        B = L.PARTS[b]
        if A["side"] == B["side"] and overlap(
                rect(A["pos"], A["courtyard"]),
                rect(B["pos"], B["courtyard"]), gap=0.15):
            print(f"[FAIL] courtyard collision: {a} / {b}")
            bad += 1
check("same-face courtyards clear", bad == 0, "0.15 mm assembly gap required")

bad = 0
for hx, hy in L.HOLES:
    for name, spec in L.PARTS.items():
        if rect_circle_overlap(rect(spec["pos"], spec["courtyard"]), hx, hy,
                               L.HARDWARE_KEEPOUT_D / 2):
            print(f"[FAIL] mount keepout at ({hx:+.2f},{hy:+.2f}) hits {name}")
            bad += 1
check("M3 hardware keepouts clear", bad == 0,
      f"4 x diameter {L.HARDWARE_KEEPOUT_D:.1f} mm, both faces")

bad = 0
for channel in L.CHANNELS:
    drv = L.PARTS[f"U_DRV_{channel}"]["pos"]
    farthest = 0.0
    for phase in "ABC":
        q = L.PARTS[f"Q_{channel}_{phase}_HS"]["pos"]
        farthest = max(farthest, math.dist(drv, q))
    if farthest > 10.0:
        bad += 1
        print(f"[FAIL] {channel} driver-to-FET centre run {farthest:.1f} mm")
check("gate-driver loops compact", bad == 0,
      "all driver-to-high-side FET centre distances <= 10 mm")

for channel in L.CHANNELS:
    for phase in "ABC":
        hi = L.PARTS[f"Q_{channel}_{phase}_HS"]["pos"]
        lo = L.PARTS[f"Q_{channel}_{phase}_LS"]["pos"]
        check(f"{channel}{phase} half bridge vertically registered", hi == lo,
              f"top/bottom centres {hi}")

print("\n=== electrical design margins (requirements) ===")
check("MOSFET voltage headroom", L.MOSFET_VDS_V >= 2 * L.PACK_FULL_V,
      f"{L.MOSFET_VDS_V:.0f} V FET / {L.PACK_FULL_V:.1f} V full pack = "
      f"{L.MOSFET_VDS_V / L.PACK_FULL_V:.2f}x")
check("gate driver survives clamp target", L.DRIVER_ABS_MAX_V > L.TRANSIENT_LIMIT_V,
      f"driver abs max {L.DRIVER_ABS_MAX_V:.0f} V > transient gate "
      f"{L.TRANSIENT_LIMIT_V:.0f} V")
check("transient gate below FET rating", L.TRANSIENT_LIMIT_V <= L.MOSFET_VDS_V - 10,
      f"{L.TRANSIENT_LIMIT_V:.0f} V leaves {L.MOSFET_VDS_V - L.TRANSIENT_LIMIT_V:.0f} V")
check("speed-run burst covers motor bench peak", L.CHANNEL_BURST_A_TARGET >= 45 * 1.2,
      f"{L.CHANNEL_BURST_A_TARGET:.0f} A target vs 45 A motor point")

# Six-step BLDC has two FETs in the current path.  Doubling the 25 C Rds(on)
# is a conservative first-order hot-junction screening assumption; switching,
# copper and connector losses are deliberately NOT hidden inside this number.
for current, label in ((L.CHANNEL_CONTINUOUS_A_TARGET, "continuous"),
                       (L.CHANNEL_BURST_A_TARGET, "2 s burst")):
    conduction = 2 * current ** 2 * L.FET_RDS_ON_HOT_DESIGN_OHM
    print(f"  {label:10s}: first-order hot conduction loss {conduction:.1f} W/channel")
check("burst is explicitly time limited", L.BURST_DURATION_S <= 2.0,
      f"{L.BURST_DURATION_S:.1f} s; rating requires dyno and thermal validation")

active_cost = sum(L.ACTIVE_PART_COST_USD.values())
print(f"  active power/control parts snapshot: ${active_cost:.2f}, before passives/PCB/assembly")
check("prototype budget is not misrepresented", active_cost > 50.0,
      "custom ESC cannot honestly be included in a sub-$200 one-off aircraft")

print()
if fails:
    print(f"{len(fails)} FAILED: {', '.join(sorted(set(fails)))}")
    raise SystemExit(1)
print("all checks passed -- mechanical/electrical screening only; NOT flight-qualified")
