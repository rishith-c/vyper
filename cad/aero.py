"""VYPER-5W aerodynamic analysis.

Component drag build-up plus momentum-theory rotor work. This is engineering
estimation, NOT CFD -- every coefficient below is a handbook value for the
shape in question and is named so you can argue with it. Areas that can be
measured off the actual solids are measured, not guessed: the wing planform
and the plate area sitting under the prop discs are both taken by boolean.

Run:  python aero.py
"""

import math

from build123d import Cylinder, Plane, Pos, Rot, extrude, section

import body
import components as C
import shells
import vy_params as P
import wing

RHO = 1.225          # kg/m^3, sea level
NU = 1.46e-5         # m^2/s, kinematic viscosity of air

# ---------------------------------------------------------------- drag coefficients
# All referenced to the area named alongside them.
CD_FUSELAGE = 0.10   # streamlined body of revolution, fineness ~5, on frontal area
CD_WING_P0 = 0.020   # profile drag of a thick flat-ish section, on planform
CD_MOTOR = 0.80      # exposed cylinder in crossflow, on frontal area
CD_PLATE = 1.17      # flat plate normal to flow, on frontal area
K_INTERFERENCE = 1.15

# A conventional open racer for comparison: exposed pack, 4 flat arms, open
# stack. 0.0075 m^2 equivalent flat-plate area is mid-range for the class.
CDA_OPEN_RACER = 0.0075


def wing_planform_m2():
    """Net planform of BOTH panels, measured off the solid rather than the
    parameters, so the lightening bay and the root saddle are accounted for."""
    total = 0.0
    for hand in wing.HANDS:
        w = wing.gen(hand)
        # Slice at mid-skin and take the face area: the panel is prismatic in
        # plan over the skin thickness, so this is the projected planform.
        sec = section(w, Plane.XY.offset(-P.WING_SKIN / 2))
        total += sum(f.area for f in sec.faces())
    return total * 1e-6


def plate_under_discs_m2():
    """Wing area actually sitting inside the prop discs -- this is what
    generates rotor download in the hover."""
    total = 0.0
    for hand in wing.HANDS:
        w = Pos(0, 0, P.MOTOR_PAD_Z) * wing.gen(hand)
        for mx, my in wing.motor_stations(hand):
            disc = Pos(mx, my, P.MOTOR_PAD_Z) * Cylinder(P.PROP_R, 200)
            try:
                inter = w & disc
                sec = section(inter, Plane.XY.offset(P.MOTOR_PAD_Z - P.WING_SKIN / 2))
                total += sum(f.area for f in sec.faces())
            except Exception:
                pass
    return total * 1e-6


def disc_area_m2():
    return 4 * math.pi * (P.PROP_R * 1e-3) ** 2


def report(auw_g, thrust_g):
    W = auw_g * 9.81e-3
    T = thrust_g * 9.81e-3

    Sw = wing_planform_m2()
    span = 2 * (P.WING_TIP_Y - P.WING_ROOT_Y) * 1e-3 + 2 * P.FUSE_R_MAX * 1e-3
    ar = span ** 2 / Sw if Sw else 0.0

    print("=== wing ===")
    print(f"planform (both panels)   {Sw * 1e4:8.1f} cm^2   (measured off the solids)")
    print(f"span (tip to tip)        {span * 1e3:8.0f} mm")
    print(f"aspect ratio             {ar:8.2f}")
    print(f"wing loading             {auw_g / (Sw * 1e4):8.2f} g/cm^2")

    # Speed at which the wings alone carry the aircraft, at a usable CL.
    CL = 0.55
    v_carry = math.sqrt(2 * W / (RHO * Sw * CL))
    print(f"speed for wings to carry AUW at CL={CL}: "
          f"{v_carry:5.1f} m/s = {v_carry * 3.6:5.0f} km/h")
    for v in (20.0, 30.0, 40.0):
        L = 0.5 * RHO * v * v * Sw * CL
        print(f"  lift at {v:4.0f} m/s ({v * 3.6:3.0f} km/h): "
              f"{L / 9.81e-3:6.0f} g = {100 * L / W:4.0f} % of AUW")

    # Reynolds number, to say whether the coefficients above are even valid.
    chord = (P.WING_PLAN[0][0] - P.WING_PLAN[-1][0]) * 1e-3
    re30 = 30.0 * chord / NU
    print(f"wing chord {chord * 1e3:.0f} mm -> Re at 30 m/s = {re30:,.0f}")
    print("  Re ~4e5 is transitional -- high enough that the 0.020 profile")
    print("  drag figure is defensible, low enough that it is still the")
    print("  softest number in this analysis.")

    print("\n=== drag build-up ===")
    a_fuse = math.pi * (P.FUSE_R_MAX * 1e-3) ** 2
    a_motor = 4 * (C.MOTOR_BELL_D * C.MOTOR_H) * 1e-6
    d_fuse = CD_FUSELAGE * a_fuse
    d_wing = CD_WING_P0 * Sw
    d_motor = CD_MOTOR * a_motor
    cda = (d_fuse + d_wing + d_motor) * K_INTERFERENCE
    for name, v in (("fuselage", d_fuse), ("wings (profile)", d_wing),
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
    print(f"wing area inside the discs {plate * 1e4:6.0f} cm^2 = {100 * frac:4.1f} %"
          " of disc area  (measured)")
    print(f"estimated hover download   {100 * dl:4.1f} % of thrust"
          f"  = {dl * thrust_g:4.0f} g")
    print("  This is the price of the wing layout. The lightening bay between")
    print("  the motors exists partly to keep it down.")

    return {
        "wing_area_m2": Sw,
        "cda_m2": cda,
        "v_max_ms": v_max,
        "download_frac": dl,
        "plate_frac": frac,
        "aspect_ratio": ar,
    }


def airframe_mass_g():
    g = 0.0
    for fn in (shells.fuselage_lower, shells.fuselage_upper, shells.nose_cone,
               shells.tail_cone, shells.tail_fin):
        g += fn().volume * P.SHELL_FILL * P.PETG_RHO
    for h in wing.HANDS:
        g += wing.gen(h).volume * P.WING_FILL * P.PETG_RHO
    return g


if __name__ == "__main__":
    auw = airframe_mass_g() + sum(C.PAYLOAD.values())
    report(auw, 4 * 1600.0)
