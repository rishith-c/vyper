"""VYPER-5F full airframe assembly -- verification model, not a printed part."""

from build123d import Color, Compound, Pos, Rot

import body
import components as C
import arm
import shells
import vy_params as P

# angle -> (hand, extra yaw)


SHELL = Color(0.22, 0.24, 0.28)
FAIRING = Color(0.80, 0.28, 0.10)
GUTS = Color(0.30, 0.75, 0.45)
REF = Color(0.30, 0.65, 0.90)


def placed_arms():
    """Two blades crossed at +/- the half-angle, half-lapped at the centre."""
    out = {}
    for notch, sign in (("top", 1.0), ("bottom", -1.0)):
        out[notch] = (
            Pos(0, 0, P.MOTOR_PAD_Z)
            * Rot(0, 0, sign * arm.ARM_ANGLE)
            * arm.gen(notch)
        )
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

    for hand, solid in placed_arms().items():
        solid.label = f"arm_{hand}"
        solid.color = FAIRING
        parts.append(solid)

    for name, solid in placed_components().items():
        solid.label = f"PART_{name}"
        solid.color = GUTS
        parts.append(solid)

    for i, (mx, my, mz) in enumerate(body.all_motors()):
        m = Pos(mx, my, mz) * C.motor()
        m.label = f"PART_motor_{i}"
        m.color = Color(0.45, 0.47, 0.50)
        parts.append(m)

        d = Pos(mx, my, mz + C.MOTOR_PAD_TO_PROP) * C.prop_disc()
        d.label = f"REF_propdisc_{i}"
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
