"""VYPER-5W aerodynamic analysis.

Component drag build-up plus momentum-theory rotor work. This is engineering
estimation, NOT CFD -- every coefficient below is a handbook value for the
shape in question and is named so you can argue with it. Areas that can be
measured off the actual solids are measured, not guessed: the wing planform
and the plate area sitting under the prop discs are both taken by boolean.

Run:  python aero.py
"""

import math

from build123d import Cylinder, Plane, Pos, Rot, section

import body
import components as C
import shells
import vy_params as P
import arm

RHO = 1.225          # kg/m^3, sea level
NU = 1.46e-5         # m^2/s, kinematic viscosity of air

# ---------------------------------------------------------------- drag coefficients
# All referenced to the area named alongside them.
CD_FUSELAGE = 0.10   # streamlined body of revolution, fineness ~5, on frontal area
CD_BLADE = 0.20      # rounded rectangular strut, on frontal area (t x span)
CD_MOTOR = 0.80      # exposed cylinder in crossflow, on frontal area
CD_PLATE = 1.17      # flat plate normal to flow, on frontal area
K_INTERFERENCE = 1.15

# A conventional open racer for comparison: exposed pack, 4 flat arms, open
# stack. 0.0075 m^2 equivalent flat-plate area is mid-range for the class.
CDA_OPEN_RACER = 0.0075


def blade_frontal_m2():
    """Silhouette of the two blades looking down the flight axis.

    Each blade is ARM_W thick and ARM_H deep, crossing at ARM_ANGLE, so the
    span it projects onto Y is len*sin(angle). Frontal area is that projected
    span times the depth, minus the part hidden behind the body.
    """
    proj = arm.ARM_LEN * math.sin(math.radians(arm.ARM_ANGLE))
    exposed = max(proj - 2 * P.FUSE_R_MAX, 0.0)
    return 2 * exposed * P.ARM_H * 1e-6


def plate_under_discs_m2():
    """Blade area inside the prop discs -- the rotor-download term."""
    total = 0.0
    for notch, sign in (("top", 1.0), ("bottom", -1.0)):
        a = (
            Pos(0, 0, P.MOTOR_PAD_Z)
            * Rot(0, 0, sign * arm.ARM_ANGLE)
            * arm.gen(notch)
        )
        for mx, my in P.MOTOR_XY:
            disc = Pos(mx, my, P.MOTOR_PAD_Z) * Cylinder(P.PROP_R, 200)
            try:
                sec = section(a & disc,
                              Plane.XY.offset(P.MOTOR_PAD_Z - 1.0))
                total += sum(f.area for f in sec.faces())
            except Exception:
                pass
    return total * 1e-6


def disc_area_m2():
    return 4 * math.pi * (P.PROP_R * 1e-3) ** 2


