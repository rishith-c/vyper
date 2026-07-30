"""VYPER-5F fuselage shells. All four derive from the one mould line in body.py.

SPLIT STRATEGY
--------------
Three cuts, each chosen so the resulting part prints with no supports:

  nose cone   X > +68     prints OPEN END DOWN -- a dome, section shrinks all
                          the way up to the tip
  main body   +68..-92    split horizontally at Z = +13 into a structural
                          lower shell and a lid; both print CUT FACE DOWN, so
                          each is a half-tube whose section shrinks upward
  tail cone   X < -92     prints OPEN END DOWN, same as the nose
  fin         separate    because a fin moulded into the tail cone would be a
                          horizontal plate hanging in mid-air

The canopy registers on its four M3 alone -- at Y = +-24 those bolts pass
through the shell wall, which is enough location for a lid. An interference
lip was tried first and is not worth it: built from the exact cavity it is
only tangent to the wall and exports as two floating arcs, and grown enough to
merge it then fouls the lid by the same amount.

The canopy parting is at Z = +13, not at the waterline. Two reasons: it keeps
the pylon roots (Z = +16 on the shoulder, with their backing ribs) inside one
continuous structural shell instead of straddling a bolted joint, and it makes
the lid a lid rather than half the airframe.

BATTERY
-------
The 76 x 38 x 31 pack drops in from above onto a floor at Z = -18 and the
canopy closes on top of it at Z = +13. 31 mm of bay for a 31 mm pack: the lid
IS the battery retainer, so there is no strap and no strap drag.

COOLING IS NOT OPTIONAL
-----------------------
A sealed fuselage will cook a 55 A ESC and an analog VTX. Air comes in through
the annular gap around the camera in the nose, runs the length of the cavity
over the stack, and leaves through the tail aperture, with side gills over the
stack as the local exit. If you close these up the ESC will thermal-throttle.
"""

from build123d import Box, Cylinder, Pos, RectangleRounded, Rot, extrude

import body
import components as C
import vy_params as P


def despeck(part, min_vol=1.0):
    """Drop sub-1 mm^3 boolean slivers.

    Cutting the battery envelope (whose top lands exactly on the Z=13 canopy
    split) leaves a pair of 0.5 mm specks on the parting edge. They are
    numerically zero volume but they export as extra shells and would slice as
    floating specks. Anything real is orders of magnitude bigger, so the
    one-solid check in verify.py still has teeth.
    """
    from build123d import Compound

    keep = [x for x in part.solids() if x.volume > min_vol]
    return keep[0] if len(keep) == 1 else Compound(keep)


def _shrink_marker(gap):
    # Cheap inward offset of the cavity: reuse the revolve with reduced radii.
    stations = []
    for x, r in P.FUSE_PROFILE:
        if not (-130.0 <= x <= 104.0):
            continue
        stations.append((x, max(r - P.FUSE_WALL - gap - 1.6, 0.8)))
    return body._revolved(stations)


# ------------------------------------------------------------------ nose cone
def nose_cone():
    part = body.shell() - body.aft_of(P.SPLIT_NOSE_X)

    # Camera bay: a socket the 19 x 19 body slides into from behind.
    cam = Pos(P.CAM_FACE_X, 0, 0) * C.camera(grow=C.FIT / 2)
    part -= cam
    # Aperture: the lens looks out, and the annular gap around it is the
    # cooling inlet.
    part -= Pos(P.INLET_X, 0, 0) * Rot(0, 90, 0) * Cylinder(P.INLET_D / 2, 40)

    # Two M3 into the main body's forward ring.
    for sy in (1, -1):
        part -= Pos(P.SPLIT_NOSE_X + 7, sy * 20, 0) * Rot(0, 90, 0) * Cylinder(
            P.M3_CLR / 2, 30
        )
    return despeck(part.clean())


