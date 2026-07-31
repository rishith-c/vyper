"""Printer calibration coupon -- print this FIRST, before any airframe part.

Every clearance in this design assumes your Neptune 4 holds a particular
dimensional error. Mine assumes roughly -0.1 mm on holes (elephant-foot and
over-extrusion shrink them) and +0.1 mm on outside dimensions. If your machine
is off by 0.3 mm the M3 holes will not pass a bolt and the saddles will not
seat, and you will find that out after nine hours of printing rather than
twenty minutes.

WHAT IS ON IT
-------------
1. M3 hole ladder, 3.0 -> 3.6 mm in 0.1 steps. Find the smallest that passes
   an M3 bolt by hand. That number minus 3.0 is your hole error. If it is not
   3.3, change M3_CLR in vy_params.py and regenerate.
2. M2 hole ladder, 2.0 -> 2.6, same idea for the camera screws.
3. Saddle gauge: a 30 mm arc cut to the actual fuselage radius with the real
   SADDLE_GAP. It should drop onto the printed fuselage without force.
4. Motor bolt pattern: the real 16 x 16 square in a 4.0 mm pad, so you can
   check a motor bolts on and that an M3x8 does NOT protrude past the pad.
5. Wall ladder: 0.8 / 1.2 / 1.6 / 2.0 / 2.4 mm upstands, to confirm your
   slicer actually produces the wall count you asked for at WING_WALL.
6. Bridge test: 6 mm and 10 mm unsupported spans, matching the wire tunnels.
7. Overhang fan: 30 / 45 / 60 / 75 degrees from vertical, to confirm the
   support-free claim holds on YOUR machine.

Print it in the same material, layer height and wall count you will use for
the airframe, or it tells you nothing.
"""

from build123d import (
    Box,
    Cylinder,
    Plane,
    Polygon,
    Pos,
    Rot,
    extrude,
)

import vy_params as P

PLATE_L, PLATE_W, PLATE_T = 120.0, 76.0, 4.0
M3_LADDER = (3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
M2_LADDER = (2.0, 2.1, 2.2, 2.3, 2.4, 2.5)
WALLS = (0.8, 1.2, 1.6, 2.0, 2.4)
OVERHANGS = (30.0, 45.0, 60.0, 75.0)


def gen_step():
    plate = Pos(0, 0, PLATE_T / 2) * Box(PLATE_L, PLATE_W, PLATE_T)

    # 1. M3 hole ladder along the top edge.
    for i, d in enumerate(M3_LADDER):
        x = -PLATE_L / 2 + 12 + i * 13
        plate -= Pos(x, PLATE_W / 2 - 11, PLATE_T / 2) * Cylinder(
            d / 2, PLATE_T + 4
        )

    # 2. M2 hole ladder below it.
    for i, d in enumerate(M2_LADDER):
        x = -PLATE_L / 2 + 12 + i * 13
        plate -= Pos(x, PLATE_W / 2 - 26, PLATE_T / 2) * Cylinder(
            d / 2, PLATE_T + 4
        )

    # 3. Saddle gauge: the real fuselage radius plus the real clearance.
    r = P.FUSE_R_MAX + P.SADDLE_GAP
    gauge = Pos(-PLATE_L / 2 + 30, -PLATE_W / 2 + 20, PLATE_T + 9) * Box(
        34.0, 30.0, 18.0
    )
    plate += gauge
    plate -= (
        Pos(-PLATE_L / 2 + 30, -PLATE_W / 2 + 20, PLATE_T + 2)
        * Rot(0, 90, 0)
        * Cylinder(r, 40)
    )

    # 4. Real motor pattern in a real 4.0 mm pad.
    px, py = PLATE_L / 2 - 22, -PLATE_W / 2 + 20
    plate += Pos(px, py, PLATE_T + P.MOTOR_PAD_T / 2) * Cylinder(
        15.0, P.MOTOR_PAD_T
    )
    h = 16.0 / 2
    for sx in (-h, h):
        for sy in (-h, h):
            plate -= Pos(px + sx, py + sy, PLATE_T) * Cylinder(
                P.M3_CLR / 2, P.MOTOR_PAD_T + 10
            )
    plate -= Pos(px, py, PLATE_T) * Cylinder(4.5, P.MOTOR_PAD_T + 10)

    # 5. Wall ladder.
    for i, t in enumerate(WALLS):
        x = -PLATE_L / 2 + 14 + i * 9
        plate += Pos(x, 4.0, PLATE_T + 7.5) * Box(t, 22.0, 15.0)

    # 6. Bridges at the two bore sizes actually used.
    for i, span in enumerate((6.0, 10.0)):
        x = 8.0 + i * 22
        plate += Pos(x, 6.0, PLATE_T + 9) * Box(18.0, 30.0, 18.0)
        plate -= Pos(x, 6.0, PLATE_T + 6) * Rot(0, 90, 0) * Cylinder(
            span / 2, 24.0
        )

    # 7. Overhang fan, angles measured FROM VERTICAL, which is how the
    # airframe's printability claim is stated.
    for i, ang in enumerate(OVERHANGS):
        x = PLATE_L / 2 - 46 + i * 11
        import math

        run = 16.0 * math.tan(math.radians(ang))
        prof = Polygon(
            (0.0, 0.0), (-run - 3.0, 16.0), (-run - 3.0, 19.0), (3.0, 0.0),
            align=None,
        )
        plate += Pos(x, PLATE_W / 2 - 44, PLATE_T) * extrude(
            Plane.XZ * prof, amount=4.0, both=True
        )

    return plate.clean()


if __name__ == "__main__":
    c = gen_step()
    print("coupon:", round(c.volume, 0), "mm^3",
          round(c.volume * 0.6 * P.PETG_RHO, 1), "g",
          [round(v, 1) for v in c.bounding_box().size])
