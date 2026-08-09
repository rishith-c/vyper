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


def rounded_board(width, height, thickness, corner_r, hole_d,
                  hole_pitch_x, hole_pitch_y):
    board = cq.Workplane("XY").rect(width, height).extrude(thickness / 2.0, both=True)
    board = board.edges("|Z").fillet(corner_r)
    for x in (-hole_pitch_x / 2.0, hole_pitch_x / 2.0):
        for y in (-hole_pitch_y / 2.0, hole_pitch_y / 2.0):
            cutter = (
                cq.Workplane("XY").center(x, y)
                .circle(hole_d / 2.0).extrude(thickness, both=True)
            )
            board = board.cut(cutter)
    return board


def vertical_board(width, height, thickness, corner_r, hole_d,
                   hole_pitch_x, hole_pitch_z, center_y, center_z):
    """PCB plane in aircraft XZ; component sides face radially outward."""
    return (
        rounded_board(width, height, thickness, corner_r, hole_d,
                      hole_pitch_x, hole_pitch_z)
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((0, center_y, center_z))
    )


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

# The removable cassette lands on the hub and carries two longitudinal boards
# back-to-back.  This follows the rocket fuselage instead of forcing a square
# racing stack across it.
assembly.add(M.electronics_cassette, name="electronics_cassette_PETG",
             color=cq.Color(0.22, 0.24, 0.28))
esc = vertical_board(
    S.ESC_BOARD_WIDTH_MM, S.ESC_BOARD_HEIGHT_MM, S.ESC_BOARD_THICKNESS_MM,
    S.ESC_BOARD_CORNER_RADIUS_MM, S.ESC_MOUNT_HOLE_D_MM,
    S.ESC_MOUNT_PITCH_X_MM, S.ESC_MOUNT_PITCH_Z_MM,
    S.ESC_BOARD_CENTER_Y_MM, S.ELECTRONICS_CENTER_Z_MM,
)
fc = vertical_board(
    S.FC_BOARD_WIDTH_MM, S.FC_BOARD_HEIGHT_MM, S.FC_BOARD_THICKNESS_MM,
    S.FC_BOARD_CORNER_RADIUS_MM, S.FC_MOUNT_HOLE_D_MM,
    S.FC_MOUNT_PITCH_X_MM, S.FC_MOUNT_PITCH_Z_MM,
    S.FC_BOARD_CENTER_Y_MM, S.ELECTRONICS_CENTER_Z_MM,
)
assembly.add(esc, name="VYPER_ESC_EVT_board", color=cq.Color(0.08, 0.25, 0.12))
assembly.add(fc, name="VYPER_F405_board", color=cq.Color(0.10, 0.35, 0.18))
assembly.add(
    cq.Workplane("XY").box(
        S.ESC_BOARD_WIDTH_MM - 4.0, S.ESC_COMPONENT_HEIGHT_MM,
        S.ESC_BOARD_HEIGHT_MM - 6.0,
    ).translate((
        0,
        S.ESC_BOARD_CENTER_Y_MM - S.ESC_BOARD_THICKNESS_MM / 2.0
        - S.ESC_COMPONENT_HEIGHT_MM / 2.0,
        S.ELECTRONICS_CENTER_Z_MM,
    )),
             name="ESC_component_envelope", color=cq.Color(0.10, 0.10, 0.10))
assembly.add(
    cq.Workplane("XY").box(
        S.FC_BOARD_WIDTH_MM - 3.0, S.FC_COMPONENT_HEIGHT_MM,
        S.FC_BOARD_HEIGHT_MM - 6.0,
    ).translate((
        0,
        S.FC_BOARD_CENTER_Y_MM + S.FC_BOARD_THICKNESS_MM / 2.0
        + S.FC_COMPONENT_HEIGHT_MM / 2.0,
        S.ELECTRONICS_CENTER_Z_MM,
    )),
             name="FC_component_envelope", color=cq.Color(0.12, 0.12, 0.12))

# Two electrically isolated aluminum heat spreaders on the ESC's outward face.
# Their centre gap keeps the battery pads and buck-regulator support accessible.
# This is an integration envelope, not a claim that the 55 A burst rating has
# passed thermal qualification.
spreader_y = (
    S.ESC_BOARD_CENTER_Y_MM - S.ESC_BOARD_THICKNESS_MM / 2.0
    - S.ESC_COMPONENT_HEIGHT_MM - S.ESC_HEAT_SPREADER_THICKNESS_MM / 2.0
)
spreader_offset_z = (
    S.ESC_HEAT_SPREADER_CENTER_GAP_MM / 2.0
    + S.ESC_HEAT_SPREADER_SEGMENT_HEIGHT_MM / 2.0
)
spreader_segments = []
for offset_z in (-spreader_offset_z, spreader_offset_z):
    spreader_segments.append(
        cq.Workplane("XY").box(
            S.ESC_HEAT_SPREADER_WIDTH_MM,
            S.ESC_HEAT_SPREADER_THICKNESS_MM,
            S.ESC_HEAT_SPREADER_SEGMENT_HEIGHT_MM,
        ).translate((0, spreader_y, S.ELECTRONICS_CENTER_Z_MM + offset_z)).val()
    )
assembly.add(
    cq.Compound.makeCompound(spreader_segments),
    name="ESC_aluminum_heat_spreader", color=cq.Color(0.55, 0.57, 0.60),
)

# Camera/VTX/RX envelopes continue forward of the cassette inside the ogive.
assembly.add(cq.Workplane("XY").box(19, 19, 21).translate((0, 0, 229.0)),
             name="camera_19mm", color=cq.Color(0.08, 0.08, 0.08))
assembly.add(cq.Workplane("XY").box(26, 26, 6).translate((0, 0, 207.0)),
             name="VTX_26mm", color=cq.Color(0.30, 0.18, 0.06))
assembly.add(cq.Workplane("XY").box(15, 11, 4).translate((0, 0, 201.0)),
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
