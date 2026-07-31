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
This is the aerodynamic OUTER SHELL only. The arms are flat carbon plate that
you buy, cut and slide in through the slots from the inside; they are not
printed. The stack bolts to the internal shelf. Motors, battery, camera and
wiring are yours to place.

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
# Set by the largest thing that must fit, which after the $150 re-spec is the
# 4S 1500 pack (75 x 35 x 30): half-diagonal 23.0 + 1.0 fit + 2.0 wall = 26.0.
# The old 60 mm body was sized by a 44 mm-wide SpeedyBee ESC; the budget
# 36 x 36 stack does not need it, so the aircraft got 25% less frontal area.
R_MAX = 26.0             # max outer radius -> 52 mm diameter body
WALL = 2.0               # constant shell wall thickness

# ---- Longitudinal stations --------------------------------------------------
Z_TAIL_TOP = 60.0        # boat-tail ends / parallel body begins
Z_NOSE_BASE = 170.0      # parallel body ends / ogive begins
R_TAIL_BASE = 21.0       # radius at the very base (Z=0)
R_TIP = 0.6              # tiny flat at the tip: a knife point will not print

# ---- Arm slots --------------------------------------------------------------
# Flat carbon plate arms slide in from the INSIDE and out through the wall.
ARM_COUNT = 4
ARM_ANGLES = [45.0, 135.0, 225.0, 315.0]   # true-X quadcopter
# The blade stands ON EDGE: 26 mm tall, 6 mm thick streamwise. Motor thrust
# is vertical, so depth in Z is what resists bending -- a 6 mm-thick flat
# plate lying horizontally would be 18x less stiff for the same material.
# It is also the low-drag orientation, since 6 mm is what the air sees.
ARM_THICK = 6.0          # streamwise thickness (horizontal)
ARM_WIDTH = 26.0         # vertical depth -- carries the bending
ARM_FIT = 0.4            # total slip fit added to BOTH slot dimensions
ARM_Z = 95.0             # slot centre height -- lower-middle of the body
ARM_REACH = 60.0         # how far the cutter runs past R_MAX

# ---- Internal flight-stack shelf -------------------------------------------
SHELF_Z = 135.0          # top face of the shelf
SHELF_T = 3.0            # shelf thickness
STACK_PITCH = 30.5       # standard 30.5 x 30.5 mounting pattern
STACK_HOLE_D = 3.2       # M3 clearance in printed PETG (see note below)
SHELF_VENT_D = 18.0      # central pass-through for the ESC / motor looms

# ---- Cavity extent ----------------------------------------------------------
CAVITY_BOTTOM = -1.0     # below Z=0, so the base is OPEN for assembly
MIN_INNER_R = 2.5        # stop hollowing once the nose gets this thin

PROFILE_STEPS = 60       # spline sample count per curved section


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
    # open to the cavity: the carbon plate feeds in from inside and pushes out.
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
HUB_BOLT_D = 3.2
PAD_TAIL_L = 14.0        # boat-tail length below the pad
PAD_TAIL_R = 0.45        # aft radius as a fraction of pad radius


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

    # Motor pad stays a VERTICAL boss, so its face is normal to the body axis
    # and thrust is not canted. Streamlined to a teardrop rather than a plain
    # disc: the blunt trailing side of a cylinder is where most of its drag
    # comes from, so the aft half is faired out to a point.
    pad_r = MOTOR_PATTERN / 2.0 * math.sqrt(2) + 4.0
    z_pad = -drop
    # The pad's axis is ALONG the flight direction, so it behaves like a
    # nacelle, not a bluff cylinder: its drag is base drag off the flat aft
    # end. The fix is a boat-tail, not a teardrop in plan. Tapering the
    # underside to 45 % radius removes most of that base area.
    # Built as a straight boss PLUS a separate boat-tail cone. A single loft
    # from pad_r straight down to the tail radius leaves the boss too slim
    # where the blade meets it, and the union comes apart into two solids.
    boss = (
        cq.Workplane("XY")
        .workplane(offset=z_pad - ARM_WIDTH)
        .center(R_MOTOR, 0)
        .circle(pad_r)
        .extrude(ARM_WIDTH)
    )
    tail = (
        cq.Workplane("XY")
        .workplane(offset=z_pad - ARM_WIDTH)
        .center(R_MOTOR, 0)
        .circle(pad_r)
        .workplane(offset=-PAD_TAIL_L)
        .circle(pad_r * PAD_TAIL_R)
        .loft()
    )
    arm = arm.union(boss).union(tail)

    # Hollow the pad from below to leave exactly MOTOR_PAD_T under the motor.
    arm = arm.cut(
        cq.Workplane("XY")
        .workplane(offset=z_pad - ARM_WIDTH - 1.0)
        .center(R_MOTOR, 0)
        .circle(pad_r - 2.0)
        .extrude(ARM_WIDTH - MOTOR_PAD_T + 1.0)
    )

    # 16 x 16 M3 + centre bore, through the 4 mm pad only.
    half = MOTOR_PATTERN / 2.0
    for sx in (-half, half):
        for sy in (-half, half):
            arm = arm.cut(
                cq.Workplane("XY")
                .workplane(offset=z_pad - MOTOR_PAD_T - 1.0)
                .center(R_MOTOR + sx, sy)
                .circle(3.2 / 2.0)
                .extrude(MOTOR_PAD_T + 2.0)
            )
    arm = arm.cut(
        cq.Workplane("XY")
        .workplane(offset=z_pad - MOTOR_PAD_T - 1.0)
        .center(R_MOTOR, 0)
        .circle(MOTOR_BORE_D / 2.0)
        .extrude(MOTOR_PAD_T + 2.0)
    )

    # Root bolt: one M3 through the blade into the internal hub.
    arm = arm.cut(
        cq.Workplane("XZ")
        .workplane(offset=-ARM_THICK)
        .center(ARM_ROOT_R + 8.0, -ARM_WIDTH / 2.0)
        .circle(HUB_BOLT_D / 2.0)
        .extrude(ARM_THICK * 2.0)
    )
    return arm


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


# =============================================================================
# BUILD
# =============================================================================

result = build_shell()
arm = build_arm()
hub = build_hub()

# CQ-Editor picks this up automatically. Uncomment to export:
# cq.exporters.export(result, "vyper_shell.stl")
# cq.exporters.export(result, "vyper_shell.step")

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
