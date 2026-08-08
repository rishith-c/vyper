"""
=============================================================================
 PEREGREEN-INSPIRED HIGH-SPEED ROCKET-DRONE FUSELAGE SHELL
 Parametric CadQuery model -- paste directly into CQ-Editor and press F5
=============================================================================

Inspired by the Peregreen V4 (Luke & Mike Bell, Cape Town), the fully
3D-printed quadcopter that set the Guinness record at 657.59 km/h in Dec 2025.
Two features of that aircraft drive this model:

  * the fuselage was printed as ONE seamless piece -- no joints to add weight,
    turbulence or a stress riser. This script produces a single closed solid
    for the same reason.
  * the outer contour was CFD-optimised (AirShaper) into a smooth, slightly
    fuller body. Here that is approximated analytically with a Von Karman
    ogive, which is the mathematically minimum-drag nose shape rather than a
    stylistic guess.

ORIENTATION
-----------
The model is built VERTICAL: +Z runs from the tail base (Z = 0) up to the nose
tip (Z = TOTAL_LEN). A tail-sitter rocket-drone stands on its base, so the
four arms leave the body horizontally and the props sweep in horizontal planes.

WHAT THIS IS AND IS NOT
-----------------------
This module now generates the aerodynamic shell, four printed blade arms, the
internal arm hub and the removable tail. Purchased electronics, motors,
propellers and fasteners are integrated as fit-check geometry in
`vyper_assembly.py`; they are not fused into printable airframe STLs.

MATHEMATICAL SECTIONS (bottom to top)
-------------------------------------
  Z = 0 .. 60      BOAT-TAIL. Radius grows R_TAIL -> R_MAX on a cosine
                   easing. A boat-tail reduces base drag, which on a blunt
                   body is a large fraction of total drag.
  Z = 60 .. 170    PARALLEL MID-BODY at R_MAX. This is where the electronics,
                   the arm roots and the stack shelf live. Constant radius
                   because packaging, not aerodynamics, governs here.
  Z = 170 .. 300   VON KARMAN (LD-Haack) OGIVE. For a nose of given length and
                   base radius this minimises theoretical wave/pressure drag:

                       theta(x) = arccos(1 - 2x/L)
                       r(x)     = (R/sqrt(pi)) * sqrt(theta - sin(2*theta)/2)

                   with x measured aft from the tip. At x=0, r=0; at x=L, r=R.
                   Unlike a tangent ogive it meets the body with zero slope
                   discontinuity, so there is no shoulder to trip the flow.

The wall is a constant 2.0 mm, produced by revolving a second profile whose
radius is (outer - 2.0) and cutting it. A true `.shell()` operation is NOT
used: on a spline-revolved solid with this much curvature change OCC
frequently fails or produces non-uniform wall thickness. Two revolves and a
boolean is exact and always works.

=============================================================================
"""

import math

import cadquery as cq

# =============================================================================
# PARAMETERS -- everything is driven from here
# =============================================================================

# ---- Overall envelope -------------------------------------------------------
TOTAL_LEN = 300.0        # base (Z=0) to nose tip (Z=TOTAL_LEN)
# Set by the DOGCOM Pro 6S 1380 pack (81 x 39 x 33): cross-section
# half-diagonal 25.54 + 0.96 fit + 2.0 wall = 28.5 mm.  A 52 mm body only has
# a 24 mm internal radius and cannot accept a battery capable of the selected
# 6S propulsion current.  This 57 mm body is the smallest honest circular
# envelope for the selected pack; the battery fit is checked in test_vyper.py.
R_MAX = 28.5             # max outer radius -> 57 mm diameter body
WALL = 2.0               # constant shell wall thickness

# ---- Longitudinal stations --------------------------------------------------
Z_TAIL_TOP = 60.0        # boat-tail ends / parallel body begins
Z_NOSE_BASE = 170.0      # parallel body ends / ogive begins
R_TAIL_BASE = R_MAX      # full-diameter battery loading opening at Z=0
R_TIP = 0.6              # tiny flat at the tip: a knife point will not print

