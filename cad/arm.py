"""VYPER-5 arm -- tapered cantilever, one part, print four.

THE WHOLE DESIGN IS DRIVEN BY PRINT ORIENTATION
-----------------------------------------------
An FDM part is strong along the extrusion and weak between layers. A drone
arm is a cantilever: motor thrust at the tip, clamped at the root, so the
peak stress is bending -- tension on one face, compression on the other,
both running ALONG the arm.

So the arm is laid out to be printed MOTOR-PAD FACE DOWN ON THE BED:

  * The top face (the motor mounting face) is flat over the entire length.
    That face is the bed face: dead flat, best surface on the part, and it
    is exactly the face a motor needs to sit on without rocking.
  * The arm only ever gets THINNER going up from the bed, because all the
    taper is on the underside. Cross-section shrinks monotonically with
    height, so there is not a single overhang anywhere. Zero supports.
  * Bed contact is the whole 111 x up-to-26 mm plan area. It will not lift.
  * Peak bending fibres are continuous perimeter extrusions running the
    full length of the arm. Layer adhesion only ever sees transverse shear,
    which works out around 0.6 MPa -- two orders of magnitude under what
    the interlayer bond can take.

Print it any other way and it snaps at the root.

TAPER
-----
Depth follows the bending moment instead of being a straight ramp, so the
stress stays roughly flat along the span (~5-8 MPa at full static thrust)
instead of spiking just inboard of the motor pad, which is where a linear
taper always fails. Root keeps full 14 mm depth past BOTH bolts.

MOTOR PAD
---------
4.0 mm thick, which sets how deep an M3 motor screw reaches into the bell.
Use M3x8. Longer screws hit the windings and kill the motor -- this is the
single most common way people destroy a brand new set of motors.
"""

from build123d import (
    Axis,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    extrude,
    make_face,
)

import vy_params as P


def _plan_face():
    """Closed plan outline: +Y half from params, mirrored to -Y."""
    half = list(P.ARM_OUTLINE)
    pts = half + [(x, -y) for x, y in reversed(half)]
    return make_face(Polyline(*pts, close=True))


def _taper_cutter():
    """Everything below the underside profile, extruded wide in Y."""
    prof = [(x, P.ARM_H - h) for x, h in P.ARM_TAPER]
    x0 = prof[0][0]
    pts = [(x0, -2.0)] + prof + [(P.ARM_L + 9.0, prof[-1][1]), (P.ARM_L + 9.0, -2.0)]
    sk = Plane.XZ * make_face(Polyline(*pts, close=True))
    return extrude(sk, amount=P.ARM_W_TIP + P.MOTOR_PATTERN, both=True)


def gen_step():
    arm = extrude(_plan_face(), amount=P.ARM_H)
    arm -= _taper_cutter()

    # Root bolts -- both sit in the full-depth section, ahead of the taper.
    for x in (P.ARM_BOLT_1, P.ARM_BOLT_2):
        arm -= Pos(x, 0, P.ARM_H / 2) * Cylinder(P.M3_CLR / 2, P.ARM_H + 4)

    # Motor: 16x16 M3 square, aligned to the arm axis.
    h = P.MOTOR_PATTERN / 2
    for dx in (-h, h):
        for dy in (-h, h):
            arm -= Pos(P.MOTOR_X + dx, dy, P.ARM_H / 2) * Cylinder(
                P.M3_CLR / 2, P.ARM_H + 4
            )
    # Bell boss relief; also lets grit and water fall out.
    arm -= Pos(P.MOTOR_X, 0, P.ARM_H / 2) * Cylinder(P.MOTOR_BORE / 2, P.ARM_H + 4)

    # Single tie point for the motor phase wires. Placed at mid-span where
    # it costs ~30% of local section modulus and the margin can afford it.
    arm -= Pos(P.ARM_ZIP_X, 0, P.ARM_H / 2) * Cylinder(P.ARM_ZIP_D / 2, P.ARM_H + 4)

    return arm.clean()


if __name__ == "__main__":
    a = gen_step()
    bb = a.bounding_box()
    print("arm volume  mm^3:", round(a.volume, 1))
    print("arm bbox    mm  :", [round(v, 2) for v in bb.size])
