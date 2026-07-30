"""VYPER-5 bottom plate -- the structural spine. Print one.

SHAPE
-----
An X, not a slab: a central square carrying the stack, plus two crossed
bars that back up the arms out to R = 54. Material only exists where a
load path exists. A solid plate of the same reach would add ~6 g and a lot
of frontal area for nothing -- on a 5" racer that is real top speed.

Printed flat, bottom face on the bed. Plate loads are in-plane, so flat
printing is right here for the same reason it would be wrong for an arm.

ARM INTERFACE
-------------
Four shallow (0.8 mm) grooves along the arm axes. These are a LOCATING
feature, not a structural one -- they exist so the arms land straight
without a jig. Going deeper would just thin the plate exactly where the
arm bolts pull through it.

Each arm is clamped by two M3:
  inner  R = 21.57  shared with the 30.5 x 30.5 stack pattern
  outer  R = 38.0   also carries the top-plate standoff

That 16.4 mm couple carries ~83 N per bolt at full static thrust and ~250 N
under a 10 g arm-tip impact. Bearing in the printed bore works out around
5 MPa, which is why the build uses M3 washers under every head.

NO COUNTERBORES. A 2 mm counterbore would put the whole arm couple into
2 mm of remaining plastic. Use button-head M3 and accept 1.8 mm of head
proud of the belly, the way every carbon frame does.

Battery is TOP mounted -- an X plate has no material out at +/-30 mm to
put strap slots through, and top mounting is what you want on a racer
anyway for prop clearance and CG.
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
    sk = RectangleRounded(P.BP_SQ, P.BP_SQ, P.BP_SQ_R)
    bar = RectangleRounded(P.BP_BAR_L, P.BP_BAR_W, P.BP_BAR_R)
    for ang in (45.0, 135.0):
        sk += Rot(0, 0, ang) * bar

    plate = extrude(sk, amount=P.BP_T)

    # Arm locating grooves, cut into the top face.
    g_len = P.BP_GROOVE_R1 - P.BP_GROOVE_R0
    g_mid = (P.BP_GROOVE_R1 + P.BP_GROOVE_R0) / 2.0
    for ang in P.ARM_ANGLES:
        groove = Box(g_len, P.BP_GROOVE_W, P.BP_GROOVE_D * 2)
        plate -= Rot(0, 0, ang) * Pos(g_mid, 0, P.BP_T) * groove

    # Arm / stack / standoff bolts.
    for ang in P.ARM_ANGLES:
        for r in (P.R_STACK, P.R_ARM_OUT):
            plate -= Rot(0, 0, ang) * Pos(r, 0, P.BP_T / 2) * Cylinder(
                P.M3_CLR / 2, P.BP_T + 4
            )

    # Accessory pairs: +X camera cage, -X antenna mount. Same pattern both
    # ends so either part can be moved or reprinted mirrored.
    for sx in (1, -1):
        for sy in (1, -1):
            plate -= Pos(sx * P.ACC_X, sy * P.ACC_Y, P.BP_T / 2) * Cylinder(
                P.M3_CLR / 2, P.BP_T + 4
            )

    # Strain relief for the XT60 lead.
    plate -= Pos(P.LEAD_SLOT_X, 0, P.BP_T / 2) * Box(
        P.LEAD_SLOT_T, P.LEAD_SLOT_W, P.BP_T + 4
    )

    return plate.clean()


if __name__ == "__main__":
    p = gen_step()
    print("bottom plate volume mm^3:", round(p.volume, 1))
    print("bottom plate bbox   mm  :", [round(v, 2) for v in p.bounding_box().size])
