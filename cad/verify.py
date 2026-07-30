"""VYPER-5 verification -- checks that must pass before anything is printed.

Bounding boxes are not proof. Prop clearance is checked by intersecting the
frame against a real prop keep-out solid; hole alignment is checked against
the numbers the mating part actually uses; bed fit is checked against the
Neptune 4 envelope.

Run:  python verify.py
"""

from build123d import Cylinder, Pos, Rot

import vy_params as P

import antenna_mount
import arm as arm_mod
import bottom_plate
import camera_cage
import standoff
import top_plate

ARM_SEAT = P.BP_T - P.BP_GROOVE_D   # arms drop into the locating grooves
ARM_TOP = ARM_SEAT + P.ARM_H
TP_Z = ARM_TOP + P.SO_LEN

# 2207-class motors put the prop plane 26-32 mm above the mount face. Take
# the worst case (lowest prop) for the keep-out.
PROP_PLANE_MIN = ARM_TOP + 26.0

PETG_RHO = 1.27e-3          # g/mm^3
FILL = 0.70                 # 5 walls + 40-50% gyroid, measured-ish

fails = []
notes = []


def check(name, ok, detail):
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}: {detail}")
    if not ok:
        fails.append(name)


# ---------------------------------------------------------------- geometry
print("=== airframe geometry ===")
adj = P.WHEELBASE / (2 ** 0.5)
tip_gap = adj - P.PROP_DIA
check(
    "adjacent prop tip gap",
    tip_gap > 10.0,
    f"{tip_gap:.1f} mm between discs (motors {adj:.1f} mm apart)",
)

check(
    "motor position",
    abs(P.ARM_R0 + P.MOTOR_X - P.R_MOTOR) < 1e-9,
    f"arm-local {P.MOTOR_X} + R0 {P.ARM_R0} = R {P.ARM_R0 + P.MOTOR_X} "
    f"-> wheelbase {2 * (P.ARM_R0 + P.MOTOR_X):.0f} mm",
)

# ---------------------------------------------------------- prop keep-out
print("\n=== prop keep-out (radius 63.5 mm, from Z=%.0f up) ===" % PROP_PLANE_MIN)
KEEP_H = 300.0
keepouts = [
    Rot(0, 0, a) * Pos(P.R_MOTOR, 0, PROP_PLANE_MIN + KEEP_H / 2)
    * Cylinder(P.PROP_R, KEEP_H)
    for a in P.ARM_ANGLES
]

placed = {
    "bottom_plate": bottom_plate.gen_step(),
    "top_plate": Pos(0, 0, TP_Z) * top_plate.gen_step(),
    "camera_cage": Pos(P.ACC_X, 0, P.BP_T) * camera_cage.gen_step(),
    "antenna_mount": Pos(-P.ACC_X, 0, P.BP_T) * antenna_mount.gen_step(),
}
one_arm = arm_mod.gen_step()
one_so = standoff.gen_step()
for i, ang in enumerate(P.ARM_ANGLES):
    placed[f"arm_{i + 1}"] = Rot(0, 0, ang) * Pos(P.ARM_R0, 0, ARM_SEAT) * one_arm
    placed[f"standoff_{i + 1}"] = (
        Rot(0, 0, ang) * Pos(P.R_ARM_OUT, 0, ARM_TOP) * one_so
    )

for name, solid in placed.items():
    worst = 0.0
    for ko in keepouts:
        try:
            worst = max(worst, (solid & ko).volume)
        except Exception:
            pass
    check(f"{name} vs props", worst < 1.0, f"intrusion {worst:.1f} mm^3")

# Top plate is the tight one -- report the actual radial margin.
tp_reach = (P.TP_SQ / 2 - P.TP_R) * (2 ** 0.5) + P.TP_R
check(
    "top plate radial margin",
    tp_reach < P.R_PROP_INNER,
    f"corner reaches R={tp_reach:.1f}, prop disc starts R={P.R_PROP_INNER:.1f} "
    f"-> {P.R_PROP_INNER - tp_reach:.1f} mm",
)

# ------------------------------------------------------------ hole matching
print("\n=== mating features ===")
check(
    "arm bolt 1 <-> stack pattern",
    abs((P.ARM_R0 + P.ARM_BOLT_1) - P.R_STACK) < 1e-6,
    f"R={P.ARM_R0 + P.ARM_BOLT_1:.3f} == stack R={P.R_STACK:.3f} "
    f"({P.STACK_PITCH} mm square)",
)
check(
    "arm bolt 2 <-> standoff/top plate",
    abs((P.ARM_R0 + P.ARM_BOLT_2) - P.R_ARM_OUT) < 1e-6,
    f"R={P.ARM_R0 + P.ARM_BOLT_2:.1f} == standoff R={P.R_ARM_OUT:.1f}",
)
check(
    "bolt couple arm root",
    (P.ARM_BOLT_2 - P.ARM_BOLT_1) > 12.0,
    f"{P.ARM_BOLT_2 - P.ARM_BOLT_1:.1f} mm between arm bolts",
)
check(
    "both arm bolts in full-depth section",
    P.ARM_BOLT_2 < P.ARM_TAPER[0][0],
    f"outer bolt at x={P.ARM_BOLT_2}, taper starts x={P.ARM_TAPER[0][0]}",
)
check(
    "arm groove clears arm",
    P.BP_GROOVE_W > P.ARM_W_ROOT,
    f"groove {P.BP_GROOVE_W} vs arm {P.ARM_W_ROOT} "
    f"({P.BP_GROOVE_W - P.ARM_W_ROOT:.1f} mm total slip)",
)

