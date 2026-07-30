"""VYPER-5 -- shared airframe parameters.

Every dimension the airframe depends on lives here. Nothing else defines
geometry twice. Units are millimetres, degrees, grams, newtons.

FRAME COORDINATE SYSTEM
-----------------------
  Origin  = centre of the bottom plate, on its BOTTOM face (Z = 0).
  +X      = forward (camera end)
  +Y      = left
  +Z      = up
  Motors sit at 45/135/225/315 degrees -- true X, not stretched/deadcat.
  A true X keeps yaw authority symmetric and is what you want for racing;
  deadcat only exists to keep props out of a camera's field of view.

WHY 220 mm / 5 inch
-------------------
  5" is the best thrust-per-dollar class in the hobby. 220 mm true-X puts
  155.6 mm between adjacent motors, so 127 mm props leave a 28.6 mm tip gap
  -- no overlap, no interference drag between discs.

VERTICAL STACK-UP (all frame Z)
-------------------------------
   0.0 .. 4.0    bottom plate
   3.2 .. 17.2   arms -- they seat 0.8 mm DOWN into the locating grooves,
                 so the arm top (the motor mounting face) is at 17.2, not 18
  17.2 .. 37.2   M3x20 standoffs; ESC + FC live in here
  37.2 .. 40.2   top plate
  40.2 ..        battery, strapped on top
  ~43.2          prop disc (motor mount face + ~26 mm for a 2207)

  Everything that reaches above ~42 mm must stay inside R = 46.5 mm along
  the 45 deg (arm) directions, because that is where the prop discs start.
  Along 0/90/180/270 deg the prop discs are never reached at all.
"""

# --------------------------------------------------------------- airframe
WHEELBASE = 220.0                 # motor-to-motor diagonal
R_MOTOR = WHEELBASE / 2.0         # 110.0
ARM_ANGLES = (45.0, 135.0, 225.0, 315.0)

PROP_DIA = 127.0                  # 5.0 in
PROP_R = PROP_DIA / 2.0
# Along an arm axis the prop disc starts at this radius. Nothing tall may
# cross it.
R_PROP_INNER = R_MOTOR - PROP_R   # 46.5

# --------------------------------------------------------------- fasteners
M3_CLR = 3.3                      # snug M3 clearance; locates the arms
M2_CLR = 2.2
ZIP_D = 4.0                       # zip-tie pass-through

# Bolt circles, all on the 45 deg arm axes.
R_STACK = 21.567                  # 30.5 x 30.5 FC/ESC pattern -> (15.25,15.25)
R_ARM_OUT = 38.0                  # outer arm bolt = top-plate standoff

STACK_PITCH = 30.5

# --------------------------------------------------------------- bottom plate
BP_T = 4.0
BP_SQ = 56.0                      # central square
BP_SQ_R = 8.0
BP_BAR_L = 108.0                  # the two crossed bars -> reach R = 54
BP_BAR_W = 17.0
BP_BAR_R = 8.0
BP_GROOVE_W = 9.4                 # arm locating groove (arm is 9.0 wide)
BP_GROOVE_D = 0.8                 # shallow: locating only, not structural
BP_GROOVE_R0 = 8.0
BP_GROOVE_R1 = 56.0

# Accessory bolt pairs: front = camera cage, rear = antenna mount.
#
# THE ARM WEDGE. Arms run out at 45 deg, 9 mm wide, starting at R=12. So a
# point (x, y) is inside an arm when |x-y| <= 6.36 and x+y >= 16.97. Along
# the +X centreline that leaves a wedge whose usable half-width is only
# (x - 6.36). Anything bolted to the nose or the tail has to live inside
# that wedge, which is why both accessory parts have trapezoidal bases that
# are narrow at the inboard end and widen going outboard.
ACC_X = 21.0
ACC_Y = 8.0


def wedge_halfwidth(x):
    """Usable half-width at distance x from centre, before hitting an arm."""
    return abs(x) - (ARM_W_ROOT / 2) * (2 ** 0.5)


# Shared accessory base outline, +X outboard. Mirror for the tail.
ACC_BASE = (
    (-8.0, 5.0),
    (0.0, 12.5),
    (26.0, 16.0),
    (26.0, -16.0),
    (0.0, -12.5),
    (-8.0, -5.0),
)

