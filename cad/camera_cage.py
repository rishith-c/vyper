"""VYPER-5 camera cage -- 19 mm micro cam. Print one.

Bolts to the front accessory pair on the bottom plate (frame X = +19,
Y = +/-9). Local origin is the underside of its own base, so it lands at
frame Z = 4.0, on top of the bottom plate.

TILT
----
Deliberately not a fixed angle. Micro cameras pivot on a single M2 screw
per side and hold their angle by clamping friction against the cage walls
-- that is how every micro cam mount works. So this has ONE hole pair and
you set the tilt when you tighten the screws. For a 6S 5" racer, 30-40
degrees is the usable range; below ~25 you cannot see where you are going
at speed.

WHY THE PIVOT IS WHERE IT IS
----------------------------
On a top-mounted battery the pack nose is the thing that ends up in the
top of your video, not the frame. A 6S 1050 pack is ~85 mm long, so its
nose sits at frame X = +42.5, Z = +41. The pivot is pushed as far forward
and as high as the top plate allows -- frame (26, 0, 22) -- which puts the
lens at about (41, 22). The pack nose is then 85 degrees above the lens,
and a micro cam at 30 degrees tilt with a ~100 degree vertical FOV tops
out at 80 degrees. The battery stays out of frame with 5 degrees to spare.

Height is capped by the top plate: a 19 mm camera tilted 30 degrees swings
its rear-top corner to frame Z = 35.4, and the top plate underside is at
Z = 38.

WALLS
-----
19.5 mm inner gap for a 19.0 mm camera. Two 3 mm walls standing 27 mm tall
would be a hinge on their own, so a rear web ties them together over the
full height. Without it the walls splay when you tighten the M2s and the
camera will not hold angle.

PRINT BASE DOWN, no supports. The M2 holes are horizontal and will bridge
with a little droop -- run a 2 mm drill through them by hand before
assembly. Everything else prints clean.

THIS IS THE SACRIFICIAL PART. It hangs 12 mm off the front of the bottom
plate and it is meant to break before the plate does. It is 7 g of
filament. Print two.
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

WALL_Y = (P.CAM_WIDTH + P.CAM_WALL) / 2.0     # wall centreline
WALL_LEN = P.CAM_WALL_X1 - P.CAM_WALL_X0
WALL_MID = (P.CAM_WALL_X1 + P.CAM_WALL_X0) / 2.0


def gen_step():
    cage = extrude(
        make_face(Polyline(*P.ACC_BASE, close=True)), amount=P.CAM_BASE_T
    )

    # Side walls.
    for sy in (1, -1):
        cage += Pos(WALL_MID, sy * WALL_Y, P.CAM_WALL_H / 2) * Box(
            WALL_LEN, P.CAM_WALL, P.CAM_WALL_H
        )

    # Rear web -- the part that stops the walls splaying.
    web_x = P.CAM_WALL_X0 + P.CAM_WEB_T / 2
    cage += Pos(web_x, 0, (P.CAM_BASE_T + P.CAM_WALL_H) / 2) * Box(
        P.CAM_WEB_T, P.CAM_WIDTH, P.CAM_WALL_H - P.CAM_BASE_T
    )

    # Rake the top front corner off the walls: nothing structural up there
    # and it keeps the lens clear.
    rake = make_face(
        Polyline(
            (P.CAM_WALL_X1 + 2, P.CAM_RAKE_Z),
            (P.CAM_WALL_X1 + 2, P.CAM_WALL_H + 4),
            (P.CAM_RAKE_BACK, P.CAM_WALL_H + 4),
            close=True,
        )
    )
    cage -= extrude(Plane.XZ * rake, amount=40.0, both=True)

    # M2 pivot / clamp screws.
    cage -= (
        Pos(P.CAM_PIVOT_X, 0, P.CAM_PIVOT_Z)
        * Rot(90, 0, 0)
        * Cylinder(P.M2_CLR / 2, 60.0)
    )

    # Mounting bolts into the bottom plate.
    for sy in (1, -1):
        cage -= Pos(0, sy * P.ACC_Y, P.CAM_BASE_T / 2) * Cylinder(
            P.M3_CLR / 2, P.CAM_BASE_T + 4
        )

    return cage.clean()


if __name__ == "__main__":
    c = gen_step()
    print("camera cage volume mm^3:", round(c.volume, 1))
    print("camera cage bbox   mm  :", [round(v, 2) for v in c.bounding_box().size])
