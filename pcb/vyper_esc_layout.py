"""Mechanical floorplan for the VYPER-55A four-channel ESC EVT board.

This module is the single source of truth for board/airframe interaction and
power-stage placement.  It is not an electrical rating and it is not an
authorization to order hardware.  The schematic, copper, thermal model and
EVT gates in ESC_ARCHITECTURE.md must all be complete first.

The difficult packaging decision is explicit: each inverter's three high-side
MOSFETs are on F.Cu and the matching three low-side devices are directly below
on B.Cu. That gives each half bridge a short vertical current loop. True
footprint DRC rejected the original 36 mm study; the validated floorplan is
43 mm and clears both the package courtyards and M3 keepouts.
"""

import math

BOARD_W = 43.0
BOARD_H = 43.0
CORNER_R = 12.0
FUSE_CAVITY_R = 26.5
HOLE_PITCH = 30.5
HOLE_D = 3.2
HARDWARE_KEEPOUT_D = 6.5
LAYERS = 6
OUTER_COPPER_OZ = 2
INNER_COPPER_OZ = 1

HOLES = [(sx * HOLE_PITCH / 2, sy * HOLE_PITCH / 2)
         for sx in (-1, 1) for sy in (-1, 1)]

# Manufacturer package plus assembly courtyard, millimetres.
FET_CTYD = (7.16, 5.66)     # KiCad TDSON-8-1 assembly courtyard
DRV_CTYD = (6.6, 6.6)       # TI DRV8323H, WQFN-40 6x6 body
MCU_CTYD = (4.6, 4.6)       # AT32F421K8U7-4, QFN32 4x4 body
SENSE_CTYD = (3.2, 2.0)     # 6-pin 0402 resistor network / RC filter bank
NTC_CTYD = (1.4, 0.9)       # 0402 NTC at the hottest bridge
SHUNT_CTYD = (6.9, 3.6)     # Vishay WSLF2512 Kelvin-routed current shunt
BUCK_CTYD = (3.5, 2.2)      # LMR16006X SOT-23-6 plus assembly allowance
INDUCTOR_CTYD = (5.8, 5.8)  # shielded 22 uH, Isat >= 1.6 A
OPAMP_CTYD = (3.5, 2.3)     # TLV9061 SOT-23-5 current-sum amplifier
HARNESS_CTYD = (5.8, 4.0)   # 2x4 1.27 mm solder-pad FC harness

CHANNELS = ("M1", "M2", "M3", "M4")
MOTOR_PAD_STATIONS = (-7.0, 0.0, 7.0)
MOTOR_PAD_RADIUS = 19.9


def rotate(x, y, deg):
    a = math.radians(deg)
    return (x * math.cos(a) - y * math.sin(a),
            x * math.sin(a) + y * math.cos(a))


def rotate_wh(wh, deg):
    """Swap an axis-aligned courtyard for a 90/270-degree channel."""
    quarter_turns = int(round(deg / 90.0)) % 2
    return (wh[1], wh[0]) if quarter_turns else wh


# A channel is defined in the +Y (north) orientation and rotated clockwise.
# Motor mapping follows a normal X quad order only at firmware-target time;
# the board file keeps physical channels unambiguous and does not guess motor
# direction.
ROTATION = {"M1": 0.0, "M2": -90.0, "M3": 180.0, "M4": 90.0}

