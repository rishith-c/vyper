"""Shared fuselage geometry. Not a printed part -- the shell generators import
this so the outer mould line is defined exactly once.

The fuselage is a true body of revolution about X, built by revolving a
splined profile. Everything else (cavity, splits, bays, lands) is boolean work
against that single surface, so the outer shape can be retuned by editing
FUSE_PROFILE alone.
"""

import math

from build123d import (
    Axis,
    Box,
    Cylinder,
    Line,
    Plane,
    Pos,
    Rot,
    Spline,
    make_face,
    revolve,
)

import vy_params as P


def _revolved(stations):
    """Revolve a (x, radius) profile about X, capped flat at both ends."""
    pts = [(x, r) for x, r in stations]
    x_hi, r_hi = pts[0]
    x_lo, r_lo = pts[-1]
    edges = [
        Spline(*pts),
        Line((x_lo, r_lo), (x_lo, 0.0)),
        Line((x_lo, 0.0), (x_hi, 0.0)),
        Line((x_hi, 0.0), (x_hi, r_hi)),
    ]
    return revolve(Plane.XZ * make_face(edges), axis=Axis.X)


def outer(grow=0.0):
    """Outer mould line, one closed solid.

    `grow` inflates the radii. Used for saddle cuts: a saddle carved from the
    exact mould line fits its own station perfectly, but the same part rotated
    to another station where the radius differs by even 0.2 mm then bites into
    the shell. A small uniform clearance makes every hand fit every station,
    which is what a bolted flange wants anyway.
    """
    if grow == 0.0:
        return _revolved(P.FUSE_PROFILE)
    return _revolved(tuple((x, r + grow) for x, r in P.FUSE_PROFILE))


def cavity(grow=0.0):
    """Internal volume. The outer profile offset inward by the wall thickness,
    truncated short of both tips so the nose and tail stay solid."""
    fwd, aft = P.CAVITY_X
    inner = [(fwd, max(_radius_at(fwd) - P.FUSE_WALL + grow, 1.0))]
    for x, r in P.FUSE_PROFILE:
        if not (aft < x < fwd):
            continue
        inner.append((x, max(r - P.FUSE_WALL + grow, 1.0)))
    inner.append((aft, max(_radius_at(aft) - P.FUSE_WALL + grow, 1.0)))
    # A duplicated X station makes GeomAPI_Interpolate throw; the cap
    # stations can land exactly on a profile station when the profile is
    # retuned, so dedupe rather than assuming they never collide.
    seen, clean = set(), []
    for x, r in inner:
        k = round(x, 6)
        if k in seen:
            continue
        seen.add(k)
        clean.append((x, r))
    return _revolved(clean)


def _radius_at(x):
    """Linear interpolation of the outer profile. Close enough for the
    cavity end caps; the spline itself defines the real surface."""
    pts = P.FUSE_PROFILE
    for (x0, r0), (x1, r1) in zip(pts, pts[1:]):
        if x1 <= x <= x0:
            t = (x - x0) / (x1 - x0)
            return r0 + t * (r1 - r0)
    return pts[-1][1] if x < pts[-1][0] else pts[0][1]


def shell():
    """Hollow fuselage before any splits or cutouts."""
    return outer() - cavity()


# --------------------------------------------------------------- slicing aids
BIG = 500.0


def fwd_of(x):
    return Pos(x + BIG / 2, 0, 0) * Box(BIG, BIG, BIG)


def aft_of(x):
    return Pos(x - BIG / 2, 0, 0) * Box(BIG, BIG, BIG)


def above(z):
    return Pos(0, 0, z + BIG / 2) * Box(BIG, BIG, BIG)


def below(z):
    return Pos(0, 0, z - BIG / 2) * Box(BIG, BIG, BIG)


# --------------------------------------------------------------- pylon frames
def pylon_root(angle):
    """Where a pylon leaves the fuselage, in frame coordinates."""
    x = P.PYLON_ROOT_X if math.cos(math.radians(angle)) > 0 else -P.PYLON_ROOT_X
    sign_y = 1.0 if math.sin(math.radians(angle)) > 0 else -1.0
    # The root sits at MOTOR_PAD_Z on the fuselage shoulder, so solve the
    # circular section for the y at that height.
    r = _radius_at(x)
    z = P.PYLON_ROOT_Z
    y = math.sqrt(max(r * r - z * z, 1.0))
    return (x, sign_y * y, z)


def motor_pos(i):
    """Motor centre by index into P.MOTOR_XY."""
    x, y = P.MOTOR_XY[i]
    return (x, y, P.MOTOR_PAD_Z)


def all_motors():
    return [motor_pos(i) for i in range(len(P.MOTOR_XY))]


def pylon_placement(angle):
    """Transform taking a pad-down pylon (built along local +X, pad at local
    Z=0) to its place on the airframe.

    The pylon is DEFINED with its motor pad flat at local Z=0 and every bit of
    fairing hanging below it -- that is what lets it print pad-face-down with
    no overhang anywhere, exactly like the plate version's arm. The nose-down
    MOTOR_TILT is applied here as placement only, so it never costs printability.
    """
    rx, ry, rz = pylon_root(angle)
    mx, my, mz = motor_pos(angle)
    # Yaw so local +X points from root to motor.
    yaw = math.degrees(math.atan2(my - ry, mx - rx))
    return Pos(rx, ry, rz) * Rot(0, 0, yaw) * Rot(0, P.MOTOR_TILT, 0)


def pylon_span(angle):
    rx, ry, _ = pylon_root(angle)
    mx, my, _ = motor_pos(angle)
    return math.hypot(mx - rx, my - ry)


def pad_local_x(angle):
    """Distance along the pylon at which the motor pad centre sits."""
    return pylon_span(angle)
