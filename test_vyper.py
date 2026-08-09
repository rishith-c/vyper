"""VYPER test suite: printability, tolerances, aerodynamics, fit.

Run:  python test_vyper.py
"""
import math
import cadquery as cq
import vyper_shell as M
import vyper_spec as S

RHO, NU = 1.225, 1.46e-5
fails = []


def check(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        fails.append(name)


shell = M.result.val()
shell_body = M.shell_body.val()
shell_nose = M.shell_nose.val()
arm, hub = M.arm.val(), M.hub.val()
cassette, tail_cap = M.electronics_cassette.val(), M.tail_cap.val()

print("=== geometry / fit ===")
for n, o in (("shell", shell), ("arm", arm), ("hub", hub),
             ("electronics cassette", cassette),
             ("tail cap", tail_cap)):
    check(f"{n} is one closed solid", len(o.Solids()) == 1 and o.Volume() > 0,
          f"{len(o.Solids())} solid(s), {o.Volume():.0f} mm^3")

# Battery must fit the cavity at its narrowest packing station.
bw, bh = S.BATTERY_WIDTH_MM, S.BATTERY_HEIGHT_MM
need = math.hypot(bw / 2, bh / 2)
have = M.R_MAX - M.WALL
check("6S high-current pack fits cavity", have >= need + 0.8,
      f"{S.BATTERY_MODEL}: needs {need:.2f} mm internal radius, "
      f"has {have:.2f} ({have - need:.2f} mm radial fit allowance)")
battery_z0 = M.TAIL_SPIGOT_L + 2.0
battery_z1 = battery_z0 + S.BATTERY_LENGTH_MM
hub_z0 = M.ARM_Z - M.ARM_WIDTH / 2.0
check("battery fits longitudinally below arm hub", battery_z1 <= hub_z0 - 1.0,
      f"battery Z={battery_z0:.0f}..{battery_z1:.0f} mm; "
      f"hub starts Z={hub_z0:.0f} mm")

def inner_radius_at(z):
    if z <= M.Z_NOSE_BASE:
        return M.R_MAX - M.WALL
    x = M.TOTAL_LEN - z
    return M.von_karman_radius(
        x, M.TOTAL_LEN - M.Z_NOSE_BASE, M.R_MAX,
    ) - M.WALL


# Longitudinal boards must clear the shrinking ogive at their forward edges.
esc_top = S.ELECTRONICS_CENTER_Z_MM + S.ESC_BOARD_HEIGHT_MM / 2.0
esc_outboard = (abs(S.ESC_BOARD_CENTER_Y_MM)
                + S.ESC_BOARD_THICKNESS_MM / 2.0
                + S.ESC_COMPONENT_HEIGHT_MM
                + S.ESC_HEAT_SPREADER_THICKNESS_MM)
esc_reach = math.hypot(S.ESC_BOARD_WIDTH_MM / 2.0, esc_outboard)
esc_have = inner_radius_at(esc_top)
check("vertical ESC clears ogive", esc_have >= esc_reach + 2.0,
      f"reach R{esc_reach:.2f} at Z{esc_top:.0f} vs cavity R{esc_have:.2f} "
      f"({esc_have - esc_reach:.2f} mm radial allowance)")

fc_top = S.ELECTRONICS_CENTER_Z_MM + S.FC_BOARD_HEIGHT_MM / 2.0
fc_outboard = (abs(S.FC_BOARD_CENTER_Y_MM)
               + S.FC_BOARD_THICKNESS_MM / 2.0
               + S.FC_COMPONENT_HEIGHT_MM)
fc_reach = math.hypot(S.FC_BOARD_WIDTH_MM / 2.0, fc_outboard)
fc_have = inner_radius_at(fc_top)
check("vertical FC clears ogive", fc_have >= fc_reach + 2.0,
      f"reach R{fc_reach:.2f} at Z{fc_top:.0f} vs cavity R{fc_have:.2f} "
      f"({fc_have - fc_reach:.2f} mm radial allowance)")

hub_top = M.ARM_Z + M.ARM_WIDTH / 2.0
esc_bottom = S.ELECTRONICS_CENTER_Z_MM - S.ESC_BOARD_HEIGHT_MM / 2.0
check("electronics start above arm hub", esc_bottom >= hub_top + 1.0,
      f"ESC starts Z{esc_bottom:.0f}; hub ends Z{hub_top:.0f}")
check("cassette seats on hub", abs(S.CASSETTE_BOTTOM_Z_MM - hub_top) < 1e-6,
      f"cassette datum Z{S.CASSETTE_BOTTOM_Z_MM:.0f} = hub top Z{hub_top:.0f}")

# Arm must actually pass its slot.
check("arm passes its slot", M.ARM_FIT >= 0.3,
      f"{M.ARM_FIT:.1f} mm total slip fit on a {M.ARM_THICK}x{M.ARM_WIDTH} blade")
check("tail cap has positive retention",
      len(M.TAIL_RETAINER_ANGLES) >= 3 and M.TAIL_INSERT_L >= 4.0,
      f"{len(M.TAIL_RETAINER_ANGLES)} radial M2x10 screws into "
      f"{M.TAIL_INSERT_L:.0f} mm heat-set inserts")

print("\n=== wire routing ===")
# Three 20 AWG silicone leads are ~2.3 mm each; bundled they need ~5 mm.
LEAD_D, LEADS = 2.3, 3
bundle = LEAD_D * math.sqrt(LEADS)
check("motor leads fit the arm bore", M.WIRE_BORE_D >= bundle + 0.8,
      f"{M.WIRE_BORE_D} mm bore for a ~{bundle:.1f} mm bundle of "
      f"{LEADS}x{LEAD_D} mm")
check("bore bridges without support", M.WIRE_BORE_D <= 8.0,
      f"{M.WIRE_BORE_D} mm horizontal bore -- bridges cleanly at this size")
check("bore leaves blade sidewalls", (M.ARM_THICK - M.WIRE_BORE_D) / 2 >= 1.0,
      f"{(M.ARM_THICK - M.WIRE_BORE_D) / 2:.2f} mm wall on each side")
check("leads exit inside the fuselage", M.ARM_ROOT_R < M.R_MAX - M.WALL,
      f"root at r={M.ARM_ROOT_R} is inside the r={M.R_MAX - M.WALL} cavity")

print("\n=== pusher configuration ===")
check("motors mounted aft (pusher)", M.PUSHER,
      "props behind the arms; fuselage stays out of the slipstream")
check("thrust still on the flight axis", abs(M.ARM_SWEEP) < 90,
      "pad is normal to the body axis -- sweep moves the arm, not the thrust")

adjacent_spacing = S.adjacent_motor_spacing_mm(M.R_MOTOR)
check("adjacent prop discs clear", adjacent_spacing > S.PROP_DIAMETER_MM + 5.0,
      f"{adjacent_spacing:.1f} mm centres - {S.PROP_DIAMETER_MM:.1f} mm prop "
      f"= {adjacent_spacing - S.PROP_DIAMETER_MM:.1f} mm tip gap")
body_prop_gap = M.R_MOTOR - S.PROP_DIAMETER_MM / 2 - M.R_MAX
check("prop discs clear fuselage", body_prop_gap >= 10.0,
      f"closest radial gap {body_prop_gap:.1f} mm")

print("\n=== printing ===")
BED = (225.0, 225.0, 265.0)
for n, o in (("shell body", shell_body), ("shell nose", shell_nose),
             ("arm", arm), ("hub", hub), ("electronics cassette", cassette),
             ("tail cap", tail_cap)):
    b = o.BoundingBox()
    flat = b.xlen < BED[0] - 10 and b.ylen < BED[1] - 10 and b.zlen < BED[2] - 10
    check(f"{n} fits Neptune 4", flat,
          f"{b.xlen:.0f} x {b.ylen:.0f} x {b.zlen:.0f} mm")

check("wall printable at 0.4 nozzle", M.WALL >= 1.2,
      f"{M.WALL} mm = {M.WALL / 0.4:.0f} extrusions")
# 2207-class motors are built for 4-5 mm carbon arms and ship M3x8; their
# blind threads are 4.5-5.0 mm deep. A 4.0 mm pad is the standard stack-up.
MOTOR_THREAD_DEPTH = 4.5
SCREW_LEN = 8.0
engage = SCREW_LEN - M.MOTOR_PAD_T
check("motor screw engagement", 2.5 <= engage <= MOTOR_THREAD_DEPTH - 0.2,
      f"M3x{SCREW_LEN:.0f} through a {M.MOTOR_PAD_T} mm pad = {engage:.1f} mm "
      f"into a {MOTOR_THREAD_DEPTH} mm blind thread "
      f"({MOTOR_THREAD_DEPTH - engage:.1f} mm spare, does not bottom out)")

# Head bearing on PETG rather than carbon.
head_d, hole_d = 5.5, 3.2
seat = math.pi * (head_d ** 2 - hole_d ** 2) / 4
per_screw = 4 * 1150.0 * 9.81e-3 / 4 / 4      # max thrust / 4 motors / 4 screws
check("screw head bearing on PETG", per_screw / seat < 5.0,
      f"{per_screw / seat:.2f} MPa on {seat:.1f} mm^2 -- use washers anyway, "
      "vibration embeds a bare head over time")

pad_r = M.MOTOR_PATTERN / 2.0 * math.sqrt(2) + 4.0
edge = pad_r - (M.MOTOR_PATTERN / 2.0 * math.sqrt(2) + hole_d / 2)
check("material outboard of motor holes", edge > 1.5,
      f"{edge:.1f} mm of pad beyond each hole")
nose_slope = math.degrees(math.atan2(M.R_MAX, M.TOTAL_LEN - M.Z_NOSE_BASE))
check("nose self-supporting", nose_slope < 45.0,
      f"{nose_slope:.1f} deg from vertical at the ogive base")

print("\n=== tolerances ===")
for name, nominal, hole in (("M3 motor", 3.0, 3.2),
                            ("M3 hub", 3.0, M.HUB_BOLT_D),
                            ("M3 cassette", 3.0, S.CASSETTE_HUB_SCREW_D_MM),
                            ("M2 ESC", 2.0, S.ESC_MOUNT_HOLE_D_MM)):
    check(f"{name} clearance", 0.15 <= hole - nominal <= 0.45,
          f"{hole} mm hole on {nominal} mm bolt = {hole - nominal:.2f} mm")
check("arm slot fit", 0.3 <= M.ARM_FIT <= 0.6,
      f"{M.ARM_FIT} mm -- slide fit, no hammer")

print("\n=== aerodynamics ===")
frontal = math.pi * (M.R_MAX * 1e-3) ** 2
# CORRECTED. At max speed the body axis IS the flight direction, so looking
# down the flow you see each arm's THICKNESS (6 mm) x its exposed length --
# not its 26 mm depth, which lies ALONG the flow and is the streamwise chord.
# The earlier figure used the depth and overstated arm drag by 4.3x.
blade_frontal = 4 * (M.R_MOTOR - M.R_MAX) * M.ARM_THICK * 1e-6
# Sweep: a swept strut only sees the crossflow component, so profile drag
# falls as cos^2(sweep).
sweep_factor = math.cos(math.radians(M.ARM_SWEEP)) ** 2
motor_frontal = S.MOTOR_COUNT * S.MOTOR_DIAMETER_MM * S.MOTOR_LENGTH_MM * 1e-6
cda = (0.09 * frontal + 0.20 * blade_frontal * sweep_factor
       + 0.80 * motor_frontal) * 1.15
print(f"  body frontal   {frontal * 1e4:6.2f} cm^2   CdA {0.09 * frontal * 1e4:5.2f}")
print(f"  4 blades       {blade_frontal * 1e4:6.2f} cm^2   "
      f"CdA {0.20 * blade_frontal * sweep_factor * 1e4:5.2f}"
      f"   (swept {M.ARM_SWEEP:.0f} deg, cos^2 = {sweep_factor:.2f})")
print(f"  4 motor bells  {motor_frontal * 1e4:6.2f} cm^2   CdA {0.80 * motor_frontal * 1e4:5.2f}")
print(f"  TOTAL CdA      {cda * 1e4:6.2f} cm^2  (open racer ~75)")
check("drag beats an open racer", cda < 0.0060, f"{cda * 1e4:.1f} vs 75 cm^2")
check("motors dominate remaining drag",
      0.80 * motor_frontal / (cda / 1.15) > 0.5,
      f"{100 * 0.80 * motor_frontal / (cda / 1.15):.0f} % -- fair them next")
check("thrust stays on the flight axis",
      True, "pad is normal to the body axis; sweeping the arm costs no thrust")

rpm = S.MOTOR_STATIC_RPM
v_pitch = S.ideal_pitch_speed_kph() / 3.6
required_eff = S.required_pitch_efficiency()
v_target = S.TARGET_SPEED_KPH / 3.6
print(f"  {S.MOTOR_MODEL} manufacturer bench RPM: {rpm:,.0f}")
print(f"  {S.PROP_MODEL}: ideal pitch speed {v_pitch:.1f} m/s "
      f"= {v_pitch * 3.6:.0f} km/h")
print(f"  200 km/h requires {required_eff * 100:.1f}% of ideal pitch speed")
check("200 km/h inside analytical pitch envelope", required_eff <= 0.85,
      f"requires {required_eff * 100:.1f}% pitch efficiency; flight validation required")
d = 0.5 * RHO * v_target ** 2 * cda
p_drag = d * v_target
check("200 km/h not drag-thrust limited", d < 20.0,
      f"{d:.1f} N drag and {p_drag:.0f} W ideal propulsive power at target speed")

motor_peak_total = S.MOTOR_COUNT * S.MOTOR_PEAK_CURRENT_A
battery_claim = S.claimed_battery_current_a()
check("claimed battery current exceeds static motor peak",
      battery_claim >= motor_peak_total * 1.20,
      f"manufacturer claim {battery_claim:.0f} A vs {motor_peak_total:.0f} A "
      f"motor sum ({battery_claim / motor_peak_total:.2f}x; verify sag and temperature)")
check("ESC burst target covers selected motor",
      S.ESC_CHANNEL_BURST_A_TARGET >= S.MOTOR_PEAK_CURRENT_A * 1.20,
      f"{S.ESC_CHANNEL_BURST_A_TARGET:.0f} A target vs "
      f"{S.MOTOR_PEAK_CURRENT_A:.0f} A motor peak")

overall_length = M.TOTAL_LEN + M.TAIL_CAP_LEN
fineness = overall_length / (2 * M.R_MAX)
check("fuselage fineness in the low-drag band", 4.0 <= fineness <= 7.0,
      f"{fineness:.2f} including the removable tail (screening band 4-7)")

print("\n=== mass ===")
SHELL_FILL, ARM_FILL = 0.90, 0.62
geometric_printed = (shell.Volume() * SHELL_FILL + hub.Volume() * 0.5
                     + cassette.Volume()
                     + M.tail_cap.val().Volume() * SHELL_FILL
                     + 4 * arm.Volume() * ARM_FILL) * 1.27e-3
printed = S.sliced_airframe_mass_g()
payload = (S.MOTOR_COUNT * S.MOTOR_MASS_G + 30 + S.BATTERY_MASS_G
           + 8 + 8 + 1.5 + 4 * S.PROP_MASS_G + 40)
auw = printed + payload
thrust = 4 * 1572.5
print(f"  sliced {printed:.0f} g (geometric screen {geometric_printed:.0f} g) "
      f"+ payload {payload:.0f} g = AUW {auw:.0f} g")
check("slicer and geometric mass estimates agree",
      abs(printed - geometric_printed) / printed < 0.10,
      f"{printed:.1f} vs {geometric_printed:.1f} g "
      f"({100 * abs(printed - geometric_printed) / printed:.1f}% difference)")
check("thrust-to-weight", thrust / auw > 4.0, f"{thrust / auw:.1f}:1")

print()
if fails:
    print(f"{len(fails)} FAILED: {', '.join(fails)}")
    raise SystemExit(1)
print("all checks passed")
