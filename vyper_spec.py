"""Single source of truth for the VYPER propulsion and purchased-part envelope.

Values in this file are manufacturer-published or explicitly labelled design
targets.  The calculated speed is an analytical screening result; only a
radar/GPS flight test can establish the aircraft's real top speed.
"""

import math

# Mission target
TARGET_SPEED_KPH = 200.0

# T-Motor Velox V2207 V3, 1950KV, 6S.  The 31,612.6 rpm / 45 A point is the
# manufacturer's static P49436-3 bench result at full throttle.  The selected
# HQProp 5x5 biblade is not represented by that thrust table, so the RPM is a
# conservative screening input rather than a matched-prop guarantee.
MOTOR_MODEL = "T-Motor Velox V2207 V3 1950KV"
MOTOR_DIAMETER_MM = 27.5
MOTOR_LENGTH_MM = 31.8
MOTOR_MASS_G = 37.1
MOTOR_MOUNT_PITCH_MM = 16.0
MOTOR_PEAK_CURRENT_A = 45.0
MOTOR_STATIC_RPM = 31_612.6
MOTOR_COUNT = 4

# HQProp 5x5V1S biblade, manufacturer dimensions.
PROP_MODEL = "HQProp 5x5V1S"
PROP_DIAMETER_MM = 127.0
PROP_PITCH_IN = 5.0
PROP_MASS_G = 3.33

# OrcaSlicer 2.4.2 output using the repository's Neptune 4 / 0.4 mm / 0.20 mm
# structural PETG profile.  These are slicer estimates, still subject to real
# spool diameter/density and printer flow calibration.
SLICED_MASS_G = {
    "shell_body": 59.48,
    "shell_nose": 36.40,
    "arm_each": 27.49,  # includes build-plate-only support material
    "hub": 27.60,
    "electronics_cassette": 3.35,
    "tail_cap": 20.32,
}

# Orca's feature-tagged extrusion assigns about 7.52% of each arm file to
# Support/Support interface: 27.49 g × 0.0752 = 2.07 g. Keep this separate when
# comparing the sliced model against the support-free solid-volume estimate.
ARM_SUPPORT_MASS_G = 2.07


def sliced_airframe_mass_g():
    return (SLICED_MASS_G["shell_body"] + SLICED_MASS_G["shell_nose"]
            + 4 * SLICED_MASS_G["arm_each"] + SLICED_MASS_G["hub"]
            + SLICED_MASS_G["electronics_cassette"]
            + SLICED_MASS_G["tail_cap"])

# DOGCOM Pro 1380 mAh 180C 6S.  C ratings are manufacturer claims and are not
# substitutes for measuring voltage sag, connector temperature, and pack
# temperature on the actual aircraft.
BATTERY_MODEL = "DOGCOM Pro 1380mAh 180C 6S"
BATTERY_LENGTH_MM = 81.0
BATTERY_WIDTH_MM = 39.0
BATTERY_HEIGHT_MM = 33.0
BATTERY_MASS_G = 209.0
BATTERY_CAPACITY_AH = 1.380
BATTERY_C_RATING_CLAIMED = 180.0
BATTERY_CELLS = 6
BATTERY_FULL_VOLTAGE_V = 4.2 * BATTERY_CELLS

# Longitudinal custom-electronics package.  The airframe is a rocket body, so
# inheriting a horizontal 30.5 mm racing-stack square wastes the available
# length and leaves the ESC with poor copper/thermal area.  Both custom boards
# instead mount vertically in a removable cassette immediately above the arm
# hub.  PCB local X is aircraft X and PCB local Y maps to aircraft +Z.
ESC_BOARD_WIDTH_MM = 36.0
ESC_BOARD_HEIGHT_MM = 72.0
ESC_BOARD_THICKNESS_MM = 1.6
ESC_BOARD_CORNER_RADIUS_MM = 3.0
ESC_MOUNT_PITCH_X_MM = 30.0
ESC_MOUNT_PITCH_Z_MM = 64.0
ESC_MOUNT_HOLE_D_MM = 2.4

