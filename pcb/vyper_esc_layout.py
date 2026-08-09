"""Mechanical floorplan for the longitudinal VYPER-55A ESC EVT board.

The ESC is purpose-built for the removable vertical electronics cassette. It
is not a stretched square stack: four inverter cells are arranged along the
aircraft Z axis on a 30 x 72 mm board. Every MOSFET is on the outward face so
two electrically isolated aluminium spreaders can intercept the heat. Gate
drivers, MCUs and sensing parts live on the inward face.

This is a packaging and first-order electrical screen, not a current rating or
an authorization to fabricate. Copper, transient, thermal and dyno gates in
ESC_ARCHITECTURE.md remain mandatory.
"""

BOARD_W = 30.0
BOARD_H = 72.0
CORNER_R = 3.0
BOARD_THICKNESS = 1.6
MOUNT_PITCH_X = 24.0
MOUNT_PITCH_Y = 64.0
HOLE_D = 2.4                 # M2 clearance
HARDWARE_KEEPOUT_D = 5.0
LAYERS = 6
OUTER_COPPER_OZ = 3
INNER_COPPER_OZ = 2

HOLES = [(sx * MOUNT_PITCH_X / 2, sy * MOUNT_PITCH_Y / 2)
         for sx in (-1, 1) for sy in (-1, 1)]

# Manufacturer package plus assembly courtyard, millimetres.
FET_CTYD = (7.16, 5.66)
DRV_CTYD = (6.6, 6.6)
MCU_CTYD = (4.6, 4.6)
SENSE_CTYD = (3.2, 2.0)
NTC_CTYD = (1.4, 0.9)
SHUNT_CTYD = (6.9, 3.6)
BUCK_CTYD = (3.5, 2.2)
INDUCTOR_CTYD = (5.8, 5.8)
OPAMP_CTYD = (3.5, 2.3)
HARNESS_CTYD = (5.8, 4.0)
SWD_CTYD = (2.8, 2.8)

CHANNELS = ("M1", "M2", "M3", "M4")
CHANNEL_Y = {"M1": -23.5, "M2": -8.8, "M3": 8.8, "M4": 23.5}
PHASE_X = (-7.4, 0.0, 7.4)
FET_ROW_OFFSET_Y = 3.0

# Alternating long-edge exits prevent phase leads from crossing the board.
MOTOR_SIDE = {"M1": -1, "M2": 1, "M3": -1, "M4": 1}
MOTOR_PAD_STATIONS = (-2.8, 0.0, 2.8)
MOTOR_PAD_CENTER_X = 13.3
MOTOR_PAD_SIZE = (2.0, 2.2)

PARTS = {}
MOTOR_PADS = {}
MOTOR_CONNECTORS = {}
for channel in CHANNELS:
    cy = CHANNEL_Y[channel]

    # High- and low-side rows are both on F.Cu. This makes the complete power
    # stage accessible to one isolated spreader and keeps each switch-node loop
    # on one copper face. The driver connects through a compact via fanout.
    for phase, x in zip("ABC", PHASE_X):
        PARTS[f"Q_{channel}_{phase}_HS"] = dict(
            pos=(x, cy - FET_ROW_OFFSET_Y), side="F", courtyard=FET_CTYD,
            pkg="BSC012N06NS SuperSO8 60V", heat_spreader=True)
        PARTS[f"Q_{channel}_{phase}_LS"] = dict(
            pos=(x, cy + FET_ROW_OFFSET_Y), side="F", courtyard=FET_CTYD,
            pkg="BSC012N06NS SuperSO8 60V", heat_spreader=True)

    # The gate driver is directly behind the six FETs. Control and current
    # sensing stay inward, away from the external aluminium spreader.
    PARTS[f"U_DRV_{channel}"] = dict(
        pos=(0.0, cy), side="B", courtyard=DRV_CTYD,
        pkg="DRV8323H WQFN40 6x6", noisy=True)
    PARTS[f"U_MCU_{channel}"] = dict(
        pos=(-6.0, cy), side="B", courtyard=MCU_CTYD,
        pkg="AT32F421K8U7-4 QFN32 4x4")
    PARTS[f"RN_BEMF_{channel}"] = dict(
        pos=(6.0, cy - 3.9), side="B", courtyard=SENSE_CTYD,
        pkg="3x phase divider plus RC clamps")
    PARTS[f"TH_{channel}"] = dict(
        pos=(6.0, cy + 3.6), side="B", courtyard=NTC_CTYD,
        pkg="0402 NTC")
    PARTS[f"RSH_{channel}"] = dict(
        pos=(7.8, cy), side="B", courtyard=SHUNT_CTYD,
        pkg="WSLF2512R0005FEA 0.5m 10W")

    side = MOTOR_SIDE[channel]
    cx = side * MOTOR_PAD_CENTER_X
    MOTOR_CONNECTORS[channel] = dict(pos=(cx, cy), side="F", rotation=0.0)
    MOTOR_PADS[channel] = [(cx, cy + offset) for offset in MOTOR_PAD_STATIONS]