# XT60 lead strain-relief slot, rear centreline.
LEAD_SLOT_X = -15.0
LEAD_SLOT_W = 8.0                 # along Y
LEAD_SLOT_T = 3.0                 # along X

# --------------------------------------------------------------- arm
ARM_R0 = 12.0                     # inner end radius (4 arms clear each other)
ARM_L = 111.0                     # part length; motor centre at local x = 98
ARM_H = 14.0                      # root height. Top face is FLAT full length.
ARM_W_ROOT = 9.0
ARM_W_TIP = 7.0
PAD_T = 4.0                       # tip thickness == motor screw grip depth

MOTOR_X = R_MOTOR - ARM_R0        # 98.0, arm-local
MOTOR_PATTERN = 16.0              # 2207 / 2306 M3 square
MOTOR_BORE = 8.0                  # bell boss relief + grit drain

ARM_BOLT_1 = R_STACK - ARM_R0     # 9.567
ARM_BOLT_2 = R_ARM_OUT - ARM_R0   # 26.0
ARM_ZIP_X = 64.0                  # motor-wire tie point
ARM_ZIP_D = 2.6

# Underside taper, as (arm-local x, depth). Depth tracks the bending moment
# so peak stress stays roughly flat along the span instead of spiking just
# inboard of the motor pad.
ARM_TAPER = (
    (30.0, 14.0),
    (55.0, 12.5),
    (72.0, 9.5),
    (82.0, 5.5),
    (86.0, 4.0),
)

# Plan outline, +Y half, root -> tip. Mirrored in the generator.
ARM_OUTLINE = (
    (0.0, 4.5),
    (40.0, 4.5),
    (74.0, 3.5),
    (78.0, 4.5),
    (82.0, 8.0),
    (85.0, 12.0),
    (86.5, 13.0),
    (108.0, 13.0),
    (111.0, 9.5),
)

# --------------------------------------------------------------- top plate
TP_SQ = 66.0
TP_R = 10.0
TP_T = 3.0
TP_VENT_Y = 20.0                  # cooling / lightening holes over the stack
TP_VENT_D = 15.0
TP_STRAP_X = 19.0                 # one strap, two slots
TP_STRAP_W = 22.0                 # along Y, for a 20 mm strap
TP_STRAP_T = 4.0                  # along X
TP_ZIP_X = 10.0                   # RX / VTX tie points, clear of the battery
TP_ZIP_Y = 28.5

# --------------------------------------------------------------- standoff
SO_LEN = 20.0
SO_OD = 7.0

# --------------------------------------------------------------- camera cage
CAM_WIDTH = 19.5                  # inner gap; micro cams mount 19.0 across
CAM_WALL = 3.0
CAM_BASE_T = 3.0
CAM_WALL_H = 29.0
CAM_WALL_X0 = 1.0                 # frame X = 22, first station wide enough
CAM_WALL_X1 = 26.0
# Pivot sits as far forward and as high as the top plate allows, so the
# lens ends up AHEAD of the battery nose. See camera_cage.py.
CAM_PIVOT_X = 18.0                # frame X = 39; far enough forward that the
                                  # camera's rear corner clears the web when
                                  # it is tilted back
CAM_PIVOT_Z = 18.0
CAM_RAKE_Z = 20.0                 # front-top rake: (X1+2, RAKE_Z) -> (RAKE_BACK, top)
CAM_RAKE_BACK = 17.0
CAM_WEB_T = 2.5                   # rear web tying the two walls together

# --------------------------------------------------------------- antenna mount
ANT_BASE_T = 3.0
ANT_BLADE_T = 5.0                 # thickness in Y
ANT_TILT = 30.0                   # degrees back from vertical
ANT_BORE = 6.0                    # flexible antenna shaft
ANT_HEAD_L = 20.0
ANT_HEAD_W = 11.0
ANT_HEAD_D = 14.0

# Blade profile in local XZ, leaning toward -X (rearward on the airframe).
ANT_BLADE = (
    (4.0, 0.0),
    (0.0, 10.0),
    (-24.0, 46.0),
    (-36.0, 46.0),
    (-15.0, 8.0),
    (-15.0, 0.0),
)
ANT_HEAD_AT = (-30.0, 41.0)       # local XZ, centre of the head block

# --------------------------------------------------------------- print
NEPTUNE4_BED = (225.0, 225.0, 265.0)
