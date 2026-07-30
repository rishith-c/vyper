"""VYPER-5 standoff, M3 x 20 -- print four ONLY if you skip the metal ones.

A set of aluminium M3x20 female-female standoffs is about $4 and is the
right answer: they are threaded, so the top plate takes a short M3x8 from
above and the arm takes an M3x25 from below, and the column is in pure
compression through metal.

This printed version is a plain SPACER -- no thread. If you use it you need
a single M3x45 all the way through bottom plate + arm + spacer + top plate
with a nyloc on top, and you have to be careful not to crush it.

7 mm OD on a 3.3 mm bore leaves 1.85 mm of wall, which is four perimeters
at 0.4 mm and no infill. Print standing up.
"""

from build123d import Cylinder, Pos

import vy_params as P


def gen_step():
    so = Pos(0, 0, P.SO_LEN / 2) * Cylinder(P.SO_OD / 2, P.SO_LEN)
    so -= Pos(0, 0, P.SO_LEN / 2) * Cylinder(P.M3_CLR / 2, P.SO_LEN + 4)
    return so.clean()


if __name__ == "__main__":
    s = gen_step()
    print("standoff volume mm^3:", round(s.volume, 1))
    print("standoff bbox   mm  :", [round(v, 2) for v in s.bounding_box().size])
