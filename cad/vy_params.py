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
WHEELBASE = 220.0
R_MOTOR = WHEELBASE / 2.0
ARM_ANGLES = (45.0, 135.0, 225.0, 315.0)

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
FUSE_NOSE_X = 112.0
FUSE_TAIL_X = -142.0
FUSE_R_MAX = 31.0                 # 62 mm dia; set by the 44 mm ESC + walls

FUSE_PROFILE = (
    (112.0, 0.8),
    (108.0, 6.5),
    (100.0, 12.5),
    (88.0, 19.5),
    (72.0, 25.5),
    (50.0, 29.5),
    (35.0, 31.0),
    (0.0, 31.0),
    (-45.0, 31.0),
    (-70.0, 27.5),
    (-95.0, 22.0),
    (-118.0, 15.0),
    (-135.0, 8.0),
    (-142.0, 3.0),
)

FUSE_WALL = 2.2
FUSE_R_IN = FUSE_R_MAX - FUSE_WALL

# Split stations. Nose cone and tail cone come off; the main body splits
# horizontally into a structural lower shell and a lid.
SPLIT_NOSE_X = 68.0
SPLIT_TAIL_X = -92.0
SPLIT_CANOPY_Z = 13.0             # lid parting height
CANOPY_BOLT_X0 = 52.0
CANOPY_BOLT_X1 = -56.0
CANOPY_BOLT_Y = 24.0

# Longitudinal bay layout, front to back.
# The 19 x 19 camera needs 13.5 mm of internal half-diagonal, which the nose
# taper does not provide until about X = 94. Sat at 92 with margin.
CAM_FACE_X = 92.0
# Pack sits aft of the widest point: at X = +64 the inner radius is only
# 24.75 mm against the pack's 24.5 mm half-diagonal, which is no margin at all.
BATT_X0, BATT_X1 = -16.0, 60.0    # 76 mm pack
BATT_FLOOR_Z = -18.0
STACK_X = -39.0                   # stack centre
STACK_Z = -4.0                    # ESC underside
VTX_X = -70.0
RX_X = -82.0

# --------------------------------------------------------------- pylons
# Root stations on the fuselage flank; front pair sweeps out-and-forward,
# rear pair out-and-aft.
PYLON_ROOT_X = 25.0
PYLON_ROOT_Z = 16.0               # == MOTOR_PAD_Z: pylons are flat-topped
PYLON_CHORD_ROOT = 30.0           # streamwise width at the root
PYLON_CHORD_TIP = 26.0            # where it meets the nacelle
PYLON_DEPTH = 17.0                # vertical; this is what carries bending

# Belly profile: (z below the flat top, plan inset). Lofting the plan shape
# downward with a growing inset rounds the underside of strut and nacelle
# together, and guarantees the section only ever shrinks going up in the print.
PYLON_BELLY = ((0.0, 0.0), (4.0, 0.5), (8.0, 1.6), (11.5, 3.4),
               (14.5, 5.8), (17.0, 9.0))

PYLON_FLANGE_W = 30.0             # root flange, bolts to a flat land
PYLON_FLANGE_H = 24.0             # tall, because the bending is vertical
PYLON_FLANGE_T = 11.0             # thick, because the saddle cut eats most of it
PYLON_FLANGE_OUT = 2.0            # how far it stands proud of the root plane
RIB_T = 9.0                       # backing rib depth; bounded by the bays
SADDLE_GAP = 0.6
LIP_BITE = 0.9                    # how far the canopy lip merges into the wall                  # clearance on every saddled mating face
PYLON_FLANGE_BOLT = 8.0           # +/- in both axes -> 16 mm couple arm
MOTOR_PAD_T = 4.0                 # material left under the motor -> M3x8
MOTOR_POCKET_D = 26.0             # belly hollow under the nacelle
WIRE_CH_W = 6.0                   # motor-wire tunnel bore
WIRE_TUNNEL_Z = 8.0               # below the pad plane

NACELLE_L = 46.0                  # pod length
NACELLE_D = 30.0                  # pod max width, just over the 28 mm bell
NACELLE_NOSE = 14.0               # rounded leading portion


# --------------------------------------------------------------- tail fin
FIN_X = -104.0                    # root leading edge
FIN_LEN = 46.0
FIN_H = 44.0
FIN_T = 5.0
FIN_FOOT_W = 26.0                 # saddle foot straddling the tail cone
FIN_BOLT_SP = 26.0
FIN_SWEEP = 26.0                  # LE sweep, mm aft over the height
ANT_BORE = 6.0                    # VTX antenna shaft, up the fin

# --------------------------------------------------------------- cooling
# Enclosed electronics cook. Annular nose inlet, ducted past the stack, out
# through the tail. Without this the ESC and VTX will thermal-throttle.
INLET_D = 15.0                    # nose aperture; at X=99 the OML radius is
INLET_X = 99.0                    # only 12.5, so 22 mm would remove the nose
EXIT_D = 26.0
GILL_X = -66.0                    # side gills over the stack
GILL_W, GILL_H, GILL_N = 3.5, 14.0, 4

# --------------------------------------------------------------- print
NEPTUNE4_BED = (225.0, 225.0, 265.0)
PETG_RHO = 1.27e-3
SHELL_FILL = 0.85                 # thin shells print nearly solid
PYLON_FILL = 0.50                 # 4 walls + light infill; stress is low