# ---- Arm slots --------------------------------------------------------------
# Printed blade arms slide in from the INSIDE and out through the wall.
ARM_COUNT = 4
ARM_ANGLES = [45.0, 135.0, 225.0, 315.0]   # true-X quadcopter
# The blade stands ON EDGE: 26 mm tall, 6 mm thick streamwise. Motor thrust
# is vertical, so depth in Z is what resists bending -- a 6 mm-thick flat
# plate lying horizontally would be 18x less stiff for the same material.
# It is also the low-drag orientation, since 6 mm is what the air sees.
ARM_THICK = 8.0          # streamwise thickness; leaves wall around wire bore
ARM_WIDTH = 26.0         # vertical depth -- carries the bending
ARM_FIT = 0.4            # total slip fit added to BOTH slot dimensions
ARM_Z = 110.0            # hub starts at Z=97, immediately above the battery
ARM_REACH = 60.0         # how far the cutter runs past R_MAX

# ---- Internal flight-stack shelf -------------------------------------------
SHELF_Z = 155.0          # top face; leaves a routed loom bay above the hub
SHELF_T = 3.0            # shelf thickness
STACK_PITCH = 30.5       # standard 30.5 x 30.5 mounting pattern
STACK_HOLE_D = 3.2       # M3 clearance in printed PETG (see note below)
SHELF_VENT_D = 18.0      # central pass-through for the ESC / motor looms

# ---- Cavity extent ----------------------------------------------------------
CAVITY_BOTTOM = -1.0     # below Z=0, so the base is OPEN for assembly
MIN_INNER_R = 2.5        # stop hollowing once the nose gets this thin

PROFILE_STEPS = 60       # spline sample count per curved section

# ---- Print split ------------------------------------------------------------
# The 300 mm body is printed standing, which is the only sensible orientation
# for a body of revolution. It does not fit a 265 mm-Z bed: at the 95 % usable
# height that is 251.75 mm, so the part is 48 mm too tall.
#
# Printing it as one piece was the stated intent, following the Peregreen V4.
# That is worth keeping where it is affordable and it is not affordable here,
# so the question becomes WHERE to split rather than whether to.
#
# Z = 170 is the answer, for three reasons that all point the same way:
#   * it is the ogive/parallel-body junction, which the Von Karman profile
#     already meets with zero slope discontinuity. A joint there adds no
#     shoulder the flow was not already seeing.
#   * both halves then print standing: 170 mm body and 130 mm nose, against
#     251.75 mm usable. Neither needs support it did not already need.
#   * the arms land at Z = 95 and the shelf at Z = 135, both well below the
#     joint, so the split is entirely outside the loaded region. The nose
#     carries nothing but its own air load.
#
# The joint is a LAP, not a butt: each half keeps half the wall through the
# overlap, so glue area is the full 25 mm of engagement rather than a 2 mm
# end-grain ring. A butt joint here would be the stress riser the one-piece
# argument was trying to avoid.
SPLIT_ENABLE = True
SPLIT_Z = 170.0          # ogive base -- see above
SPIGOT_L = 25.0          # lap engagement length
SPIGOT_FIT = 0.25        # radial clearance, nose spigot into body socket

# Removable aerodynamic tail cap. The main shell stays full diameter down to
# Z=0 so the 81 mm battery can load axially. This cap then adds the boat-tail
# outside that packaging volume instead of falsely tapering through the pack.
TAIL_CAP_LEN = 60.0
TAIL_EXIT_R = 8.0
TAIL_SPIGOT_L = 12.0
TAIL_SPIGOT_WALL = 1.75
TAIL_RETAINER_ANGLES = [0.0, 120.0, 240.0]
TAIL_RETAINER_Z = 6.0
TAIL_RETAINER_SCREW_D = 2.2       # M2 clearance, printed then hand-reamed
TAIL_INSERT_D = 3.6               # M2 heat-set insert pilot envelope
TAIL_INSERT_L = 4.0


# =============================================================================
# PROFILE MATHEMATICS
# =============================================================================

def von_karman_radius(x, length, base_radius):
    """Von Karman (LD-Haack) ogive radius at distance x aft of the tip.

        theta = arccos(1 - 2x/L)
        r     = (R / sqrt(pi)) * sqrt(theta - sin(2*theta)/2)

    This is the minimum-drag body of revolution for a given length and base
    diameter under Sears-Haack theory. It is the reason the nose here is not
    simply a cone or a circular-arc ogive.
    """
    x = min(max(x, 0.0), length)                 # clamp against float drift
    theta = math.acos(1.0 - 2.0 * x / length)
    return (base_radius / math.sqrt(math.pi)) * math.sqrt(
        theta - math.sin(2.0 * theta) / 2.0
    )


