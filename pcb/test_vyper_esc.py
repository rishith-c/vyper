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
check("vertical ESC outline", L.BOARD_W == 30.0 and L.BOARD_H == 72.0,
      f"{L.BOARD_W:.0f} x {L.BOARD_H:.0f} mm")
check("cassette mount pattern", (L.MOUNT_PITCH_X, L.MOUNT_PITCH_Y, L.HOLE_D)
      == (24.0, 64.0, 2.4),
      f"{L.MOUNT_PITCH_X:.0f} x {L.MOUNT_PITCH_Y:.0f} mm, M2 clearance")
check("six-layer heavy-copper stack declared",
      L.LAYERS == 6 and L.OUTER_COPPER_OZ >= 3 and L.INNER_COPPER_OZ >= 2,
      f"{L.LAYERS} layers, {L.OUTER_COPPER_OZ}/{L.INNER_COPPER_OZ} oz")
check("isolated heat spreader envelope",
      L.HEAT_SPREADER_W <= L.BOARD_W - 2.0
      and (L.HEAT_SPREADER_SEGMENT_COUNT * L.HEAT_SPREADER_SEGMENT_H
           + L.HEAT_SPREADER_CENTER_GAP) <= L.BOARD_H - 4.0
      and L.THERMAL_PAD_MIN_BREAKDOWN_V >= 1000,
      f"{L.HEAT_SPREADER_SEGMENT_COUNT} x "
      f"{L.HEAT_SPREADER_W:.0f}x{L.HEAT_SPREADER_SEGMENT_H:.1f}x"
      f"{L.HEAT_SPREADER_T:.1f} mm, {L.HEAT_SPREADER_CENTER_GAP:.0f} mm gap, "
      "dielectric >= "
      f"{L.THERMAL_PAD_MIN_BREAKDOWN_V} V")

edge_clearance = 0.5
bad = 0
for channel, pads in L.MOTOR_PADS.items():
    for x, y in pads:
        pad = rect((x, y), L.MOTOR_PAD_SIZE)
        if (pad[0] < -L.BOARD_W / 2 + edge_clearance
                or pad[2] > L.BOARD_W / 2 - edge_clearance
                or pad[1] < -L.BOARD_H / 2 + edge_clearance
                or pad[3] > L.BOARD_H / 2 - edge_clearance):
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
check("M2 hardware keepouts clear", bad == 0,
      f"4 x M2 keepout diameter {L.HARDWARE_KEEPOUT_D:.1f} mm, both faces")

bad = 0
for channel in L.CHANNELS:
    drv = L.PARTS[f"U_DRV_{channel}"]["pos"]
    farthest = 0.0
    for phase in "ABC":
        for role in ("HS", "LS"):
            q = L.PARTS[f"Q_{channel}_{phase}_{role}"]["pos"]
            farthest = max(farthest, math.dist(drv, q))
    if farthest > 8.5:
        bad += 1
        print(f"[FAIL] {channel} driver-to-FET centre run {farthest:.1f} mm")
check("gate-driver loops compact", bad == 0,
      "all driver-to-FET centre distances <= 8.5 mm")

for channel in L.CHANNELS:
    for phase in "ABC":
        hi = L.PARTS[f"Q_{channel}_{phase}_HS"]["pos"]
        lo = L.PARTS[f"Q_{channel}_{phase}_LS"]["pos"]
        check(f"{channel}{phase} half bridge aligned on cooling face",
              hi[0] == lo[0] and hi[1] < lo[1]
              and L.PARTS[f"Q_{channel}_{phase}_HS"]["side"] == "F"
              and L.PARTS[f"Q_{channel}_{phase}_LS"]["side"] == "F",
              f"HS {hi}, LS {lo}")

for lower, upper in zip(L.CHANNELS, L.CHANNELS[1:]):
    lower_edge = max(rect(spec["pos"], spec["courtyard"])[3]
                     for name, spec in L.PARTS.items()
                     if name.startswith(f"Q_{lower}_"))
    upper_edge = min(rect(spec["pos"], spec["courtyard"])[1]
                     for name, spec in L.PARTS.items()
                     if name.startswith(f"Q_{upper}_"))
    check(f"{lower}/{upper} inverter-cell separation", upper_edge >= lower_edge + 0.15,
          f"{upper_edge - lower_edge:.2f} mm courtyard gap")

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
ocp_at_hot_screen = L.VDS_OCP_NOMINAL_V / L.FET_RDS_ON_HOT_DESIGN_OHM
check("VDS OCP guards burst region", ocp_at_hot_screen >= 0.9 * L.CHANNEL_BURST_A_TARGET,
      f"nominal {ocp_at_hot_screen:.1f} A at conservative hot Rds(on); must be scoped")
logic_load = L.MCU_COUNT * L.MCU_MAX_105C_A
check("logic regulator DC margin", L.BUCK_OUTPUT_A >= 2 * logic_load,
      f"{L.BUCK_OUTPUT_A * 1000:.0f} mA vs {logic_load * 1000:.1f} mA MCU maximum")

# Six-step BLDC has two FETs in the current path.  Doubling the 25 C Rds(on)
# is a conservative first-order hot-junction screening assumption; switching,
# copper and connector losses are deliberately NOT hidden inside this number.
for current, label in ((L.CHANNEL_CONTINUOUS_A_TARGET, "continuous"),
                       (L.CHANNEL_BURST_A_TARGET, "2 s burst")):
    conduction = 2 * current ** 2 * L.FET_RDS_ON_HOT_DESIGN_OHM
    print(f"  {label:10s}: first-order hot conduction loss {conduction:.1f} W/channel")
shunt_burst = L.CHANNEL_BURST_A_TARGET ** 2 * L.SHUNT_OHM
check("current shunt burst loss margin", shunt_burst <= L.SHUNT_POWER_W / 2,
      f"{shunt_burst:.2f} W at {L.CHANNEL_BURST_A_TARGET:.0f} A vs {L.SHUNT_POWER_W:.0f} W part")
current_scale = 1000 * L.SHUNT_OHM * L.CSA_GAIN_V_PER_V
check("AM32 current scale", abs(current_scale - 5.0) < 1e-9,
      f"{current_scale:.1f} mV/A at PA2 and summed FC output")
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