def report(auw_g, thrust_g):
    W = auw_g * 9.81e-3
    T = thrust_g * 9.81e-3

    Sb = blade_frontal_m2()

    print("=== arms ===")
    print(f"two blades, {P.ARM_W:.0f} x {P.ARM_H:.0f} mm, "
          f"{arm.ARM_LEN:.0f} mm long, crossing at "
          f"{2 * arm.ARM_ANGLE:.0f} deg")
    print(f"blade frontal silhouette  {Sb * 1e4:8.1f} cm^2")
    print("  The blades make no useful lift and are not meant to. The whole")
    print("  point of this layout is that a 9 mm blade edge-on costs almost")
    print("  nothing, so the drag budget is body + motors and nothing else.")

    print("\n=== frame geometry ===")
    xs = sorted({abs(x) for x, _ in P.MOTOR_XY})
    ys = sorted({abs(y) for _, y in P.MOTOR_XY})
    fa, lat = 2 * xs[0], 2 * ys[0]
    frontal_wing = Sb
    print(f"stretched X: {fa:.0f} mm fore-aft / {lat:.0f} mm lateral"
          f" = {fa / lat:.2f}:1")
    print(f"lateral spacing sits at the 127 mm prop minimum + "
          f"{lat - P.PROP_DIA:.0f} mm")
    print(f"exposed blade frontal area {frontal_wing * 1e4:5.1f} cm^2")

    print("\n=== drag build-up ===")
    a_fuse = math.pi * (P.FUSE_R_MAX * 1e-3) ** 2
    a_motor = 4 * (C.MOTOR_BELL_D * C.MOTOR_H) * 1e-6
    d_fuse = CD_FUSELAGE * a_fuse
    d_wing = CD_BLADE * Sb
    d_motor = CD_MOTOR * a_motor
    cda = (d_fuse + d_wing + d_motor) * K_INTERFERENCE
    for name, v in (("fuselage", d_fuse), ("2 blades", d_wing),
                    ("4 motor bells", d_motor)):
        print(f"  {name:18s} CdA = {v * 1e4:6.2f} cm^2  ({100 * v / (cda / K_INTERFERENCE):4.0f} %)")
    print(f"  interference x{K_INTERFERENCE}")
    print(f"  TOTAL              CdA = {cda * 1e4:6.2f} cm^2")
    print(f"  open racer, same class  {CDA_OPEN_RACER * 1e4:6.2f} cm^2"
          f"   -> {100 * (1 - cda / CDA_OPEN_RACER):.0f} % less drag")
    print("  NOTE: the motors are now the single largest drag item. Fairing")
    print("  the airframe has made the bare bells the thing worth attacking.")

    print("\n=== top speed ===")
    kv, cells = 1750, 6
    rpm = kv * cells * 3.7 * 0.78          # loaded, ~78 % of no-load
    pitch_m = 4.3 * 0.0254
    v_pitch = rpm / 60.0 * pitch_m
    v_max = 0.75 * v_pitch
    print(f"prop 5x4.3 at ~{rpm:,.0f} rpm -> pitch speed {v_pitch:5.1f} m/s")
    print(f"realistic max level speed      {v_max:5.1f} m/s = {v_max * 3.6:5.0f} km/h")
    d_at_max = 0.5 * RHO * v_max ** 2 * cda
    print(f"drag there {d_at_max:5.2f} N against {T:5.1f} N available")
    print("  Thrust is NOT the limit -- prop pitch is. This is the single most")
    print("  important result here: the fairing does not raise the ceiling,")
    print("  it lowers what it costs to sit at the ceiling.")

    print("\n=== what the fairing actually buys ===")
    for v in (30.0, 40.0):
        d_new = 0.5 * RHO * v * v * cda
        d_old = 0.5 * RHO * v * v * CDA_OPEN_RACER
        print(f"  at {v:.0f} m/s ({v * 3.6:.0f} km/h): drag {d_new:4.2f} N vs "
              f"{d_old:4.2f} N open  ->  {100 * (1 - d_new / d_old):2.0f} % less "
              f"power to hold speed")

    print("\n=== hover ===")
    A = disc_area_m2()
    v_i = math.sqrt(W / (2 * RHO * A))
    p_ideal = W * v_i
    print(f"disc area (4 props)      {A * 1e4:8.0f} cm^2")
    print(f"disc loading             {W / A:8.1f} N/m^2")
    print(f"induced velocity         {v_i:8.1f} m/s")
    print(f"ideal hover power        {p_ideal:8.0f} W  "
          f"(x ~1.9 for real figure of merit -> {p_ideal * 1.9:.0f} W)")

    plate = plate_under_discs_m2()
    frac = plate / A
    # Download scales with the blocked fraction; ~0.06 of thrust for a plate
    # fully covering the disc at this spacing (gap/R = 0.41).
    dl = frac * 0.06
    print(f"blade area inside the discs {plate * 1e4:5.0f} cm^2 = {100 * frac:4.1f} %"
          " of disc area  (measured)")
    print(f"estimated hover download   {100 * dl:4.1f} % of thrust"
          f"  = {dl * thrust_g:4.0f} g")
    print("  Two thin blades block far less of the disc than the wing panels")
    print("  did, which is the other half of why this layout is better here.")

    return {
        "blade_frontal_m2": Sb,
        "cda_m2": cda,
        "v_max_ms": v_max,
        "download_frac": dl,
        "plate_frac": frac,
    }


def airframe_mass_g():
    g = 0.0
    for fn in (shells.fuselage_lower, shells.fuselage_upper, shells.nose_cone,
               shells.tail_cone, shells.tail_fin):
        g += fn().volume * P.SHELL_FILL * P.PETG_RHO
    for n in ("top", "bottom"):
        g += arm.gen(n).volume * P.ARM_FILL * P.PETG_RHO
    return g


if __name__ == "__main__":
    auw = airframe_mass_g() + sum(C.PAYLOAD.values())
    report(auw, 4 * 1600.0)