PARTS = {}
MOTOR_PADS = {}
for channel in CHANNELS:
    deg = ROTATION[channel]
    # One row on each face.  Each x station is one phase half bridge, so the
    # switch node can change layers through a compact via field between FETs.
    # 7.4 mm station pitch clears the 7.16 mm manufacturer-derived TDSON
    # courtyards and, more importantly, its asymmetric 4.55 mm drain lands.
    for phase, x in zip("ABC", (-7.4, 0.0, 7.4)):
        for side, role in (("F", "HS"), ("B", "LS")):
            pos = rotate(x, 16.0, deg)
            PARTS[f"Q_{channel}_{phase}_{role}"] = dict(
                pos=pos, side=side, courtyard=rotate_wh(FET_CTYD, deg),
                pkg="BSC012N06NS SuperSO8 60V")

    # Driver is on F, MCU and BEMF divider/filter network on B.  Keeping the
    # driver radially inboard of its FET row caps every gate run below 10 mm.
    PARTS[f"U_DRV_{channel}"] = dict(
        pos=rotate(0.0, 9.7, deg), side="F", courtyard=DRV_CTYD,
        pkg="DRV8323H WQFN40 6x6", noisy=True)
    PARTS[f"U_MCU_{channel}"] = dict(
        pos=rotate(0.0, 9.7, deg), side="B", courtyard=MCU_CTYD,
        pkg="AT32F421K8U7-4 QFN32 4x4")
    PARTS[f"RN_BEMF_{channel}"] = dict(
        pos=rotate(4.7, 4.8, deg), side="B",
        courtyard=rotate_wh(SENSE_CTYD, deg),
        pkg="3x phase divider plus RC clamps")
    PARTS[f"TH_{channel}"] = dict(
        pos=rotate(-4.7, 9.1, deg), side="B",
        courtyard=rotate_wh(NTC_CTYD, deg),
        pkg="0402 NTC")
    PARTS[f"RSH_{channel}"] = dict(
        pos=rotate(8.0, 8.0, deg), side="B",
        courtyard=rotate_wh(SHUNT_CTYD, deg),
        pkg="WSLF2512R0005FEA 0.5m 10W")

    # Keep the radial edge of every plated motor pad 0.6 mm inside Edge.Cuts.
    # KiCad's default copper-to-edge rule is 0.5 mm, leaving 0.1 mm process
    # margin while preserving direct perimeter access for phase wires.
    MOTOR_PADS[channel] = [rotate(x, MOTOR_PAD_RADIUS, deg)
                           for x in MOTOR_PAD_STATIONS]

# Vertical 12-AWG pigtails pass through the central shelf/loom opening.  The
# pads are intentionally central, away from every mounting hole and board edge.
BATTERY_PADS = {"VBAT+": (-1.5, 0.0), "GND": (1.5, 0.0)}
BATTERY_PAD_SIZE = (2.2, 5.0)
MOTOR_PAD_SIZE = (2.2, 2.0)

# The front-face quadrant gaps are the only locations that clear the four
# radial gate drivers, mounting keepouts and central battery pigtails.  These
# are electrically shared support parts, not unplaced schematic afterthoughts.
PARTS["U_BUCK"] = dict(
    pos=(-7.0, -7.0), side="F", courtyard=BUCK_CTYD,
    pkg="LMR16006XDDCR 60V 0.6A")
PARTS["L_BUCK"] = dict(
    pos=(-7.0, 7.0), side="F", courtyard=INDUCTOR_CTYD,
    pkg="22uH shielded Isat>=1.6A")
PARTS["U_ISUM"] = dict(
    pos=(7.0, -7.0), side="F", courtyard=OPAMP_CTYD,
    pkg="TLV9061IDBVR total-current summer")
PARTS["J_HARNESS"] = dict(
    pos=(7.0, 7.0), side="F", courtyard=HARNESS_CTYD,
    pkg="2x4 P1.27 FC harness solder pads")

# Ratings and hard parts.  These are checked as requirements, not claims.
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

# Direct-source component pricing snapshot.  Assembly, PCB fabrication and
# shipping are excluded; a one-off prototype does not meet the aircraft's
# sub-$200 target.  This is here to stop BOM arithmetic from hiding that fact.
ACTIVE_PART_COST_USD = {
    "24x BSC012N06NS": 24 * 1.8227,  # LCSC 10+ price seen 2026-08-08
    "4x DRV8323HRTAR": 4 * 1.4136,   # LCSC 1+ price seen 2026-08-08
    "4x AT32F421K8U7-4 allowance": 4 * 1.50,
    "LMR16006X plus inductor allowance": 2.75,
    "TLV9061 plus 4x WSLF shunts allowance": 7.00,
}