# ------------------------------------------------------------------ tail cone
def tail_cone():
    part = body.shell() - body.fwd_of(P.SPLIT_TAIL_X)
    # Exit aperture -- the other end of the cooling duct.
    part -= Pos(P.FUSE_TAIL_X + 6, 0, 0) * Rot(0, 90, 0) * Cylinder(
        P.EXIT_D / 2, 40
    )
    # Fin bolts, tapped up into the cone from inside.
    for sx in (-1, 1):
        part -= Pos(P.FIN_X - P.FIN_LEN / 2 + sx * P.FIN_BOLT_SP / 2, 0, 0) \
            * Cylinder(P.M3_TAP / 2, 60)
    for sy in (1, -1):
        part -= Pos(P.SPLIT_TAIL_X - 7, sy * 14, 0) * Rot(0, 90, 0) * Cylinder(
            P.M3_CLR / 2, 30
        )
    return despeck(part.clean())


# ------------------------------------------------------------------ main body
def _main_shell():
    return (
        body.shell()
        - body.fwd_of(P.SPLIT_NOSE_X)
        - body.aft_of(P.SPLIT_TAIL_X)
    )


def _pylon_ribs():
    """Backing ribs behind each pylon flange, carrying the four M3."""
    ribs = None
    for ang in P.ARM_ANGLES:
        rx, ry, rz = body.pylon_root(ang)
        mx, my, _ = body.motor_pos(ang)
        import math

        ux = (rx - mx) / math.hypot(rx - mx, ry - my)
        uy = (ry - my) / math.hypot(rx - mx, ry - my)
        yaw = math.degrees(math.atan2(uy, ux))
        # Only P.RIB_T deep. The battery bay (+-19 in Y) and the stack bay
        # (+-22) both pass right through the pylon root station, so a rib that
        # reaches any further inboard collides with the electronics.
        blk = (
            Pos(rx + ux * P.RIB_T / 2, ry + uy * P.RIB_T / 2,
                rz - P.PYLON_FLANGE_H / 2)
            * Rot(0, 0, yaw)
            * Box(P.RIB_T, P.PYLON_FLANGE_W + 4, P.PYLON_FLANGE_H)
        )
        ribs = blk if ribs is None else ribs + blk
    return ribs


def _pylon_bolt_holes():
    import math

    holes = None
    for ang in P.ARM_ANGLES:
        rx, ry, rz = body.pylon_root(ang)
        mx, my, _ = body.motor_pos(ang)
        d = math.hypot(rx - mx, ry - my)
        ux, uy = (rx - mx) / d, (ry - my) / d
        yaw = math.degrees(math.atan2(uy, ux))
        b = P.PYLON_FLANGE_BOLT
        for sv in (-b, b):
            for sz in (-b, b):
                h = (
                    Pos(rx, ry, rz - P.PYLON_FLANGE_H / 2 + sz)
                    * Rot(0, 0, yaw)
                    * Pos(0, sv, 0)
                    * Rot(0, 90, 0)
                    * Cylinder(P.M3_TAP / 2, 46)
                )
                holes = h if holes is None else holes + h
    return holes


def component_envelopes(grow=0.0):
    """Every bought part, placed, optionally grown by a fit clearance."""
    return [
        Pos((P.BATT_X0 + P.BATT_X1) / 2, 0, P.BATT_FLOOR_Z + C.BATT_H / 2)
        * C.battery(grow),
        Pos(P.STACK_X, 0, P.STACK_Z) * C.stack(grow),
        Pos(P.VTX_X, 0, -4) * C.vtx(grow),
        Pos(P.RX_X, 0, 4) * C.rx(grow),
    ]