# The centre feed halves the worst-case VBAT/GND distribution distance versus
# a connector at one end. The cassette provides pigtail strain relief; the
# two heat-spreader segments leave this centre service window uncovered.
BATTERY_PADS = {"VBAT+": (-1.5, 0.0), "GND": (1.5, 0.0)}
BATTERY_PAD_SIZE = (2.2, 5.0)

# Shared low-power support lives on B.Cu.
PARTS["U_BUCK"] = dict(
    pos=(-5.5, 0.0), side="B", courtyard=BUCK_CTYD,
    pkg="LMR16006XDDCR 60V 0.6A")
PARTS["L_BUCK"] = dict(
    pos=(5.8, 0.0), side="B", courtyard=INDUCTOR_CTYD,
    pkg="22uH shielded Isat>=1.6A")
PARTS["U_ISUM"] = dict(
    pos=(-5.0, 33.0), side="B", courtyard=OPAMP_CTYD,
    pkg="TLV9061IDBVR total-current summer")
PARTS["J_HARNESS"] = dict(
    pos=(5.0, -33.0), side="B", courtyard=HARNESS_CTYD,
    pkg="2x4 P1.27 FC harness solder pads")

for channel in CHANNELS:
    cy = CHANNEL_Y[channel]
    PARTS[f"J_SWD_{channel}"] = dict(
        pos=(-10.2, cy + 3.8), side="B", courtyard=SWD_CTYD,
        pkg="2x2 P1.27 SWD test pads")

# Ratings and hard parts. These are checked as requirements, not claims.
CELL_COUNT_MAX = 6
PACK_FULL_V = 25.2
MOSFET_VDS_V = 60.0
DRIVER_ABS_MAX_V = 65.0
TRANSIENT_LIMIT_V = 50.0
CHANNEL_CONTINUOUS_A_TARGET = 30.0
CHANNEL_BURST_A_TARGET = 55.0
BURST_DURATION_S = 2.0
FET_RDS_ON_25C_OHM = 0.0012
FET_RDS_ON_HOT_DESIGN_OHM = 0.0024
FET_COUNT = 24
VDS_OCP_NOMINAL_V = 0.13
SHUNT_OHM = 0.0005
SHUNT_POWER_W = 10.0
CSA_GAIN_V_PER_V = 10.0
MCU_COUNT = 4
MCU_MAX_105C_A = 0.0207
BUCK_OUTPUT_A = 0.6

# Each spreader segment is a packaging envelope. A dielectric interface with a
# verified breakdown rating is mandatory; aluminium must never touch live
# copper. The 6 mm centre gap exposes the battery/regulator service bay.
HEAT_SPREADER_W = 28.0
HEAT_SPREADER_SEGMENT_H = 27.5
HEAT_SPREADER_SEGMENT_COUNT = 2
HEAT_SPREADER_CENTER_GAP = 6.0
HEAT_SPREADER_T = 1.0
THERMAL_PAD_T = 0.5
THERMAL_PAD_MIN_BREAKDOWN_V = 1000

# Direct-source component pricing snapshot. PCB, assembly and shipping excluded.
ACTIVE_PART_COST_USD = {
    "24x BSC012N06NS": 24 * 1.8227,
    "4x DRV8323HRTAR": 4 * 1.4136,
    "4x AT32F421K8U7-4 allowance": 4 * 1.50,
    "LMR16006X plus inductor allowance": 2.75,
    "TLV9061 plus 4x WSLF shunts allowance": 7.00,
}
