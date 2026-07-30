"""VYPER-5 VTX antenna mount -- rear blade. Print one.

Bolts to the rear accessory pair on the bottom plate (frame X = -19,
Y = +/-9), same pattern as the camera cage.

WHY IT LEANS
------------
The antenna has to end up somewhere the props are not. The blade rakes
30 degrees aft and puts the antenna bore at frame (-46, 0, 50). Nearest
rear prop centre is (-77.8, 77.8); that is 84 mm away against a 63.5 mm
blade radius, so the antenna sits ~20 mm outside the disc even though it
is above the prop plane. A vertical post at the plate edge would not
clear.

The 30 degree rake is also the print constraint: the down-facing side of
the blade never exceeds ~34 degrees from vertical, so it prints base-down
with no supports and no droop.

STRENGTH: deliberately none to speak of. The blade sees ~0.5 MPa from its
own antenna under a 20 g load. It is designed to snap before it levers the
bottom plate. 6 g of filament versus a $12 VTX -- the antenna and the
frame both survive by letting this part be the fuse.
"""

from build123d import (
    Box,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    Rot,
    extrude,
    make_face,
)

import vy_params as P


def gen_step():
    # Same wedge base as the camera cage, mirrored to point aft.
    base = make_face(Polyline(*[(-x, y) for x, y in P.ACC_BASE], close=True))
    mount = extrude(base, amount=P.ANT_BASE_T)

    # Raked blade, extruded across Y.
    blade = make_face(Polyline(*P.ANT_BLADE, close=True))
    mount += extrude(Plane.XZ * blade, amount=P.ANT_BLADE_T / 2, both=True)

    # Head block, aligned to the blade axis. Rotating about +Y takes +Z
    # toward +X, so a negative angle rakes it aft with the blade.
    hx, hz = P.ANT_HEAD_AT
    head_at = Pos(hx, 0, hz) * Rot(0, -P.ANT_TILT, 0)
    mount += head_at * Box(P.ANT_HEAD_D, P.ANT_HEAD_W, P.ANT_HEAD_L)

    # Antenna bore, on the same axis.
    mount -= head_at * Cylinder(P.ANT_BORE / 2, P.ANT_HEAD_L + 30)

    # Cross hole so the antenna can be zip-tied instead of trusting friction.
    mount -= head_at * Rot(90, 0, 0) * Cylinder(1.75, P.ANT_HEAD_W + 8)

    # Mounting bolts into the bottom plate.
    for sy in (1, -1):
        mount -= Pos(0, sy * P.ACC_Y, P.ANT_BASE_T / 2) * Cylinder(
            P.M3_CLR / 2, P.ANT_BASE_T + 4
        )

    return mount.clean()


if __name__ == "__main__":
    m = gen_step()
    bb = m.bounding_box()
    print("antenna mount volume mm^3:", round(m.volume, 1))
    print("antenna mount bbox   mm  :", [round(v, 2) for v in bb.size])
    print("bore tip frame XYZ      :", round(P.ACC_X * -1 + bb.min.X, 1), 0,
          round(P.BP_T + bb.max.Z, 1))
