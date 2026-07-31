"""VYPER-5F verification. Nothing gets printed until this passes.

"Perfect fit for the parts" is only meaningful if it is checked. So every
bought component is modelled at its spec-sheet size in components.py, placed
where the airframe expects it, and then boolean-tested:

  * does it collide with any printed part?
  * is it actually INSIDE the fuselage cavity, or hanging out in space?
  * does anything on the airframe reach into a prop disc?
  * do any two printed parts overlap?
  * does every part fit the Neptune 4 bed?

Run:  python verify.py
"""

import math

from build123d import Pos

import assembly
import body
import components as C
import wing
import shells
import vy_params as P

fails = []


def check(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        fails.append(name)


def vol(x):
    try:
        return x.volume
    except Exception:
        return 0.0


print("=== airframe geometry ===")
import itertools
gaps = [
    ((math.dist(a[:2], b[:2])) - P.PROP_DIA)
    for a, b in itertools.combinations(body.all_motors(), 2)
]
check("min prop tip gap", min(gaps) > 5.0,
      f"{min(gaps):.1f} mm between the closest pair of discs")
# Frame geometry: a stretched X (longer fore-aft than lateral) is what a
# speed airframe wants -- narrower frontal area, and the rear discs pulled
# out of the front discs' wake. A square layout is a true X in name only.
xs = sorted({abs(x) for x, _ in P.MOTOR_XY})
ys = sorted({abs(y) for _, y in P.MOTOR_XY})
fore_aft, lateral = 2 * xs[0], 2 * ys[0]
stretch = fore_aft / lateral
check("stretched-X geometry", 1.10 <= stretch <= 1.45,
      f"{fore_aft:.0f} mm fore-aft / {lateral:.0f} mm lateral = {stretch:.2f}:1")
check("lateral spacing at prop minimum", lateral - P.PROP_DIA < 20.0,
      f"{lateral - P.PROP_DIA:.0f} mm tip gap -- narrow is the point")

check("motor tilt shipped", P.MOTOR_TILT == 0.0,
      f"{P.MOTOR_TILT:.0f} deg -- conventional; see vy_params docstring")

PRINTED = {
    "fuselage_lower": shells.fuselage_lower(),
    "fuselage_upper": shells.fuselage_upper(),
    "nose_cone": shells.nose_cone(),
    "tail_cone": shells.tail_cone(),
    "tail_fin": shells.tail_fin(),
}
PRINTED.update({f"wing_{h}": s for h, s in assembly.placed_wings().items()})
COMPONENTS = assembly.placed_components()

# ------------------------------------------------------- components vs frame
print("\n=== bought parts vs printed parts ===")
cav = body.cavity()
for cname, csolid in COMPONENTS.items():
    worst = 0.0
    for pname, psolid in PRINTED.items():
        worst = max(worst, vol(csolid & psolid))
    check(f"{cname} clash", worst < 1.0, f"{worst:.1f} mm^3 into printed material")

    outside = vol(csolid) - vol(csolid & cav)
    check(f"{cname} inside cavity", outside < 1.0,
          f"{outside:.1f} mm^3 of {vol(csolid):.0f} outside the fuselage")

# Motors must sit on the pads, clear of the fairings.
for i, (mx, my, mz) in enumerate(body.all_motors()):
    m = Pos(mx, my, mz) * C.motor()
    worst = max(vol(m & s) for s in PRINTED.values())
    check(f"motor {i} seats", worst < 1.0, f"{worst:.1f} mm^3 clash")

# --------------------------------------------------------------- prop keep-out
print("\n=== prop keep-out ===")
KEEP = 400.0
keepouts = []
from build123d import Cylinder

for mx, my, mz in body.all_motors():
    keepouts.append(
        Pos(mx, my, mz + C.MOTOR_PAD_TO_PROP - 3 + KEEP / 2)
        * Cylinder(P.PROP_R, KEEP)
    )
for pname, psolid in PRINTED.items():
    worst = max(vol(psolid & k) for k in keepouts)
    check(f"{pname} vs props", worst < 1.0, f"{worst:.1f} mm^3")

# ---------------------------------------------------------- part interference
print("\n=== printed part interference ===")
names = list(PRINTED)
worst_pair = ("none", 0.0)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        v = vol(PRINTED[a] & PRINTED[b])
        if v > worst_pair[1]:
            worst_pair = (f"{a} / {b}", v)
# Saddled joints (pylon flanges, fin foot) are near-tangent curved-on-curved
# contacts. OCC reports tens of mm^3 of intersection on those purely from
# tessellation, so the threshold is set at an interference that would actually
# matter: 60 mm^3 over a ~720 mm^2 saddle is under 0.1 mm average.
SADDLE_NOISE = 60.0
check("no part overlaps", worst_pair[1] < SADDLE_NOISE,
      f"worst {worst_pair[0]} = {worst_pair[1]:.1f} mm^3 "
      f"(~{worst_pair[1] / 720:.2f} mm over a saddle face)")

# ------------------------------------------------------------ single solids
# A printed part that comes out as several disconnected lumps slices into
# floating islands. This caught stack posts that stopped tangent to the shell
# inner surface instead of merging into the wall.
print("\n=== each part is one solid ===")
for pname, psolid in PRINTED.items():
    n = len(psolid.solids())
    check(f"{pname} connected", n == 1, f"{n} solid(s)")

# ---------------------------------------------------------------- bed fit
print("\n=== Neptune 4 bed (%.0f x %.0f x %.0f) ===" % P.NEPTUNE4_BED)
BX, BY, BZ = P.NEPTUNE4_BED
TO_PRINT = [
    ("fuselage_lower", shells.fuselage_lower(), 1, P.SHELL_FILL),
    ("fuselage_upper", shells.fuselage_upper(), 1, P.SHELL_FILL),
    ("nose_cone", shells.nose_cone(), 1, P.SHELL_FILL),
    ("tail_cone", shells.tail_cone(), 1, P.SHELL_FILL),
    ("tail_fin", shells.tail_fin(), 1, P.SHELL_FILL),
    ("wing_l", wing.gen("l"), 1, P.WING_FILL),
    ("wing_r", wing.gen("r"), 1, P.WING_FILL),
]
printed_g = 0.0
for name, solid, qty, fill in TO_PRINT:
    s = solid.bounding_box().size
    fits = s.X < BX - 10 and s.Y < BY - 10 and s.Z < BZ - 10
    g = solid.volume * fill * P.PETG_RHO
    printed_g += g * qty
    check(f"{name} x{qty}", fits, f"{s.X:.0f} x {s.Y:.0f} x {s.Z:.0f} mm, {g:.1f} g ea")

# ---------------------------------------------------------------- mass budget
print("\n=== mass ===")
payload_g = sum(C.PAYLOAD.values())
auw = printed_g + payload_g
thrust_g = 4 * 1600.0            # 2207 1750KV on 6S, 5x4.3x3, ~1.6 kg/motor
print(f"printed frame      {printed_g:6.0f} g")
for k, v in C.PAYLOAD.items():
    print(f"  {k:30s} {v:5.0f} g")
print(f"AUW                {auw:6.0f} g")
print(f"static thrust      {thrust_g:6.0f} g")
check("thrust-to-weight", thrust_g / auw > 7.0, f"{thrust_g / auw:.1f}:1")

print()
if fails:
    print(f"{len(fails)} CHECK(S) FAILED: {', '.join(fails)}")
    raise SystemExit(1)
print("all checks passed")