FC_BOARD_WIDTH_MM = 26.0
FC_BOARD_HEIGHT_MM = 64.0
FC_BOARD_THICKNESS_MM = 1.6
FC_BOARD_CORNER_RADIUS_MM = 3.0
FC_MOUNT_PITCH_X_MM = 16.0
FC_MOUNT_PITCH_Z_MM = 56.0
FC_MOUNT_HOLE_D_MM = 3.2       # M2 silicone isolation grommet envelope

ELECTRONICS_CENTER_Z_MM = 161.0
ESC_BOARD_CENTER_Y_MM = -4.5
FC_BOARD_CENTER_Y_MM = 4.5
ESC_COMPONENT_HEIGHT_MM = 4.5
FC_COMPONENT_HEIGHT_MM = 4.0
ESC_HEAT_SPREADER_THICKNESS_MM = 1.0
ESC_HEAT_SPREADER_WIDTH_MM = 34.0
ESC_HEAT_SPREADER_SEGMENT_HEIGHT_MM = 27.5
ESC_HEAT_SPREADER_CENTER_GAP_MM = 6.0

# Removable PETG electronics cassette.  It lands on the hub top face at Z123,
# uses two M3 screws into heat-set inserts in the intact hub core, and is
# laterally captured by the ogive/nose when assembled.
CASSETTE_BOTTOM_Z_MM = 123.0
CASSETTE_TOP_Z_MM = 200.0
CASSETTE_WIDTH_MM = 38.0
CASSETTE_SPINE_THICKNESS_MM = 2.0
CASSETTE_RAIL_WIDTH_MM = 3.0
CASSETTE_BOARD_STANDOFF_D_MM = 5.0
CASSETTE_BOARD_GAP_MM = 2.7
CASSETTE_BOARD_INSERT_D_MM = 3.2
CASSETTE_BOARD_INSERT_DEPTH_MM = 2.5
CASSETTE_HUB_SCREW_PITCH_MM = 10.0
CASSETTE_HUB_SCREW_D_MM = 3.4
CASSETTE_HUB_INSERT_D_MM = 4.2
CASSETTE_HUB_INSERT_DEPTH_MM = 5.0

# Electrical design limits for the custom 4-in-1 ESC.  These are requirements,
# not achieved ratings, until EVT hardware passes the validation gates.
# A sealed rocket fuselage is not the same thermal environment as an open
# racing frame.  The selected motor reaches 45 A only at the static full-load
# bench point; the ESC is therefore rated here for 30 A continuous and a
# deliberately time-limited 55 A / 2 s speed-run burst.  Those remain design
# requirements until instrumented hardware testing establishes real ratings.
ESC_CHANNEL_CONTINUOUS_A_TARGET = 30.0
ESC_CHANNEL_BURST_A_TARGET = 55.0
ESC_BURST_DURATION_S_TARGET = 2.0
ESC_MOSFET_VDS_RATING_V = 60.0
ESC_GATE_DRIVER_ABS_MAX_V = 65.0
ESC_SWITCH_NODE_TRANSIENT_LIMIT_V = 50.0

# The existing true-X geometry uses 110 mm motor radius (220 mm diagonal).
MOTOR_RADIUS_MM = 110.0


def ideal_pitch_speed_kph(rpm=MOTOR_STATIC_RPM, pitch_in=PROP_PITCH_IN):
    """No-slip helical pitch speed. Real speed is lower because props slip."""
    return rpm * pitch_in * 0.0254 / 60.0 * 3.6


def required_pitch_efficiency(target_kph=TARGET_SPEED_KPH):
    return target_kph / ideal_pitch_speed_kph()


def adjacent_motor_spacing_mm(radius=MOTOR_RADIUS_MM):
    return math.sqrt(2.0) * radius


def claimed_battery_current_a():
    return BATTERY_CAPACITY_AH * BATTERY_C_RATING_CLAIMED