def fuselage_lower():
    part = _main_shell() - body.above(P.SPLIT_CANOPY_Z)

    # Battery floor: a flat pad across the bottom of the cavity.
    floor = Pos((P.BATT_X0 + P.BATT_X1) / 2, 0, P.BATT_FLOOR_Z - 1.5) * Box(
        P.BATT_X1 - P.BATT_X0 + 14, 54, 3.0
    )
        # Trim to the OUTER solid, not the cavity: clipping at the inner surface
    # leaves the floor merely tangent to the shell, and it exports as a
    # separate disconnected solid.
    part += floor & body.outer()

    # Stack posts: four at 30.5 x 30.5, self-tapping M3.
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = P.STACK_X + sx * C.STACK_PITCH / 2
            py = sy * C.STACK_PITCH / 2
            # Runs down past the inner surface into the shell wall so it
            # actually lands on structure instead of floating in the cavity.
            post = Pos(px, py, (P.STACK_Z - 34.0) / 2) * Cylinder(
                4.0, P.STACK_Z + 34.0
            )
            part += post & body.outer()
            part -= Pos(px, py, P.STACK_Z - 5) * Cylinder(P.M3_TAP / 2, 16)

    # Pylon backing ribs, then the tapped bolt pattern through shell + rib.
    part += (_pylon_ribs() & body.outer()) - body.above(P.SPLIT_CANOPY_Z)
    part -= _pylon_bolt_holes()

    # Canopy bolts.
    for px in (P.CANOPY_BOLT_X0, P.CANOPY_BOLT_X1):
        for sy in (1, -1):
            part -= Pos(px, sy * P.CANOPY_BOLT_Y, P.SPLIT_CANOPY_Z - 6) * Cylinder(
                P.M3_TAP / 2, 16
            )

    # ---- carve the real component envelopes out of the structure.
    #
    # This is what makes the fit exact rather than nominal: the bays are not
    # drawn by hand and hoped to be big enough, they are the actual spec-sheet
    # solids from components.py grown by the fit clearance and subtracted. Any
    # rib, post or lip that would have fouled the electronics is removed by
    # construction, and verify.py then confirms zero clash.
    for env in component_envelopes(grow=C.FIT):
        part -= env

    # Cooling gills over the stack.
    for i in range(P.GILL_N):
        gx = P.GILL_X + i * 7.0
        for sy in (1, -1):
            part -= Pos(gx, sy * 34, -2) * Box(P.GILL_W, 20, P.GILL_H)

    return despeck(part.clean())


def fuselage_upper():
    part = _main_shell() - body.below(P.SPLIT_CANOPY_Z)
    for px in (P.CANOPY_BOLT_X0, P.CANOPY_BOLT_X1):
        for sy in (1, -1):
            part -= Pos(px, sy * P.CANOPY_BOLT_Y, P.SPLIT_CANOPY_Z + 8) * Cylinder(
                P.M3_CLR / 2, 30
            )
    return despeck(part.clean())



# ------------------------------------------------------------------ tail fin
def tail_fin():
    """Swept blade. Carries the VTX antenna on the centreline, which is the
    one place on this airframe that is prop-safe at any height -- the rear
    discs are 77.8 mm off centre against a 63.5 mm radius."""
    root = P.FIN_X
    pts = [
        (root, 0.0),
        (root - P.FIN_LEN, 0.0),
        (root - P.FIN_LEN + 6, P.FIN_H),
        (root - P.FIN_SWEEP, P.FIN_H),
    ]
    from build123d import Plane, Polygon, make_face

    blade = Plane.XZ * Polygon(*pts, align=None)
    part = extrude(blade, amount=P.FIN_T / 2, both=True)

    # Saddle foot: a slab straddling the tail cone, then carved by the cone
    # itself so the mating face IS the mould line. The tail is only ~11 mm in
    # radius here, so a spigot deep enough to be useful would punch straight
    # out the bottom -- same reasoning as the pylon root flanges.
    # Foot spans Z 0..30 so it still stands proud of the tail where the cone
    # is fattest (r = 21.6 at the forward end). A shallower foot gets entirely
    # swallowed by the saddle cut up there.
    part += Pos(root - P.FIN_LEN / 2, 0, 12) * Box(
        P.FIN_LEN - 2, P.FIN_FOOT_W, 26
    )
    part -= body.outer(P.SADDLE_GAP)

    # Antenna bore up the trailing edge.
    part -= Pos(root - P.FIN_SWEEP - 4, 0, P.FIN_H - 14) * Rot(0, 8, 0) * Cylinder(
        P.ANT_BORE / 2, 40
    )
    for sx in (-1, 1):
        part -= Pos(root - P.FIN_LEN / 2 + sx * P.FIN_BOLT_SP / 2, 0, 20) \
            * Cylinder(P.M3_CLR / 2, 60)
    return despeck(part.clean())
