"""Targeted VYPER internal-envelope and cassette interface checks."""

import vyper_assembly as A
import vyper_shell as M
import vyper_spec as S


parts = {
    name: node.obj.val() if hasattr(node.obj, "val") else node.obj
    for name, node in A.assembly.traverse()
    if node.obj is not None
}

collision_pairs = (
    ("fuselage", "VYPER_ESC_EVT_board"),
    ("fuselage", "VYPER_F405_board"),
    ("fuselage", "ESC_component_envelope"),
    ("fuselage", "FC_component_envelope"),
    ("fuselage", "ESC_aluminum_heat_spreader"),
    ("fuselage", "electronics_cassette_PETG"),
    ("fuselage", "camera_19mm"),
    ("fuselage", "VTX_26mm"),
    ("fuselage", "ELRS_RX"),
    ("arm_hub", "electronics_cassette_PETG"),
    ("electronics_cassette_PETG", "VYPER_ESC_EVT_board"),
    ("electronics_cassette_PETG", "VYPER_F405_board"),
    ("electronics_cassette_PETG", "ESC_component_envelope"),
    ("electronics_cassette_PETG", "FC_component_envelope"),
    ("VYPER_ESC_EVT_board", "ESC_component_envelope"),
    ("VYPER_F405_board", "FC_component_envelope"),
    ("ESC_component_envelope", "ESC_aluminum_heat_spreader"),
    ("camera_19mm", "VTX_26mm"),
    ("VTX_26mm", "ELRS_RX"),
)

for first, second in collision_pairs:
    overlap = parts[first].intersect(parts[second]).Volume()
    assert overlap < 1e-4, f"{first} intersects {second}: {overlap:.4f} mm^3"

hub_top = M.ARM_Z + M.ARM_WIDTH / 2.0
assert abs(S.CASSETTE_BOTTOM_Z_MM - hub_top) < 1e-6

esc_inner_face = S.ESC_BOARD_CENTER_Y_MM + S.ESC_BOARD_THICKNESS_MM / 2.0
esc_standoff_face = -S.CASSETTE_SPINE_THICKNESS_MM / 2.0 - S.CASSETTE_BOARD_GAP_MM
assert abs(esc_inner_face - esc_standoff_face) < 1e-6

fc_inner_face = S.FC_BOARD_CENTER_Y_MM - S.FC_BOARD_THICKNESS_MM / 2.0
fc_standoff_face = S.CASSETTE_SPINE_THICKNESS_MM / 2.0 + S.CASSETTE_BOARD_GAP_MM
assert abs(fc_inner_face - fc_standoff_face) < 1e-6

assert S.ESC_MOUNT_PITCH_X_MM < S.ESC_BOARD_WIDTH_MM
assert S.ESC_MOUNT_PITCH_Z_MM < S.ESC_BOARD_HEIGHT_MM
assert S.FC_MOUNT_PITCH_X_MM < S.FC_BOARD_WIDTH_MM
assert S.FC_MOUNT_PITCH_Z_MM < S.FC_BOARD_HEIGHT_MM

print(f"all {len(collision_pairs)} targeted assembly collision checks pass")
print("hub/cassette and both PCB/standoff interface planes are coincident")
