"""VYPER-5W wing panel -- two mirror hands, print one each.

Replaces the four separate pylons. Each panel is a broad swept surface
carrying TWO motors at their normal true-X stations, blended into the
fuselage flank. This is the layout in the reference build: the arms are not
struts, they are wing.

WHY IT IS WORTH THE CHANGE
--------------------------
A strut is dead weight in cruise. A panel of the same mass is a lifting
surface: at 30 m/s the two wings carry roughly half the all-up weight, which
unloads the props and is exactly what makes a fast forward-flight airframe
efficient. It is not free -- the props now sweep over a broad plate 26 mm
below them and lose a few percent to rotor download in the hover. Both
numbers are computed in aero.py rather than asserted here.

PRINT ORIENTATION, UNCHANGED IN PRINCIPLE
-----------------------------------------
Flat top at the motor pad plane, every bit of fairing hanging below it, so
the panel prints top-face-down with no overhang anywhere and no supports.
The flat top is simultaneously the bed face and both motor mounting faces.

The belly is rounded by lofting one plan outline downward with a growing
inset, which also guarantees the section only shrinks going up.

Local Z = 0 is the motor pad plane; the panel is placed at frame Z =
MOTOR_PAD_Z. X and Y are frame axes throughout, so the planform reads
directly off the parameters.

ROOT JOINT
----------
The root is a saddle carved from the fuselage solid itself, so it matches the
mould line exactly, with four M3 per side running horizontally into ribs
inside the lower shell. A 192 mm root chord means the joint is enormously
stiffer than the four small flanges it replaces -- the wing is bolted along
almost the whole length of the main body.
"""

import math

from build123d import (
    Box,
    Cylinder,
    RectangleRounded,
    extrude,
    Plane,
    Polygon,
    Pos,
    Rot,
    loft,
    mirror,
    offset,
)

import body
import components as C
import vy_params as P

HANDS = ("l", "r")


def motor_stations(hand="l"):
    """The two motor centres this panel carries, in frame XY."""
    sy = 1.0 if hand == "l" else -1.0
    return [(x, y) for x, y in P.MOTOR_XY if y * sy > 0]


def _plan():
    """Left-wing planform in frame XY."""
    return Polygon(*P.WING_PLAN, align=None)


def planform_area_mm2():
    """One panel, outboard of the fuselage surface. Used by aero.py."""
    return _plan().area


def gen(hand="l"):
    """Right hand is the left mirrored about XZ.

    Built one way and mirrored for the same reason as the old pylons:
    reconstructing the mirrored planform flips the outline's winding, OCC
    builds a negatively oriented face, and every later boolean eats the part
    instead of cutting it.
    """
    if hand == "r":
        return mirror(gen("l"), about=Plane.XZ)

    # ---- fairing: plan lofted downward with a growing inset
    plan = _plan()
    sections = []
    for dz, ins in P.WING_BELLY:
        sk = offset(plan, -ins) if ins > 0 else plan
        sections.append(Plane.XY.offset(-dz) * sk)
    part = loft(sections)

    # ---- lightening bay between the motors
    bay = Pos(P.WING_BAY_X, P.WING_BAY_Y, -P.WING_DEPTH / 2) * RectangleRounded(
        P.WING_BAY_L, P.WING_BAY_W, P.WING_BAY_R
    )
    part -= extrude(bay, amount=P.WING_DEPTH + 8, both=True)

    # ---- hollow from below: skin + perimeter + ribs.
    hollow = None
    for dz, ins in P.WING_BELLY:
        if dz < P.WING_SKIN:
            continue
        sk = offset(plan, -(ins + P.WING_WALL))
        sec = Plane.XY.offset(-dz) * sk
        hollow = sec if hollow is None else hollow
    cav_sections = []
    for dz, ins in P.WING_BELLY:
        z = max(dz, P.WING_SKIN)
        cav_sections.append(
            Plane.XY.offset(-z) * offset(plan, -(ins + P.WING_WALL))
        )
    cavity = loft(cav_sections)
    # Keep the ribs and the bay walls out of the cavity.
    keep = None
    for rx in P.WING_RIBS_X:
        r = Pos(rx, 0, -P.WING_DEPTH / 2) * Rot(0, 0, 0) * Box(
            P.WING_WALL, 400, P.WING_DEPTH + 8
        )
        keep = r if keep is None else keep + r
    bay_wall = Pos(P.WING_BAY_X, P.WING_BAY_Y, -P.WING_DEPTH / 2) * extrude(
        offset(
            RectangleRounded(P.WING_BAY_L, P.WING_BAY_W, P.WING_BAY_R),
            P.WING_WALL,
        ),
        amount=P.WING_DEPTH + 8,
        both=True,
    )
    part -= cavity - keep - bay_wall

    for mx, my in motor_stations("l"):
        # Local boss taking the skin to 4.0 mm under each motor, so an M3x8
        # reaches exactly 4 mm into the bell and no further.
        part += Pos(mx, my, -(P.WING_SKIN + P.MOTOR_PAD_T) / 2) * Cylinder(
            P.WING_PAD_BOSS_D / 2, P.MOTOR_PAD_T + P.WING_SKIN
        )
        h = C.MOTOR_PATTERN / 2
        for sx in (-h, h):
            for sy in (-h, h):
                part -= Pos(mx + sx, my + sy, -P.MOTOR_PAD_T / 2) * Cylinder(
                    P.M3_CLR / 2, P.MOTOR_PAD_T + 6
                )
        part -= Pos(mx, my, -P.MOTOR_PAD_T / 2) * Cylinder(
            4.5, P.MOTOR_PAD_T + 6
        )

    # ---- wire runs: one spanwise bore per motor, into the fuselage
    for mx, my in motor_stations("l"):
        part -= (
            Pos(mx, (my + P.WING_ROOT_Y) / 2, -P.WIRE_TUNNEL_Z)
            * Rot(90, 0, 0)
            * Cylinder(P.WIRE_CH_W / 2, abs(my - P.WING_ROOT_Y) + 40)
        )

    # ---- root bolts, horizontal into the ribs. Cut before the saddle so they
    # pierce clean geometry rather than a freshly trimmed spline surface.
    for bx in P.WING_BOLTS_X:
        part -= (
            Pos(bx, P.WING_ROOT_Y + 10, -P.WING_BOLT_Z)
            * Rot(90, 0, 0)
            * Cylinder(P.M3_CLR / 2, 70)
        )

    # ---- saddle, LAST
    part -= Pos(0, 0, -P.MOTOR_PAD_Z) * body.outer(P.SADDLE_GAP)
    return part.clean()


def gen_step():
    return gen("l")


if __name__ == "__main__":
    for h in HANDS:
        w = gen(h)
        bb = w.bounding_box()
        print(
            f"wing_{h}: {w.volume:8.0f} mm^3  "
            f"{w.volume * P.PYLON_FILL * P.PETG_RHO:5.1f} g  "
            f"bbox {[round(v, 1) for v in bb.size]}  "
            f"solids {len(w.solids())}"
        )
    print("planform per side:", round(planform_area_mm2() / 100, 1), "cm^2")
