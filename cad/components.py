"""Solid models of the actual bought parts.

These are not decoration. Every internal dimension of the airframe is derived
from these envelopes, and verify.py boolean-checks each one against the bay it
is supposed to live in. "Perfect fit" has to be a check, not a claim.

All dimensions are from manufacturer spec sheets (July 2026):

  SpeedyBee F405 V4 BLS 55A stack
    FC   41.6 x 39.4 x 7.8 mm, 10.5 g
    ESC  45.6 x 44.0 x 8.0 mm, 23.5 g
    both 30.5 x 30.5 M3, assembled stack height 16.1 mm
  CNHL Ultra Black 6S 1050 mAh 150C
    76 x 38 x 31 mm, 180 g
  2207 motor
    28 mm bell, 16 x 16 M3, M5 shaft
  19 mm micro camera
    19 x 19 face, ~22 mm deep with lens

The ESC being 44 mm wide is what sets the fuselage diameter. It is the widest
rigid object in the aircraft and it cannot be rotated or bent around anything.
"""

from build123d import Box, Cylinder, Pos, Rot

# ---------------------------------------------------------------- motor
MOTOR_BELL_D = 28.0
MOTOR_H = 32.0                 # base to top of bell
MOTOR_PATTERN = 16.0           # M3 square
MOTOR_PAD_TO_PROP = 26.0       # mount face -> prop plane, 2207 class
MOTOR_MASS = 34.0

# ---------------------------------------------------------------- stack
ESC_L, ESC_W, ESC_H = 45.6, 44.0, 8.0
FC_L, FC_W, FC_H = 41.6, 39.4, 7.8
STACK_PITCH = 30.5
STACK_H = 16.1                 # assembled, ESC underside -> FC top
STACK_MASS = 34.0

# ---------------------------------------------------------------- battery
BATT_L, BATT_W, BATT_H = 76.0, 38.0, 31.0
BATT_MASS = 180.0

# ---------------------------------------------------------------- video / RC
CAM_W, CAM_H, CAM_D = 19.0, 19.0, 22.0
CAM_MASS = 8.0
VTX_L, VTX_W, VTX_H = 30.0, 30.0, 6.0
VTX_MASS = 9.0
RX_L, RX_W, RX_H = 15.0, 11.0, 4.0
RX_MASS = 1.5

XT60_W, XT60_H, XT60_D = 16.0, 8.1, 8.0
CAP_D, CAP_L = 12.5, 20.0      # 470 uF / 35 V low-ESR

PROP_D = 127.0                 # 5.0 in
PROP_MASS = 4.5

# Clearance added around every component when a bay is cut for it.
FIT = 1.0


def _box(l, w, h, grow=0.0):
    return Box(l + 2 * grow, w + 2 * grow, h + 2 * grow)


def motor(grow=0.0):
    """Bell envelope, origin at the CENTRE OF THE MOUNT FACE, growing +Z."""
    return Pos(0, 0, MOTOR_H / 2) * Cylinder(MOTOR_BELL_D / 2 + grow, MOTOR_H)


def stack(grow=0.0):
    """ESC + FC envelope, origin at the ESC underside centre, growing +Z.

    Uses the larger ESC footprint for the whole height -- the FC is smaller,
    but a bay sized to the FC would not admit the ESC.
    """
    return Pos(0, 0, STACK_H / 2) * _box(ESC_L, ESC_W, STACK_H, grow)


def battery(grow=0.0):
    """Origin at the pack centre."""
    return _box(BATT_L, BATT_W, BATT_H, grow)


def camera(grow=0.0):
    """Origin at the centre of the 19 x 19 front face, body growing -X."""
    return Pos(-CAM_D / 2, 0, 0) * _box(CAM_D, CAM_W, CAM_H, grow)


def vtx(grow=0.0):
    return _box(VTX_L, VTX_W, VTX_H, grow)


def rx(grow=0.0):
    return _box(RX_L, RX_W, RX_H, grow)


def prop_disc(thickness=3.0):
    """Full swept disc, origin at the prop plane centre."""
    return Cylinder(PROP_D / 2, thickness)


# Everything that is not printed, for the mass budget.
PAYLOAD = {
    "motors x4": 4 * MOTOR_MASS,
    "stack": STACK_MASS,
    "battery": BATT_MASS,
    "camera": CAM_MASS,
    "vtx + antenna": VTX_MASS + 7.0,
    "rx": RX_MASS,
    "props x4": 4 * PROP_MASS,
    "wiring, XT60, cap, heatshrink": 25.0,
    "fasteners": 26.0,
}
