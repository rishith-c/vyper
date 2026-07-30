"""VYPER-5F full airframe assembly -- verification model, not a printed part."""

from build123d import Color, Compound, Pos, Rot

import body
import components as C
import pylon
import shells
import vy_params as P

# angle -> (hand, extra yaw)
PYLONS = {45.0: ("a", 0.0), 225.0: ("a", 180.0), 315.0: ("b", 0.0), 135.0: ("b", 180.0)}

SHELL = Color(0.22, 0.24, 0.28)
FAIRING = Color(0.80, 0.28, 0.10)
GUTS = Color(0.30, 0.75, 0.45)
REF = Color(0.30, 0.65, 0.90)


def placed_pylons():
    out = {}
    cache = {h: pylon.gen(h) for h in ("a", "b")}
    for ang, (hand, yaw) in PYLONS.items():
        mx, my, mz = body.motor_pos(ang)
        out[ang] = Pos(mx, my, mz) * Rot(0, 0, yaw) * cache[hand]
    return out


def placed_components():
    names = ("battery", "stack", "vtx", "rx")
    out = dict(zip(names, shells.component_envelopes()))
    out["camera"] = Pos(P.CAM_FACE_X, 0, 0) * C.camera()
    return out


def gen_step():
    parts = []

    for name, fn, col in (
        ("fuselage_lower", shells.fuselage_lower, SHELL),
        ("fuselage_upper", shells.fuselage_upper, SHELL),
        ("nose_cone", shells.nose_cone, FAIRING),
        ("tail_cone", shells.tail_cone, FAIRING),
        ("tail_fin", shells.tail_fin, FAIRING),
    ):
        s = fn()
        s.label = name
        s.color = col
        parts.append(s)

    for ang, solid in placed_pylons().items():
        solid.label = f"pylon_{int(ang)}"
        solid.color = FAIRING
        parts.append(solid)

    for name, solid in placed_components().items():
        solid.label = f"PART_{name}"
        solid.color = GUTS
        parts.append(solid)

    for ang in P.ARM_ANGLES:
        mx, my, mz = body.motor_pos(ang)
        m = Pos(mx, my, mz) * C.motor()
        m.label = f"PART_motor_{int(ang)}"
        m.color = Color(0.45, 0.47, 0.50)
        parts.append(m)

        d = Pos(mx, my, mz + C.MOTOR_PAD_TO_PROP) * C.prop_disc()
        d.label = f"REF_propdisc_{int(ang)}"
        d.color = REF
        parts.append(d)

    asm = Compound(children=parts)
    asm.label = "VYPER5F"
    return asm


if __name__ == "__main__":
    a = gen_step()
    bb = a.bounding_box()
    print("assembly bbox mm:", [round(v, 1) for v in bb.size])
    print("Z range:", round(bb.min.Z, 1), "->", round(bb.max.Z, 1))
