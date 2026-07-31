"""VYPER-5F -- faired airframe parameters.

This is a full redesign of the original flat-plate VYPER-5 (still in git
history). Same class, same electronics, completely different structure: a
streamlined body-of-revolution fuselage with the battery and stack buried
inside, and four swept faired pylons ending in motor nacelles.

WHY THE FAIRING, HONESTLY
-------------------------
On a conventional racer the drag is dominated by the exposed battery brick,
the four flat arms and the open stack. Burying all of that is a real win.

But a quad at speed does not fly nose-first -- it pitches over 40-60 degrees,
so a fuselage aligned with the airframe X axis sits at a large angle of attack
and stops behaving like a streamlined body. That is exactly why conventional
racers do not have fuselages.

The fix is MOTOR_TILT: cant the motor pads nose-down so the airframe can make
thrust while the fuselage stays closer to the flow. 12 degrees is a proven
racing value and does not make hovering awkward. Set it to 0 for a
conventional build, or 25-30 for a dedicated speed-run airframe (and expect to
fly it nose-high in the hover).

Realistic expectation: meaningfully faster than the plate version, mostly from
burying the battery and fairing the arms. Not the 40% a wind-tunnel-aligned
body would give.

COORDINATES
-----------
  Origin  = fuselage axis, at the longitudinal datum (battery bay centre-ish)
  +X      = forward (nose)
  +Y      = left
  +Z      = up
  Fuselage is a body of revolution about the X axis.

WHAT DRIVES THE SIZE
--------------------
The SpeedyBee ESC is 44 mm wide and rigid. That single number sets the
fuselage diameter -- see components.py.
"""

import components as C

# --------------------------------------------------------------- airframe
# ROCKET / TAIL-SITTER LAYOUT.
#
# The motors are not on arms. They sit ON the swept wing, which is drawn
# around them. Positions are given explicitly rather than as a radius and an
# angle, because the layout is a stretched X (wider than it is long), not the
# 45-degree true X of a conventional racer.
#
#   front pair  (+70, +-72)
#   rear pair   (-70, +-72)
#
# Every motor pair is at least 140 mm apart, which leaves a 13 mm tip gap on
# 127 mm props. That spacing is the hard constraint the whole planform is
# built around -- 5 inch props simply cannot be packed tighter.
MOTOR_XY = ((70.0, 72.0), (-70.0, 72.0), (-70.0, -72.0), (70.0, -72.0))
WHEELBASE = 200.8                 # diagonal, for reference only
R_MOTOR = WHEELBASE / 2.0
ARM_ANGLES = (45.0, 135.0, 225.0, 315.0)   # legacy

PROP_DIA = C.PROP_D
PROP_R = PROP_DIA / 2.0

# SHIPPED AT ZERO. Motor tilt is what would let the fuselage fly aligned with
# the flow, but it re-cuts the pylon-to-fuselage joint at a compound angle and
# needs board_align_pitch set in Betaflight. The fairing's two biggest wins --
# burying the battery and fairing the arms -- pay off at any attitude, so the
# first article ships conventional. Raise this for a dedicated speed airframe
# and expect to re-verify the root lands.
MOTOR_TILT = 0.0
MOTOR_PAD_Z = 16.0                # pad height above the fuselage axis; also
                                  # the height the pylons leave the fuselage,
                                  # so the whole pylon is flat-topped

# --------------------------------------------------------------- fasteners
M3_CLR = 3.3
M2_CLR = 2.2
M3_TAP = 2.5                      # self-tapping M3 into printed plastic

# --------------------------------------------------------------- fuselage
# Outer profile: (x, radius). Splined, then revolved about X.
# A dart: pointed both ends, fineness 5.3. The ESC still sets the waist at
# 62 mm, but stretching the body makes it slender rather than bulbous.
FUSE_NOSE_X = 150.0
FUSE_TAIL_X = -170.0
FUSE_R_MAX = 31.0                 # 62 mm dia; set by the 44 mm ESC + walls

FUSE_PROFILE = (
    (150.0, 0.8),
    (144.0, 6.0),
    (136.0, 12.0),
    (124.0, 19.0),
    (108.0, 25.0),
    (85.0, 29.0),
    (60.0, 30.5),
    (10.0, 31.0),
    (-40.0, 30.5),
    (-70.0, 28.0),
    (-100.0, 24.0),
    (-130.0, 17.0),
    (-155.0, 9.0),
    (-170.0, 2.5),
)

# Where the internal cavity stops, leaving both tips solid. Kept off the
# profile stations so the cap does not duplicate one.
CAVITY_X = (140.0, -158.0)

FUSE_WALL = 2.2
FUSE_R_IN = FUSE_R_MAX - FUSE_WALL

# Split stations. Nose cone and tail cone come off; the main body splits
# horizontally into a structural lower shell and a lid.
SPLIT_NOSE_X = 95.0
SPLIT_TAIL_X = -95.0
SPLIT_CANOPY_Z = 13.0             # lid parting height
CANOPY_BOLT_X0 = 68.0
CANOPY_BOLT_X1 = -72.0
CANOPY_BOLT_Y = 24.0

