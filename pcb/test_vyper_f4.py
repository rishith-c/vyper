"""VYPER-F4 interaction checks. Nothing goes to fab until this passes.

Reads the same vyper_f4_layout.py the generator emits from, so what is
checked is what is built. Covers the interactions that scrap FC spins:
holes vs pads, courtyard vs courtyard, grommet keepouts, board-vs-fuselage,
and the gyro placement rules from the Betaflight manufacturer guidelines.

Run:  python3 test_vyper_f4.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import vyper_f4_layout as L

fails = []


def check(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        fails.append(name)


def rect(pos, wh):
    (x, y), (w, h) = pos, wh
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def rects_overlap(a, b, gap=0.0):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0]
                or a[3] + gap <= b[1] or b[3] + gap <= a[1])


def rect_circle_overlap(r, cx, cy, cr):
    nx = min(max(cx, r[0]), r[2])
    ny = min(max(cy, r[1]), r[3])
    return math.hypot(cx - nx, cy - ny) < cr


# ---------------------------------------------------------------- pattern
print("=== mounting pattern ===")
check("vertical FC outline", (L.BOARD_W, L.BOARD_H) == (30.0, 64.0),
      f"{L.BOARD_W:.0f} x {L.BOARD_H:.0f} mm")
check("cassette soft-mount pattern",
      (L.HOLE_PITCH_X, L.HOLE_PITCH_Y) == (16.0, 56.0),
      f"{L.HOLE_PITCH_X:.0f} x {L.HOLE_PITCH_Y:.0f} mm")
edge_x = L.BOARD_W / 2 - L.HOLE_PITCH_X / 2 - L.HOLE_D / 2
edge_y = L.BOARD_H / 2 - L.HOLE_PITCH_Y / 2 - L.HOLE_D / 2
check("hole edge to board edge", min(edge_x, edge_y) >= 1.0,
      f"{edge_x:.2f} mm transverse / {edge_y:.2f} mm longitudinal web")
check("grommet bore", L.HOLE_D == 3.2,
      f"{L.HOLE_D} mm M2 soft-mount bore")

# ---------------------------------------------------------- board vs cassette
print("\n=== board vs vertical cassette ===")
check("FC is narrower than ESC", L.BOARD_W < 36.0 and L.BOARD_H < 72.0,
      "30 x 64 FC nests behind the 36 x 72 ESC")

# ---------------------------------------------------------------- gyro rules
print("\n=== gyro placement (Betaflight mfr guidelines) ===")
gyro = L.PARTS["U2_gyro_ICM42688P"]
gx, gy = gyro["pos"]
check("gyro near centre", math.hypot(gx, gy) <= L.GYRO_MAX_OFFCENTRE,
      f"{math.hypot(gx, gy):.1f} mm off centre (limit {L.GYRO_MAX_OFFCENTRE})")
worst = ("", 1e9)
for name, spec in L.PARTS.items():
    if spec.get("noisy"):
        d = math.hypot(spec["pos"][0] - gx, spec["pos"][1] - gy)
        if d < worst[1]:
            worst = (name, d)
check("gyro clear of switching parts", worst[1] >= L.GYRO_MIN_TO_NOISY,
      f"nearest noisy part {worst[0]} at {worst[1]:.1f} mm "
      f"(inductor fields read as vibration; rule >= {L.GYRO_MIN_TO_NOISY})")
mcu = L.PARTS["U1_mcu_STM32F405RGT6"]
d_mcu = (math.hypot(mcu["pos"][0] - gx, mcu["pos"][1] - gy)
         - mcu["courtyard"][1] / 2 - gyro["courtyard"][1] / 2)
check("gyro-to-MCU SPI run", d_mcu < L.GYRO_MCU_TRACE_MAX,
      f"~{max(d_mcu, 0):.1f} mm courtyard gap (guideline < {L.GYRO_MCU_TRACE_MAX} mm)")

# ------------------------------------------------------ courtyard interactions
print("\n=== courtyard / pad / hole interactions ===")
worst_pair = ("none", False)
names = list(L.PARTS)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        A, B = L.PARTS[a], L.PARTS[b]
        if A["side"] != B["side"]:
            continue
        if rects_overlap(rect(A["pos"], A["courtyard"]),
                         rect(B["pos"], B["courtyard"])):
            check(f"{a} vs {b}", False, "courtyards overlap")
            worst_pair = (f"{a}/{b}", True)
check("part courtyards disjoint per side", not worst_pair[1],
      "every same-side courtyard pair checked")

PAD_W, PAD_H = L.IO_PAD_SIZE
bad = 0
for group, pads in L.PAD_GROUPS.items():
    for x, y, label in pads:
        pr = rect((x, y), (PAD_W, PAD_H))
        for name, spec in L.PARTS.items():
            if spec["side"] != "F":
                continue
            if rects_overlap(pr, rect(spec["pos"], spec["courtyard"]), gap=0.2):
                check(f"pad {label} vs {name}", False, "pad inside courtyard")
                bad += 1
check("solder pads clear of courtyards", bad == 0,
      f"{sum(len(p) for p in L.PAD_GROUPS.values())} pads vs all F-side courtyards")
check("I/O pads accept standard headers",
      L.IO_PAD_PITCH == 2.54 and L.IO_PAD_DRILL >= 1.0
      and L.IO_PAD_SIZE[0] >= 2.2 and L.IO_PAD_SIZE[1] >= 2.0,
      f"{L.IO_PAD_PITCH:.2f} mm pitch, {PAD_W:.1f}×{PAD_H:.1f} pad / "
      f"Ø{L.IO_PAD_DRILL:.1f} finished hole")

bad = 0
for hx, hy in L.HOLES:
    kr = L.GROMMET_KEEPOUT_D / 2
    for name, spec in L.PARTS.items():          # grommets exist on BOTH sides
        if rect_circle_overlap(rect(spec["pos"], spec["courtyard"]), hx, hy, kr):
            check(f"grommet@({hx:+.2f},{hy:+.2f}) vs {name}", False,
                  "courtyard inside grommet keepout")
            bad += 1
    for group, pads in L.PAD_GROUPS.items():
        for x, y, label in pads:
            if rect_circle_overlap(rect((x, y), (PAD_W, PAD_H)), hx, hy, kr):
                check(f"grommet@({hx:+.2f},{hy:+.2f}) vs pad {label}", False,
                      "pad inside grommet keepout")
                bad += 1
check("grommet keepouts clear", bad == 0,
      f"4 x Phi{L.GROMMET_KEEPOUT_D} keepouts vs every part and pad, both sides")

# Everything inside the outline, including the rounded corners.
def inside_outline(r):
    w2, h2, cr = L.BOARD_W / 2, L.BOARD_H / 2, L.CORNER_R
    for cx_, cy_ in ((r[0], r[1]), (r[0], r[3]), (r[2], r[1]), (r[2], r[3])):
        if abs(cx_) > w2 or abs(cy_) > h2:
            return False
        if abs(cx_) > w2 - cr and abs(cy_) > h2 - cr:
            ax, ay = w2 - cr, h2 - cr
            if math.hypot(abs(cx_) - ax, abs(cy_) - ay) > cr:
                return False
    return True


bad = 0
for name, spec in L.PARTS.items():
    if not inside_outline(rect(spec["pos"], spec["courtyard"])):
        check(f"{name} inside outline", False, "courtyard leaves the board")
        bad += 1
for group, pads in L.PAD_GROUPS.items():
    for x, y, label in pads:
        if not inside_outline(rect((x, y), (PAD_W, PAD_H))):
            check(f"pad {label} inside outline", False, "pad leaves the board")
            bad += 1
check("everything inside the rounded outline", bad == 0,
      "corner-radius aware containment for all parts and pads")

# ----------------------------------------------------------------- system fit
print("\n=== system integration ===")
usb = L.PARTS["J1_usb_service_SH4"]
check("USB service harness faces the open tail",
      usb["side"] == "B" and usb["pos"][1] < -12,
      "bottom side, -Y edge: removable USB-C pigtail exits through the tail")
esc = L.PARTS["J2_esc_SH8"]
check("ESC socket matches 4-in-1 harness", esc["side"] == "B" and "8-pin" in esc["pkg"],
      "SH1.0 8-pin on inward face for a short back-to-back harness")

print()
if fails:
    print(f"{len(fails)} FAILED: {', '.join(sorted(set(fails)))}")
    raise SystemExit(1)
print("all checks passed")
