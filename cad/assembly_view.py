"""VYPER-5F showcase assembly -- airframe + motors only, no prop keep-out discs.

Same geometry as assembly.py; the reference discs are omitted because at
127 mm they cover most of the aircraft in a render.
"""

from build123d import Color, Compound, Pos

import assembly
import body
import components as C
import shells
import vy_params as P

SHELL = Color(0.16, 0.18, 0.22)
FAIRING = Color(0.78, 0.24, 0.09)
METAL = Color(0.52, 0.54, 0.58)


def gen_step():
    parts = []
    for name, fn in (
        ("fuselage_lower", shells.fuselage_lower),
        ("fuselage_upper", shells.fuselage_upper),
        ("nose_cone", shells.nose_cone),
        ("tail_cone", shells.tail_cone),
        ("tail_fin", shells.tail_fin),
    ):
        s = fn()
        s.label = name
        s.color = SHELL if "fuselage" in name else FAIRING
        parts.append(s)

    for ang, solid in assembly.placed_pylons().items():
        solid.label = f"pylon_{int(ang)}"
        solid.color = FAIRING
        parts.append(solid)

    for ang in P.ARM_ANGLES:
        mx, my, mz = body.motor_pos(ang)
        m = Pos(mx, my, mz) * C.motor()
        m.label = f"motor_{int(ang)}"
        m.color = METAL
        parts.append(m)

    asm = Compound(children=parts)
    asm.label = "VYPER5F_view"
    return asm