# Longitudinal bay layout, front to back.
# The 19 x 19 camera needs 13.5 mm of internal half-diagonal, which the nose
# taper does not provide until about X = 94. Sat at 92 with margin.
CAM_FACE_X = 126.0
# Pack sits aft of the widest point: at X = +64 the inner radius is only
# 24.75 mm against the pack's 24.5 mm half-diagonal, which is no margin at all.
BATT_X0, BATT_X1 = -16.0, 60.0    # 76 mm pack
BATT_FLOOR_Z = -18.0
STACK_X = -43.0                   # stack centre
STACK_Z = -4.0                    # ESC underside
VTX_X = -76.0
RX_X = -88.0

# --------------------------------------------------------------- wings
# Two broad swept panels, each carrying TWO motors, instead of four separate
# arms. The motors stay at the same 220 mm true-X stations; the wing is the
# surface that connects them and blends into the fuselage.
#
# This is the change that turns arms into structure that also does aerodynamic
# work: at 30 m/s the two panels carry roughly half the aircraft weight, which
# unloads the props in fast forward flight. It costs a few percent of hover
# thrust to rotor download -- both quantified in aero.py.
#
# Planform is given for the LEFT wing (+Y); the right is a mirror.
# Arrowhead planform, LEFT panel, as (x, y) round the outline. The leading
# edge kinks so it stays 15 mm ahead of the front motor, and the trailing edge
# kinks to stay 15 mm behind the rear one.
WING_PLAN = (
    (100.0, 24.0),
    (85.0, 72.0),
    (55.0, 118.0),
    (-95.0, 118.0),
    (-88.0, 72.0),
    (-105.0, 24.0),
)
WING_TIP_Y = 118.0
WING_ROOT_Y = 24.0
WING_DEPTH = 14.0                 # max thickness, at the root

# Belly profile, as (depth below the flat top, plan inset).
WING_BELLY = ((0.0, 0.0), (3.5, 0.6), (7.0, 1.8), (10.0, 3.6),
              (12.5, 6.0), (14.0, 9.0))

# A solid panel this size is 92 g of dead plastic. It is hollowed from BELOW,
# which costs nothing to print: the belly is the last surface laid when the
# panel is printed top-face-down, so an open underside needs no bridging at
# all. Skin + perimeter + ribs only.
WING_SKIN = 2.2                   # top skin; also the motor mounting face
WING_WALL = 1.8                   # perimeter and rib thickness
WING_PAD_BOSS_D = 30.0            # local 4 mm pad under each motor
WING_RIBS_X = (78.0, 44.0, 12.0, -24.0, -56.0, -88.0)

# Lightening bay between the two motors. Takes a third of the planform out,
# and takes the same third of the plate out from under the prop discs, which
# is where rotor download comes from.
WING_BAY_X = 0.0
WING_BAY_Y = 76.0
WING_BAY_L = 92.0
WING_BAY_W = 46.0
WING_BAY_R = 14.0

WING_BOLTS_X = (72.0, 26.0, -30.0, -80.0)   # four M3 per side into ribs
WING_BOLT_Z = 6.0

MOTOR_PAD_T = 4.0                 # material left under each motor -> M3x8
MOTOR_POCKET_D = 26.0             # belly hollow under each motor pad
WIRE_CH_W = 6.0                   # motor-wire bore
WIRE_TUNNEL_Z = 8.0               # below the pad plane
SADDLE_GAP = 0.6                  # clearance on every saddled mating face
RIB_T = 9.0                       # backing rib depth; bounded by the bays

NACELLE_D = 30.0                  # motor pad boss on the wing


# --------------------------------------------------------------- tail fin
FIN_X = -118.0                    # root LE. Must sit well forward of the
                                  # tail tip at -142 or the foot hangs in air.
FIN_LEN = 30.0
FIN_H = 58.0                      # measured from the fuselage AXIS, so only
                                  # ~38 mm of it shows above the tail surface
FIN_T = 5.0
FIN_FOOT_W = 20.0                 # saddle foot; must be narrower than the
                                  # local tail diameter so it wraps, not overhangs
FIN_BOLT_SP = 20.0
FIN_SWEEP = 20.0                  # LE sweep, mm aft over the height
ANT_BORE = 6.0                    # VTX antenna shaft, up the fin

# --------------------------------------------------------------- cooling
# Enclosed electronics cook. Annular nose inlet, ducted past the stack, out
# through the tail. Without this the ESC and VTX will thermal-throttle.
INLET_D = 15.0                    # nose aperture; at X=99 the OML radius is
INLET_X = 137.0                   # only 12, so 22 mm would remove the nose
EXIT_D = 26.0
GILL_X = -70.0                    # side gills over the stack
GILL_W, GILL_H, GILL_N = 3.5, 14.0, 4

# --------------------------------------------------------------- print
NEPTUNE4_BED = (225.0, 225.0, 265.0)
PETG_RHO = 1.27e-3
SHELL_FILL = 0.85                 # thin shells print nearly solid
PYLON_FILL = 0.50                 # legacy
WING_FILL = 0.92                  # a hollow shell slices nearly solid
