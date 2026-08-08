"""VYPER fit-check assembly with purchased-part and fastener envelopes.

This is a mechanical integration model, not a cosmetic render. Purchased
parts use published maximum dimensions. The M3x8 motor screw is the exact
ISO 4762 STEP downloaded from step.parts; electronics use datasheet envelopes
because exact vendor STEP models were not available there.
"""

from pathlib import Path
import math

import cadquery as cq

import vyper_shell as M
import vyper_spec as S

ROOT = Path(__file__).resolve().parent


def rounded_board(width, height, thickness, corner_r=5.0, hole_d=4.0):
    board = cq.Workplane("XY").rect(width, height).extrude(thickness)
    board = board.edges("|Z").fillet(corner_r)
    half = 30.5 / 2.0
    for x in (-half, half):
        for y in (-half, half):
            cutter = (
                cq.Workplane("XY").center(x, y)
                .circle(hole_d / 2.0).extrude(thickness)
            )
            board = board.cut(cutter)
    return board


def motor_envelope():
    return (
        cq.Workplane("XY")
        .circle(S.MOTOR_DIAMETER_MM / 2.0)
        .extrude(S.MOTOR_LENGTH_MM)
    )


def prop_envelope():
    """Dimensionally bounded 5x5 biblade envelope; not a scanned airfoil."""
    r = S.PROP_DIAMETER_MM / 2.0
    hub_r = 6.6
    blade = (
        cq.Workplane("XY")
        .moveTo(hub_r, -5.0)
        .lineTo(r - 6.0, -3.5)
        .threePointArc((r, 0.0), (r - 6.0, 3.5))
        .lineTo(hub_r, 5.0)
        .close().extrude(1.5)
    )
    blades = blade.union(blade.rotate((0, 0, 0), (0, 0, 1), 180))
    hub = cq.Workplane("XY").circle(hub_r).extrude(7.1)
    return blades.union(hub)


def local_motor_face_z():
    span = M.R_MOTOR - M.ARM_ROOT_R
    drop = span * math.tan(math.radians(M.ARM_SWEEP))
    return -drop - M.ARM_WIDTH


assembly = cq.Assembly(name="VYPER_200KPH_FITCHECK")
assembly.add(M.result, name="fuselage", color=cq.Color(0.12, 0.16, 0.20, 0.45))
assembly.add(M.tail_cap, name="removable_tail", color=cq.Color(0.08, 0.10, 0.13, 0.8))
assembly.add(M.hub, name="arm_hub", color=cq.Color(0.16, 0.18, 0.22))

one_arm = M.arm.translate((0, 0, M.ARM_Z))
for index, angle in enumerate(M.ARM_ANGLES, 1):
    placed = one_arm.rotate((0, 0, 0), (0, 0, 1), angle)
    assembly.add(placed, name=f"arm_{index}", color=cq.Color(0.10, 0.12, 0.15))

# Battery: axial loading through the removable tail cap.
battery_z0 = M.TAIL_SPIGOT_L + 2.0
battery = (
    cq.Workplane("XY")
    .box(S.BATTERY_WIDTH_MM, S.BATTERY_HEIGHT_MM, S.BATTERY_LENGTH_MM)
    .translate((0, 0, battery_z0 + S.BATTERY_LENGTH_MM / 2.0))
)
assembly.add(battery, name="battery_DOGCOM_1380_6S", color=cq.Color(0.16, 0.35, 0.16))

# Separate 4-in-1 ESC and FC boards on the shelf. Component blocks are maximum
# placement envelopes so shell/stack interactions are visible in the STEP.
esc_z = M.SHELF_Z
fc_z = esc_z + 7.0
esc = rounded_board(36.0, 36.0, 1.6).translate((0, 0, esc_z))
fc = rounded_board(36.0, 36.0, 1.6).translate((0, 0, fc_z))
assembly.add(esc, name="VYPER_ESC_EVT_board", color=cq.Color(0.08, 0.25, 0.12))
assembly.add(fc, name="VYPER_F405_board", color=cq.Color(0.10, 0.35, 0.18))
assembly.add(cq.Workplane("XY").box(28, 24, 4.5).translate((0, 0, esc_z + 3.85)),
             name="ESC_component_envelope", color=cq.Color(0.10, 0.10, 0.10))
assembly.add(cq.Workplane("XY").box(24, 24, 4.0).translate((0, 0, fc_z + 3.6)),
             name="FC_component_envelope", color=cq.Color(0.12, 0.12, 0.12))

# Camera/VTX/RX envelopes forward of the stack and below the ogive shoulder.
assembly.add(cq.Workplane("XY").box(19, 19, 21).translate((0, 0, 187.0)),
             name="camera_19mm", color=cq.Color(0.08, 0.08, 0.08))
assembly.add(cq.Workplane("XY").box(26, 26, 6).translate((0, 0, 177.0)),
             name="VTX_26mm", color=cq.Color(0.30, 0.18, 0.06))
assembly.add(cq.Workplane("XY").box(15, 11, 4).translate((0, 0, 172.0)),
             name="ELRS_RX", color=cq.Color(0.12, 0.28, 0.12))

# Motors, props, and exact M3x8 screws. All propulsion axes remain parallel to
# body +Z; arm sweep moves the motor stations aft but never cants thrust.
motor = motor_envelope()
prop = prop_envelope()
screw_path = ROOT / "cad" / "vendor" / "iso4762_socket_head_cap_screw_m3x8.step"
screw = cq.importers.importStep(str(screw_path)) if screw_path.exists() else None
face_z = M.ARM_Z + local_motor_face_z()
for motor_index, angle in enumerate(M.ARM_ANGLES, 1):
    x = M.R_MOTOR * math.cos(math.radians(angle))
    y = M.R_MOTOR * math.sin(math.radians(angle))
    motor_placed = motor.translate((x, y, face_z - S.MOTOR_LENGTH_MM))
    prop_placed = (
        prop.rotate((0, 0, 0), (0, 0, 1), angle)
        .translate((x, y, face_z - S.MOTOR_LENGTH_MM - 7.1))
    )
    assembly.add(motor_placed, name=f"motor_{motor_index}",
                 color=cq.Color(0.30, 0.30, 0.32))
    assembly.add(prop_placed, name=f"prop_{motor_index}",
                 color=cq.Color(0.75, 0.12, 0.08, 0.55))

    if screw is not None:
        for screw_index, (dx, dy) in enumerate(((-8, -8), (-8, 8), (8, -8), (8, 8)), 1):
            # Rotate each local mounting coordinate with the arm station.
            ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            sx = x + dx * ca - dy * sa
            sy = y + dx * sa + dy * ca
            placed_screw = screw.translate((sx, sy, face_z + M.MOTOR_PAD_T))
            assembly.add(placed_screw, name=f"motor_{motor_index}_M3x8_{screw_index}",
                         color=cq.Color(0.55, 0.57, 0.60))

result = assembly.toCompound()

show_object = globals().get("show_object")
if show_object:
    show_object(result, name="VYPER_fitcheck")


if __name__ == "__main__":
    out = ROOT / "cad" / "vyper_assembly.step"
    cq.exporters.export(result, str(out))
    bb = result.BoundingBox()
    print(f"wrote {out}")
    print(f"assembly {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm, "
          f"solids={len(result.Solids())}")
