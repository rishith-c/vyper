"""VYPER-5 full airframe assembly -- verification model, not a printed part.

Places every printed part at its real frame location, plus 2207 motor
envelopes and prop discs as reference bodies, so the stack-up and the prop
clearances can be checked visually rather than trusted.

Reference bodies are labelled REF_* and are NOT for printing.
"""

from build123d import Color, Compound, Cylinder, Location, Pos, Rot

import vy_params as P

import antenna_mount
import arm as arm_mod
import bottom_plate
import camera_cage
import standoff
import top_plate

ARM_SEAT = P.BP_T - P.BP_GROOVE_D   # arms drop into the locating grooves
ARM_TOP = ARM_SEAT + P.ARM_H              # 18.0
TP_Z = ARM_TOP + P.SO_LEN               # 38.0

MOTOR_D = 28.0                          # 2207 bell
MOTOR_H = 27.0                          # mount face -> prop seat
PROP_T = 1.5


def gen_step():
    parts = []

    bp = bottom_plate.gen_step()
    bp.label = "bottom_plate"
    bp.color = Color(0.20, 0.22, 0.26)
    parts.append(bp)

    one_arm = arm_mod.gen_step()
    for i, ang in enumerate(P.ARM_ANGLES):
        a = Rot(0, 0, ang) * Pos(P.ARM_R0, 0, ARM_SEAT) * one_arm
        a.label = f"arm_{i + 1}"
        a.color = Color(0.85, 0.30, 0.10)
        parts.append(a)

    one_so = standoff.gen_step()
    for i, ang in enumerate(P.ARM_ANGLES):
        s = Rot(0, 0, ang) * Pos(P.R_ARM_OUT, 0, ARM_TOP) * one_so
        s.label = f"standoff_{i + 1}"
        s.color = Color(0.55, 0.57, 0.60)
        parts.append(s)

    tp = Pos(0, 0, TP_Z) * top_plate.gen_step()
    tp.label = "top_plate"
    tp.color = Color(0.20, 0.22, 0.26)
    parts.append(tp)

    cc = Pos(P.ACC_X, 0, P.BP_T) * camera_cage.gen_step()
    cc.label = "camera_cage"
    cc.color = Color(0.85, 0.30, 0.10)
    parts.append(cc)

    am = Pos(-P.ACC_X, 0, P.BP_T) * antenna_mount.gen_step()
    am.label = "antenna_mount"
    am.color = Color(0.85, 0.30, 0.10)
    parts.append(am)

    # ---------------------------------------------------- reference bodies
    for i, ang in enumerate(P.ARM_ANGLES):
        m = (
            Rot(0, 0, ang)
            * Pos(P.R_MOTOR, 0, ARM_TOP + MOTOR_H / 2)
            * Cylinder(MOTOR_D / 2, MOTOR_H)
        )
        m.label = f"REF_motor_{i + 1}"
        m.color = Color(0.35, 0.37, 0.40)
        parts.append(m)

        d = (
            Rot(0, 0, ang)
            * Pos(P.R_MOTOR, 0, ARM_TOP + MOTOR_H + PROP_T / 2)
            * Cylinder(P.PROP_R, PROP_T)
        )
        d.label = f"REF_propdisc_{i + 1}"
        d.color = Color(0.30, 0.65, 0.90)
        parts.append(d)

    asm = Compound(children=parts)
    asm.label = "VYPER5"
    return asm


if __name__ == "__main__":
    a = gen_step()
    bb = a.bounding_box()
    print("assembly bbox mm:", [round(v, 2) for v in bb.size])
    print("assembly Z range:", round(bb.min.Z, 2), "->", round(bb.max.Z, 2))
