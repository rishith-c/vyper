"""VYPER-5 top plate -- battery deck + stack lid. Print one.

Sits on four M3x20 standoffs at R = 38 (the outer arm bolts). 66 x 66 mm
with a 10 mm corner radius reaches R = 42.5 on the diagonals; the prop
discs start at R = 46.5, so there is 4 mm of clearance to the nearest
blade tip. That clearance is the reason this plate is not any bigger.

3.0 mm. The sizing case is the battery: 175 g strapped to the middle,
17 N under a 10 g pull, spanning 53.7 mm between adjacent standoffs. That
is 2.3 MPa in a 3 mm section -- about 20x under PETG yield. Thickness here
is set by stiffness and crash robustness, not strength, which is why the
only material removed is two vents over the stack.

One 20 mm strap through two slots 38 mm apart, which lands on the middle
third of a 6S 1050 pack. Four 4 mm tie points sit outboard of the pack
footprint so the VTX and RX leads can be tied down without being crushed
under the battery.
"""

from build123d import (
    Box,
    Cylinder,
    Pos,
    RectangleRounded,
    Rot,
    extrude,
)

import vy_params as P


def gen_step():
    plate = extrude(RectangleRounded(P.TP_SQ, P.TP_SQ, P.TP_R), amount=P.TP_T)

    # Standoff bolts, on the arm axes at R = 38.
    for ang in P.ARM_ANGLES:
        plate -= Rot(0, 0, ang) * Pos(P.R_ARM_OUT, 0, P.TP_T / 2) * Cylinder(
            P.M3_CLR / 2, P.TP_T + 4
        )

    # Battery strap slots.
    for sx in (1, -1):
        plate -= Pos(sx * P.TP_STRAP_X, 0, P.TP_T / 2) * Box(
            P.TP_STRAP_T, P.TP_STRAP_W, P.TP_T + 4
        )

    # Vents over the stack. Also the only weight worth taking out of this
    # part -- at 3 mm the plate only sees ~2.3 MPa, so it is stiffness and
    # crash-robustness driven, not strength driven.
    for sy in (1, -1):
        plate -= Pos(0, sy * P.TP_VENT_Y, P.TP_T / 2) * Cylinder(
            P.TP_VENT_D / 2, P.TP_T + 4
        )

    # Tie points, outboard of the battery footprint.
    for sx in (1, -1):
        for sy in (1, -1):
            plate -= Pos(sx * P.TP_ZIP_X, sy * P.TP_ZIP_Y, P.TP_T / 2) * Cylinder(
                P.ZIP_D / 2, P.TP_T + 4
            )

    return plate.clean()


if __name__ == "__main__":
    p = gen_step()
    print("top plate volume mm^3:", round(p.volume, 1))
    print("top plate bbox   mm  :", [round(v, 2) for v in p.bounding_box().size])