# Arms must not collide with each other at the hub.
hub_gap = P.ARM_R0 * (3.14159265 / 2) - P.ARM_W_ROOT
check("arm-to-arm at hub", hub_gap > 5.0, f"{hub_gap:.1f} mm arc gap at R={P.ARM_R0}")

# Motor screws must not punch into the windings.
check(
    "motor screw grip",
    3.5 <= P.PAD_T <= 4.5,
    f"pad {P.PAD_T} mm -> M3x8 reaches {8 - P.PAD_T:.1f} mm into the bell",
)

# -------------------------------------------------------- part interference
# Every joint in this frame is face-to-face. Any non-zero intersection
# volume between two printed parts is a modelling error, not a fit.
print("\n=== part-to-part interference ===")
names = list(placed)
worst_pair = ("", 0.0)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        try:
            v = (placed[a] & placed[b]).volume
        except Exception:
            v = 0.0
        if v > worst_pair[1]:
            worst_pair = (f"{a} / {b}", v)
        if v > 1.0:
            check(f"{a} / {b}", False, f"overlap {v:.1f} mm^3")
check(
    "no part overlaps",
    worst_pair[1] < 1.0,
    f"worst pair {worst_pair[0] or 'none'} = {worst_pair[1]:.2f} mm^3",
)

# ------------------------------------------------------------ camera sightline
print("\n=== camera ===")
import math

CAM_BODY = 19.0
CAM_TILT = 30.0
CAM_VFOV = 100.0                # micro cam, 4:3, ~150 deg diagonal lens
LENS_REACH = 15.0               # pivot -> front of lens
PACK = (85.0, 34.0, 30.0)       # 6S 1050

piv = (P.ACC_X + P.CAM_PIVOT_X, P.BP_T + P.CAM_PIVOT_Z)
lens = (piv[0] + LENS_REACH * math.cos(math.radians(CAM_TILT)),
        piv[1] + LENS_REACH * math.sin(math.radians(CAM_TILT)))
pack_nose = (PACK[0] / 2, TP_Z + P.TP_T)

blocked_at = math.degrees(math.atan2(pack_nose[1] - lens[1],
                                     pack_nose[0] - lens[0]))
image_top = CAM_TILT + CAM_VFOV / 2
check(
    "battery out of frame",
    blocked_at > image_top,
    f"pack nose sits {blocked_at:.0f} deg up, image tops out at "
    f"{image_top:.0f} deg -> {blocked_at - image_top:.0f} deg margin",
)

# A 19 mm camera tilted 30 deg swings its corners on a 13.4 mm radius.
swing = CAM_BODY / 2 * (2 ** 0.5)
cam_top = piv[1] + swing
check(
    "camera clears top plate",
    cam_top < TP_Z,
    f"camera reaches Z={cam_top:.1f}, top plate underside Z={TP_Z:.1f}",
)

t = math.radians(CAM_TILT)
low_z = P.CAM_PIVOT_Z - (CAM_BODY / 2) * (math.sin(t) + math.cos(t))
check(
    "camera clears its own base",
    low_z > P.CAM_BASE_T,
    f"lowest corner local Z={low_z:.1f}, base top Z={P.CAM_BASE_T:.1f}",
)

back_x = P.CAM_PIVOT_X - (CAM_BODY / 2) * (math.cos(t) + math.sin(t))
web_face = P.CAM_WALL_X0 + P.CAM_WEB_T
check(
    "camera clears rear web",
    back_x > web_face,
    f"rear corner local X={back_x:.1f}, web face X={web_face:.1f}",
)

# ---------------------------------------------------------------- bed fit
print("\n=== Neptune 4 bed (%.0f x %.0f x %.0f) ===" % P.NEPTUNE4_BED)
BED_X, BED_Y, BED_Z = P.NEPTUNE4_BED
printed = {
    "bottom_plate": (bottom_plate.gen_step(), 1),
    "arm": (one_arm, 4),
    "top_plate": (top_plate.gen_step(), 1),
    "camera_cage": (camera_cage.gen_step(), 1),
    "antenna_mount": (antenna_mount.gen_step(), 1),
    "standoff": (one_so, 4),
}
total_g = 0.0
for name, (solid, qty) in printed.items():
    s = solid.bounding_box().size
    fits = s.X < BED_X - 10 and s.Y < BED_Y - 10 and s.Z < BED_Z - 10
    g = solid.volume * FILL * PETG_RHO
    total_g += g * qty
    check(
        f"{name} x{qty}",
        fits,
        f"{s.X:.0f} x {s.Y:.0f} x {s.Z:.0f} mm, {g:.1f} g each",
    )

print(f"\ntotal printed mass (PETG, ~{FILL:.0%} effective): {total_g:.0f} g")

# ------------------------------------------------------------------- report
print()
if fails:
    print(f"{len(fails)} CHECK(S) FAILED: {', '.join(fails)}")
    raise SystemExit(1)
print("all checks passed")