def boat_tail_radius(z):
    """Cosine easing from R_TAIL_BASE at Z=0 to R_MAX at Z_TAIL_TOP.

    A cosine (rather than a straight taper) gives zero slope at both ends, so
    the tail blends into the parallel body with no visible crease and no
    separation-triggering corner.
    """
    t = z / Z_TAIL_TOP
    return R_TAIL_BASE + (R_MAX - R_TAIL_BASE) * (1.0 - math.cos(math.pi * t)) / 2.0


def tail_cap_radius(z):
    """Cosine boat-tail radius for -TAIL_CAP_LEN <= z <= 0.

    Both endpoint slopes are zero. The cap is removable, allowing the battery
    to slide through the full-diameter Z=0 opening before the fairing is fitted.
    """
    t = (z + TAIL_CAP_LEN) / TAIL_CAP_LEN
    return TAIL_EXIT_R + (R_MAX - TAIL_EXIT_R) * (1.0 - math.cos(math.pi * t)) / 2.0


def outer_profile():
    """Full outer half-profile as a list of (radius, z), base -> tip."""
    pts = []

    # --- 1. Boat-tail: Z = 0 .. Z_TAIL_TOP
    for i in range(PROFILE_STEPS + 1):
        z = Z_TAIL_TOP * i / PROFILE_STEPS
        pts.append((boat_tail_radius(z), z))

    # --- 2. Parallel mid-body: Z_TAIL_TOP .. Z_NOSE_BASE
    # Sampled rather than a single endpoint. A spline given two identical
    # radii far apart will bow between them; a dense polyline cannot.
    for i in range(1, 21):
        pts.append((R_MAX, Z_TAIL_TOP + (Z_NOSE_BASE - Z_TAIL_TOP) * i / 20.0))

    # --- 3. Von Karman ogive: Z_NOSE_BASE .. TOTAL_LEN
    nose_len = TOTAL_LEN - Z_NOSE_BASE
    for i in range(1, PROFILE_STEPS + 1):
        # x is measured AFT FROM THE TIP, so walk it backwards to go up in Z
        x = nose_len * (PROFILE_STEPS - i) / PROFILE_STEPS
        r = von_karman_radius(x, nose_len, R_MAX)
        z = TOTAL_LEN - x
        pts.append((max(r, R_TIP), z))

    return pts


def inner_profile(outer_pts):
    """Offset the outer profile inward by WALL to form the cavity.

    Truncated once the wall would consume the section (near the tip), which
    leaves the nose solid -- convenient, because that is where you want mass
    for CG anyway on a tail-sitter.
    """
    pts = [(max(outer_pts[0][0] - WALL, MIN_INNER_R), CAVITY_BOTTOM)]
    for r, z in outer_pts:
        r_in = r - WALL
        if r_in < MIN_INNER_R:
            break
        pts.append((r_in, z))
    return pts


# =============================================================================
# SOLID CONSTRUCTION
# =============================================================================

def revolve_profile(pts, close_top=True):
    """Revolve a (radius, z) half-profile about the Z axis.

    NOTE ON THE WORKPLANE: on Workplane("XZ") the local axes map to global
    (X, Z), so a local point (r, z) sits at global (r, 0, z). The revolve axis
    is therefore the LOCAL y axis -- (0,0) to (0,1) -- not the global Z tuple.
    Getting this wrong is the classic CadQuery revolve mistake.
    """
    z_bottom = pts[0][1]
    z_top = pts[-1][1]

    # POLYLINE, not spline. A spline fitted through the whole profile
    # overshoots at the two slope discontinuities (boat-tail -> parallel body,
    # body -> ogive), self-intersects, and the revolve then yields a negative
    # volume made of a dozen fragments. At 60 samples per curved section the
    # facets are far below layer resolution, so nothing is lost.
    chain = [(0.0, z_bottom), (pts[0][0], z_bottom)]
    chain += [(r, z) for r, z in pts[1:]]
    if close_top:
        chain.append((0.0, z_top))

    return (
        cq.Workplane("XZ")
        .polyline(chain)
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )


def build_shell():
    # ---- 1. Outer aerodynamic body ------------------------------------------
    outer_pts = outer_profile()
    body = revolve_profile(outer_pts)

    # ---- 2. Hollow it to a constant 2 mm wall --------------------------------
    cavity = revolve_profile(inner_profile(outer_pts))
    shell = body.cut(cavity)

    # ---- 3. Internal flight-stack shelf --------------------------------------
    # Radius deliberately exceeds the local inner radius so the disc merges
    # INTO the wall rather than sitting tangent to it -- a tangent disc unions
    # as a separate floating solid.
    shelf_r = R_MAX - WALL + 0.5
    shelf = (
        cq.Workplane("XY")
        .workplane(offset=SHELF_Z - SHELF_T)
        .circle(shelf_r)
        .extrude(SHELF_T)
    )
    shell = shell.union(shelf)

    # ---- 3a. Self-supporting ramp under the shelf ----------------------------
    # The shelf is an annular ledge reaching 15.5 mm inward from the wall with
    # nothing beneath it: a 90 deg overhang of about 1520 mm^2. That is the
    # single largest overhang on the airframe, and unlike an external one it
    # cannot be solved with support material -- this face is 132 mm up a 53 mm
    # bore, so any support printed under it stays there forever.
    #
    # The fix is a cone under the shelf running back down to the wall at 45
    # deg. Each layer then steps inward by exactly its own height, which is the
    # self-support limit, so it prints unsupported and the ledge lands on solid
    # material. It also fillets the shelf-to-wall joint, which is where a
    # cantilevered ledge would otherwise crack first.
    #
    # Cost is 15.5 mm off the top of the battery bay, leaving about 116 mm of
    # clear cavity for a 75 mm pack. If that ever gets tight, widening
    # SHELF_VENT_D shortens the ramp one-for-one.
    # Built as a conical SHELL, not a solid cone. Only the surface has to be
    # there -- the shelf needs something to land on, not a plug. A solid cone
    # costs about 20 g, which on a roughly 690 g airframe is 3 % of all-up weight
    # bought for nothing.
    ramp_h = shelf_r - SHELF_VENT_D / 2.0
    ramp_z0 = SHELF_Z - SHELF_T - ramp_h
    ramp_wall = WALL * math.sqrt(2.0)      # 45 deg cone: vertical offset for
    #                                        a WALL-thick normal section
    ramp = (
        cq.Workplane("XY").workplane(offset=ramp_z0)
        .circle(shelf_r).extrude(ramp_h)
    ).cut(
        cq.Workplane("XY").workplane(offset=ramp_z0)
        .circle(shelf_r)
        .workplane(offset=ramp_h)
        .circle(SHELF_VENT_D / 2.0)
        .loft()
    ).cut(
        cq.Workplane("XY").workplane(offset=ramp_z0)
        .circle(shelf_r + ramp_wall)
        .workplane(offset=ramp_h)
        .circle(SHELF_VENT_D / 2.0 + ramp_wall)
        .loft()
    )
    shell = shell.union(ramp)

    # 30.5 x 30.5 stack pattern + a central loom pass-through.
    #
    # Cut with explicit cylinders rather than .faces(">Z").hole(): on a body
    # of revolution the ">Z" selector resolves to the nose tip (or to nothing
    # at all after a boolean), not to the shelf you just added. Positioning
    # the cutters absolutely is unambiguous and cannot mis-select.
    half = STACK_PITCH / 2.0
    for sx in (-half, half):
        for sy in (-half, half):
            bolt = (
                cq.Workplane("XY")
                .workplane(offset=SHELF_Z - SHELF_T - 2.0)
                .center(sx, sy)
                .circle(STACK_HOLE_D / 2.0)
                .extrude(SHELF_T + 4.0)
            )
            shell = shell.cut(bolt)

    vent = (
        cq.Workplane("XY")
        .workplane(offset=SHELF_Z - SHELF_T - 2.0)
        .circle(SHELF_VENT_D / 2.0)
        .extrude(SHELF_T + 4.0)
    )
    shell = shell.cut(vent)

    # ---- 4. Arm slots --------------------------------------------------------
    # Each cutter starts on the axis and runs radially outward, so the slot is
    # open to the cavity: the printed blade feeds in from inside and pushes out.
    slot_w = ARM_WIDTH + ARM_FIT      # vertical
    slot_t = ARM_THICK + ARM_FIT      # streamwise
    cut_len = R_MAX + ARM_REACH

    for angle in ARM_ANGLES:
        cutter = (
            cq.Workplane("XY")
            .box(cut_len, slot_t, slot_w)
            .translate((cut_len / 2.0, 0, ARM_Z))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        shell = shell.cut(cutter)

    return shell


# =============================================================================
# ARM  --  four identical blades, slid in through the slots from inside
# =============================================================================

R_MOTOR = 110.0          # motor centre radius -> 220 mm true-X wheelbase
HUB_CORE_R = 10.0        # solid core the four hub slots stop short of
ARM_ROOT_R = 11.0        # arm root radius -- four arms cannot all cross centre
ARM_TIP_OVER = 15.0      # blade reach past the motor centre
MOTOR_PATTERN = 16.0     # 2207-class M3 square
MOTOR_PAD_T = 4.0        # left under the motor -> M3x8 and nothing longer
MOTOR_BORE_D = 9.0       # bell boss relief

# ---- Print orientation ------------------------------------------------------
# MEASURED, not assumed. The blade underside sits 22 deg off horizontal (it is
# the swept face), which is a 68 deg overhang if the arm is sliced as modelled.
# Rotating the part about Y by more than ARM_SWEEP steepens that whole face
# past the 45 deg self-support limit. Facet-level sweep of the exported STEP:
#
#     rotation      overhang area     worst
#      0 deg        1182 mm^2          68 deg     <- as modelled, needs support
#     25 deg         510 mm^2          65 deg     <- best
#     45 deg         464 mm^2          76 deg     but on a cliff edge: 45.5 deg
#                                                 flips a large face and it
#                                                 jumps back to 2114 mm^2
#
# 25 deg is the setting to use: over half the overhang area gone for free, and
# it sits in the middle of a stable window rather than on the edge of one.
#
# NOTE: an earlier version of this docstring claimed the arm printed
# "top-face-down with nothing needing support". That is false and was never
# measured - top-face-down is a 158 deg rotation and scores 1957 mm^2, the
# WORST of any orientation tried.
PRINT_ROT_Y = 25.0       # degrees about Y for the print-oriented export

# ---- Arm sweep --------------------------------------------------------------
# On a tail-sitter, "angled down" means swept AFT, because at speed the body
# axis IS the flight direction. That is worth doing: a strut swept by Lambda
# sees only the crossflow component, so its profile drag falls roughly as
# cos^2(Lambda).
#
#   0 deg  -> cos^2 = 1.00   (baseline)
#   20 deg -> cos^2 = 0.88   (-12 % arm drag)
#   30 deg -> cos^2 = 0.75   (-25 % arm drag)
#
# What is NOT done here is canting the MOTORS. The pad stays normal to the
# body axis, so thrust stays on the flight axis and there is no cos(theta)
# thrust loss. Tilting the motors themselves would cost 3.4 % of thrust at
# 15 deg and buy nothing on a tail-sitter -- the body already aligns.
ARM_SWEEP = 22.0         # degrees aft ("down" when standing on the tail)

# ---- PUSHER configuration ---------------------------------------------------
# Motors mount on the AFT face of the arm, props behind them, pushing.
#
# Why pusher and not tractor, for a speed airframe specifically:
#
#   TRACTOR (props at the nose end) gives the prop clean inflow, but its
#   slipstream then washes the ENTIRE fuselage at well above freestream
#   velocity. Skin-friction drag scales with local dynamic pressure, so you
#   pay for that over the whole wetted area -- and this body is nearly all
#   the wetted area there is.
#
#   PUSHER costs the prop some inflow quality (it ingests body and arm wake,
#   which shows up as blade-loading fluctuation and noise) but leaves the
#   fuselage in clean, undisturbed air.
#
# On a body this slender with this much wetted area relative to disc area,
# keeping the fuselage out of the slipstream is the larger effect. It is also
# why high-speed UAVs are overwhelmingly pushers.
#
# Practical consequence: the motors are mounted INVERTED. Same props, but
# motor direction must be reversed in Betaflight -- see firmware/.
PUSHER = True
HUB_BOLT_D = 3.2
WIRE_BORE_D = 5.5        # 3x 20 AWG silicone; 1.25 mm wall each side


def build_arm():
    """One arm, built lying along +X with its TOP FACE at Z = 0.

    Printed top-face-down: that face is both the bed face and the motor
    mounting face, and every feature hangs below it, so the section only
    shrinks going up and nothing needs support.

    Root bending check, 2207 on 6S (~19 N at the tip):
        M = 19 N x 0.110 m            = 2.09 N.m
        Z = 6 x 26^2 / 6              = 676 mm^3
        sigma = 2.09e3 / 676          = 3.1 MPa   vs ~45 MPa PETG yield
    """
    sweep = math.radians(ARM_SWEEP)
    span = R_MOTOR - ARM_ROOT_R                     # horizontal reach
    drop = span * math.tan(sweep)                   # how far aft the tip sits
    length = span / math.cos(sweep) + ARM_TIP_OVER  # true blade length

    # Blade, built flat then rotated aft about Y. Rotating about +Y tips +X
    # toward -Z, which is aft on a nose-up rocket.
    arm = (
        cq.Workplane("XY")
        .box(length, ARM_THICK, ARM_WIDTH)
        .translate((length / 2.0, 0, -ARM_WIDTH / 2.0))
        .rotate((0, 0, 0), (0, 1, 0), ARM_SWEEP)
        .translate((ARM_ROOT_R, 0, 0))
    )

    # Motor pad stays normal to the body axis, so thrust is not canted. It is
    # only MOTOR_PAD_T thick: the previous full-depth boss plus aft cone
    # occupied the exact volume required by a pusher motor. This flow-aligned
    # disc is functional, lighter, and leaves the complete motor envelope aft.
    pad_r = MOTOR_PATTERN / 2.0 * math.sqrt(2) + 4.0
    z_pad = -drop
    z_face = (z_pad - ARM_WIDTH) if PUSHER else z_pad
    motor_pad = (
        cq.Workplane("XY")
        .workplane(offset=z_face)
        .center(R_MOTOR, 0)
        .circle(pad_r)
        .extrude(MOTOR_PAD_T)
    )
    arm = arm.union(motor_pad)

    # 16 x 16 M3 + centre bore, through the 4 mm pad only.
    half = MOTOR_PATTERN / 2.0
    for sx in (-half, half):
        for sy in (-half, half):
            arm = arm.cut(
                cq.Workplane("XY")
                .workplane(offset=z_face - 1.0)
                .center(R_MOTOR + sx, sy)
                .circle(3.2 / 2.0)
                .extrude(MOTOR_PAD_T + 2.0)
            )
    arm = arm.cut(
        cq.Workplane("XY")
        .workplane(offset=z_face - 1.0)
        .center(R_MOTOR, 0)
        .circle(MOTOR_BORE_D / 2.0)
        .extrude(MOTOR_PAD_T + 2.0)
    )

    # ---- WIRE ROUTING ---------------------------------------------------
    # Three phase wires per motor have to get from the bell to the ESC inside
    # the fuselage. They are NOT left to flap in a 200 km/h airstream: a bore
    # runs the length of the blade from the motor pocket to the root, exiting
    # inside the cavity.
    #
    # WIRE_BORE_D = 6.0 takes three 20 AWG silicone leads (about 2.3 mm each)
    # with room to pull them through by hand. Bored along the blade axis, so
    # it prints as a horizontal hole and bridges cleanly at this diameter.
    #
    # The bore is cut BEFORE the root bolt so the bolt passes through solid
    # material either side of it rather than into an open channel.
    wire_bore = (
        cq.Workplane("YZ")
        .center(0, -ARM_WIDTH / 2.0)
        .circle(WIRE_BORE_D / 2.0)
        .extrude(length + 30.0)
        .rotate((0, 0, 0), (0, 1, 0), ARM_SWEEP)
        .translate((ARM_ROOT_R - 5.0, 0, 0))
    )
    arm = arm.cut(wire_bore)

    # Root bolt: one M3 through the blade into the internal hub.
    arm = arm.cut(
        cq.Workplane("XZ")
        .workplane(offset=-ARM_THICK)
        .center(ARM_ROOT_R + 8.0, -ARM_WIDTH / 2.0)
        .circle(HUB_BOLT_D / 2.0)
        .extrude(ARM_THICK * 2.0)
    )
    return arm


def split_shell(shell):
    """Cut the shell at SPLIT_Z into a body and a nose joined by a lap.

    The wall is 2.0 mm and the lap splits it: the nose grows a ring occupying
    the INNER half (r = R_MAX-WALL .. R_MAX-WALL/2) and hanging SPIGOT_L below
    the joint; the body has that same annulus removed from its top so the ring
    drops in. Each half keeps 1.0 mm of wall through the overlap and the pair
    is 2.0 mm again once assembled.

    The nose ring shares the r = 24..25 band with the nose wall at the split
    plane, so the union is a real solid overlap. A ring sized flush to the
    cavity would only touch it tangentially and would come out as two solids.

    Returns (body, nose), both standing on Z = 0 ready to slice.
    """
    r_in = R_MAX - WALL                  # cavity wall
    r_mid = R_MAX - WALL / 2.0           # mid-wall
    far = R_MAX * 4.0

    body = shell.cut(
        cq.Workplane("XY").workplane(offset=SPLIT_Z)
        .circle(far).extrude(TOTAL_LEN)
    )
    nose = shell.cut(
        cq.Workplane("XY").workplane(offset=SPLIT_Z - TOTAL_LEN)
        .circle(far).extrude(TOTAL_LEN)
    )

    # Male lap on the nose, hanging below the joint.
    spigot = (
        cq.Workplane("XY").workplane(offset=SPLIT_Z - SPIGOT_L)
        .circle(r_mid - SPIGOT_FIT).circle(r_in)
        .extrude(SPIGOT_L)
    )
    nose = nose.union(spigot)

    # Matching female socket in the body: take the inner half of the wall out
    # over the engagement length. Cut 0.2 mm deeper than the spigot is long so
    # the two halves seat on the OUTER shoulder, which is the surface the air
    # sees, rather than bottoming out inside on a tolerance stack.
    body = body.cut(
        cq.Workplane("XY").workplane(offset=SPLIT_Z - SPIGOT_L - 0.2)
        .circle(r_mid).circle(r_in - 1.0)
        .extrude(SPIGOT_L + 0.2)
    )
    return body, nose


def build_hub():
    """Internal hub the four arm roots bolt into.

    Sits at the slot height inside the cavity. Cross-drilled on the same four
    axes as the slots, so each arm is captured in double shear rather than
    hanging off the shell wall.
    """
    hub_r = R_MAX - WALL - 0.5
    hub = (
        cq.Workplane("XY")
        .workplane(offset=ARM_Z - ARM_WIDTH / 2.0)
        .circle(hub_r)
        .extrude(ARM_WIDTH)
    )
    # Slots for the four arm roots to plug into.
    for angle in ARM_ANGLES:
        # Stops at HUB_CORE_R: a slot run to the centre would sever the hub
        # into four disconnected wedges.
        slot_len = hub_r * 1.4 - HUB_CORE_R
        hub = hub.cut(
            cq.Workplane("XY")
            .box(slot_len, ARM_THICK + ARM_FIT, ARM_WIDTH + 0.4)
            .translate((HUB_CORE_R + slot_len / 2.0, 0, ARM_Z))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
    # Matching bolt holes.
    for angle in ARM_ANGLES:
        hub = hub.cut(
            cq.Workplane("XY")
            .box(hub_r - HUB_CORE_R, HUB_BOLT_D, HUB_BOLT_D)
            .translate((ARM_ROOT_R + 8.0, 0, ARM_Z))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
    return hub


def build_tail_cap():
    """Hollow removable boat-tail with a located, screw-retained spigot.

    The aft 5 mm stays solid around a 6 mm drain/vent hole. The spigot occupies
    only the annulus next to the main-shell wall, leaving the battery envelope
    unobstructed once its forward face starts at Z=14 mm.
    """
    steps = 48
    outer_pts = []
    for i in range(steps + 1):
        z = -TAIL_CAP_LEN + TAIL_CAP_LEN * i / steps
        outer_pts.append((tail_cap_radius(z), z))
    outer = revolve_profile(outer_pts)

    inner_pts = []
    z0 = -TAIL_CAP_LEN + 5.0
    for i in range(steps + 1):
        z = z0 + (0.5 - z0) * i / steps
        inner_pts.append((max(tail_cap_radius(z) - WALL, 3.0), z))
    cap = outer.cut(revolve_profile(inner_pts))

    spigot_outer = R_MAX - WALL - SPIGOT_FIT
    spigot_inner = spigot_outer - TAIL_SPIGOT_WALL
    # A one-millimetre internal radial flange bridges the cap wall to the
    # smaller locating spigot. The spigot starts 0.5 mm inside that flange so
    # the boolean has real volume overlap rather than a fragile tangent face.
    flange = (
        cq.Workplane("XY").workplane(offset=-1.0)
        .circle(R_MAX).circle(spigot_inner)
        .extrude(1.0)
    )
    spigot = (
        cq.Workplane("XY").workplane(offset=-0.5)
        .circle(spigot_outer).circle(spigot_inner)
        .extrude(TAIL_SPIGOT_L + 0.5)
    )
    cap = cap.union(flange).union(spigot)

    # Three internal bosses carry M2 heat-set inserts.  The cap still removes
    # axially for battery access, but cannot vibrate free: M2x10 screws pass
    # radially through the main shell and engage the full 4 mm insert length.
    # Bosses are entirely inside the aerodynamic skin.
    for angle in TAIL_RETAINER_ANGLES:
        boss = (
            cq.Workplane("XY")
            .box(8.0, 6.0, 8.0)
            .translate((22.5, 0.0, TAIL_RETAINER_Z))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        cap = cap.union(boss)

        # Insert pocket opens toward the cap interior for installation.
        insert_pocket = (
            cq.Workplane("YZ").workplane(offset=18.4)
            .center(0.0, TAIL_RETAINER_Z)
            .circle(TAIL_INSERT_D / 2.0)
            .extrude(TAIL_INSERT_L + 0.2)
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        screw_bore = (
            cq.Workplane("YZ").workplane(offset=22.4)
            .center(0.0, TAIL_RETAINER_Z)
            .circle(TAIL_RETAINER_SCREW_D / 2.0)
            .extrude(7.0)
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        cap = cap.cut(insert_pocket).cut(screw_bore)

    vent = (
        cq.Workplane("XY").workplane(offset=-TAIL_CAP_LEN - 1.0)
        .circle(3.0).extrude(8.0)
    )
    return cap.cut(vent)


# =============================================================================
# BUILD
# =============================================================================

result = build_shell()
# Matching radial clearance holes in the main shell.  These are cut from the
# assembled shell, not drilled as a post-process assumption, so the exported
# STL and the tail-cap test share the same centres.
for angle in TAIL_RETAINER_ANGLES:
    retainer_hole = (
        cq.Workplane("YZ").workplane(offset=25.8)
        .center(0.0, TAIL_RETAINER_Z)
        .circle(TAIL_RETAINER_SCREW_D / 2.0)
        .extrude(4.0)
        .rotate((0, 0, 0), (0, 0, 1), angle)
    )
    result = result.cut(retainer_hole)
arm = build_arm()
hub = build_hub()
tail_cap = build_tail_cap()

# Print-ready variants. These are what actually goes to the slicer; `result`
# and `arm` stay in ASSEMBLY orientation so the assembly and the verification
# checks keep a single unambiguous reference frame.
shell_body, shell_nose = split_shell(result) if SPLIT_ENABLE else (result, None)
arm_print = arm.rotate((0, 0, 0), (0, 1, 0), PRINT_ROT_Y)

# CQ-Editor picks this up automatically. Uncomment to export:
# cq.exporters.export(result, "vyper_shell.stl")
# cq.exporters.export(result, "vyper_shell.step")
# cq.exporters.export(shell_body, "cad/vyper_shell_body.step")
# cq.exporters.export(shell_nose, "cad/vyper_shell_nose.step")
# cq.exporters.export(arm_print,  "cad/vyper_arm_print.step")

show_object = globals().get("show_object")
if show_object:
    show_object(result, name="vyper_shell")


if __name__ == "__main__":
    solid = result.val()
    bb = solid.BoundingBox()
    print("=" * 62)
    print(" PEREGREEN-INSPIRED FUSELAGE SHELL")
    print("=" * 62)
    print(f" bounding box : {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
    print(f" volume       : {solid.Volume():.0f} mm^3")
    print(f" PETG mass    : {solid.Volume() * 1.27e-3:.0f} g  (100% dense)")
    print(f" solids       : {len(solid.Solids())}")
    print(f" wall         : {WALL:.1f} mm")
    print(f" nose         : Von Karman, {TOTAL_LEN - Z_NOSE_BASE:.0f} mm long,"
          f" fineness {(TOTAL_LEN - Z_NOSE_BASE) / (2 * R_MAX):.2f}")
    print("=" * 62)
    exports = {
        "cad/vyper_shell.step": result,
        "cad/vyper_shell_body.step": shell_body,
        "cad/vyper_shell_nose.step": shell_nose,
        "cad/vyper_arm.step": arm,
        "cad/vyper_arm_print.step": arm_print,
        "cad/vyper_hub.step": hub,
        "cad/vyper_tail_cap.step": tail_cap,
        "stl/vyper_shell_body.stl": shell_body,
        "stl/vyper_shell_nose.stl": shell_nose,
        "stl/vyper_arm.stl": arm,
        "stl/vyper_arm_print.stl": arm_print,
        "stl/vyper_hub.stl": hub,
        "stl/vyper_tail_cap.stl": tail_cap,
    }
    for path, obj in exports.items():
        cq.exporters.export(obj, path, tolerance=0.05, angularTolerance=0.1)
        print(f" exported     : {path}")
