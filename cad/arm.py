"""VYPER-5X arm -- two crossed blades, half-lapped at the centre. Print two.

THE LAYOUT
----------
Two straight arms crossing in an X, flat, with the streamlined body threaded
through the crossing. Each arm runs corner to corner and carries a motor at
each end. This is the minimum-frontal-area layout: a 9 mm blade edge-on
presents almost nothing, so essentially all the drag left is the body (which
is faired) and the motors.

The big swept wing panels this replaces were the opposite trade -- they made
lift, but they made frontal area and rotor download too.

HALF LAP
--------
The two arms occupy the same 9 x 18 mm of space at the centre, so each carries
a 9 mm notch there: arm A is notched from the TOP, arm B from the BOTTOM, and
they interlock into a flat X exactly like crossed sticks. Both arms are
otherwise the same part, and both notches are cut with the same geometry, so
there is one model and a flag.

SECTION
-------
9 mm wide by 18 mm deep. Deep in the direction the motor pushes (bending),
thin in the direction it flies. Those are the same choice here, which is why
this layout is used for speed.

  root bending: 19 N at 112 mm = 2.13 N.m
  Z = 9 x 18^2 / 6 = 486 mm^3  ->  4.4 MPa against ~45 MPa PETG yield

PRINTING
--------
Flat top (the motor pad plane) goes on the bed; the belly rounds away below,
so the section only shrinks going up and there is no overhang. Peak bending
fibres are continuous perimeters running the full 254 mm.

The arm is 254 mm long, which does NOT fit a 225 mm bed square -- print it
DIAGONALLY. A 254 x 30 mm part rotated 45 degrees needs (254+30)/sqrt(2) =
201 mm in both axes, so it fits with 24 mm to spare.
"""

import math

from build123d import (
    Box,
    Cylinder,
    Plane,
    Pos,
    RectangleRounded,
    Rot,
    extrude,
    loft,
    offset,
)

import components as C
import vy_params as P

HALF_SPAN = math.hypot(P.MOTOR_XY[0][0], P.MOTOR_XY[0][1])
ARM_ANGLE = math.degrees(math.atan2(P.MOTOR_XY[0][1], P.MOTOR_XY[0][0]))
ARM_LEN = 2 * (HALF_SPAN + P.ARM_TIP_OVER)


def _tapered(sketch_fn):
    """Loft one plan shape downward with a growing inset.

    Blade and pads are lofted SEPARATELY and then unioned. Offsetting their
    union fails: the pad discs meet the blade capsule tangentially, and
    offset_2d throws on that. Two simple shapes each offset cleanly.
    """
    sections = []
    for dz, ins in P.ARM_BELLY:
        sk = sketch_fn()
        sections.append(Plane.XY.offset(-dz) * (offset(sk, -ins) if ins > 0 else sk))
    return loft(sections)


def gen(notch="top"):
    part = _tapered(
        lambda: RectangleRounded(ARM_LEN, P.ARM_W, P.ARM_W / 2 - 0.01)
    )
    for sx in (-1, 1):
        part += Pos(sx * HALF_SPAN, 0, 0) * _tapered(
            lambda: RectangleRounded(
                P.ARM_PAD_D, P.ARM_PAD_D, P.ARM_PAD_D / 2 - 0.01
            )
        )
    part = part.clean()

    # Motor pads at both ends: 16 x 16 M3 through a 4 mm pad, belly pocketed
    # out so an M3x8 reaches exactly 4 mm into the bell.
    for sx in (-1, 1):
        mx = sx * HALF_SPAN
        part -= Pos(mx, 0, (-P.MOTOR_PAD_T - P.ARM_H) / 2) * Cylinder(
            P.MOTOR_POCKET_D / 2, P.ARM_H - P.MOTOR_PAD_T + 2
        )
        h = C.MOTOR_PATTERN / 2
        for ax in (-h, h):
            for ay in (-h, h):
                part -= Pos(mx + ax, ay, -P.MOTOR_PAD_T / 2) * Cylinder(
                    P.M3_CLR / 2, P.MOTOR_PAD_T + 6
                )
        part -= Pos(mx, 0, -P.MOTOR_PAD_T / 2) * Cylinder(4.5, P.MOTOR_PAD_T + 6)

    # Half lap. Cut square across the OTHER arm's width, so the notch is
    # wide enough for it to pass at the crossing angle.
    # Width of the OTHER blade measured along this one's axis, plus fit
    # clearance. The blades cross at 2*ARM_ANGLE, so the projected width is
    # W/sin(cross), not W.
    cross = math.radians(2 * ARM_ANGLE)
    lap_w = P.ARM_W / math.sin(cross) + P.ARM_LAP_FIT
    # The blade spans Z = 0 (top, the motor pad plane) down to -ARM_H. One
    # arm loses its top half, the other its bottom half, so they interlock
    # flush. Half the depth each, plus a shim of clearance.
    half = P.ARM_H / 2
    z_c = -half / 2 if notch == "top" else -P.ARM_H + half / 2
    part -= (
        Pos(0, 0, z_c)
        * Rot(0, 0, -2 * ARM_ANGLE)
        * Box(lap_w, 400, half + P.ARM_LAP_FIT / 2)
    )

    # Body mounting: two M3 either side of the crossing, up into the shell.
    for sx in (-1, 1):
        part -= Pos(sx * P.ARM_BOLT_R, 0, -P.ARM_H / 2) * Cylinder(
            P.M3_CLR / 2, P.ARM_H + 6
        )

    return part.clean()


def gen_step():
    return gen("top")


if __name__ == "__main__":
    for n in ("top", "bottom"):
        a = gen(n)
        bb = a.bounding_box()
        print(f"arm_{n:6s} {a.volume:8.0f} mm^3  "
              f"{a.volume * P.ARM_FILL * P.PETG_RHO:5.1f} g  "
              f"bbox {[round(v, 1) for v in bb.size]}  "
              f"solids {len(a.solids())}")
    print(f"arm length {ARM_LEN:.0f} mm, cross angle {2 * ARM_ANGLE:.1f} deg")
    print(f"diagonal bed need {(ARM_LEN + P.ARM_PAD_D) / 2 ** 0.5:.0f} mm")
