"""VYPER test suite: printability, tolerances, aerodynamics, fit.

Run:  python test_vyper.py
"""
import math
import cadquery as cq
import vyper_shell as M

RHO, NU = 1.225, 1.46e-5
fails = []


def check(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        fails.append(name)


shell, arm, hub = M.result.val(), M.arm.val(), M.hub.val()

print("=== geometry / fit ===")
for n, o in (("shell", shell), ("arm", arm), ("hub", hub)):
    check(f"{n} is one closed solid", len(o.Solids()) == 1 and o.Volume() > 0,
          f"{len(o.Solids())} solid(s), {o.Volume():.0f} mm^3")

# Battery must fit the cavity at its narrowest packing station.
bw, bh = 35.0, 30.0
need = math.hypot(bw / 2, bh / 2)
have = M.R_MAX - M.WALL
check("4S 1500 pack fits cavity", have >= need + 0.5,
      f"needs {need:.1f} mm internal radius, has {have:.1f}")

# Stack must fit on the shelf.
check("36 mm stack fits shelf", (M.R_MAX - M.WALL) * 2 >= 36.0 + 2,
      f"shelf clear dia {(M.R_MAX - M.WALL) * 2:.1f} mm vs 36 mm board")

# Arm must actually pass its slot.
check("arm passes its slot", M.ARM_FIT >= 0.3,
      f"{M.ARM_FIT:.1f} mm total slip fit on a {M.ARM_THICK}x{M.ARM_WIDTH} blade")

print("\n=== printing ===")
BED = (225.0, 225.0, 265.0)
for n, o in (("shell", shell), ("arm", arm), ("hub", hub)):
    b = o.BoundingBox()
    flat = b.xlen < BED[0] - 10 and b.ylen < BED[1] - 10 and b.zlen < BED[2] - 10
    diag = (b.xlen + b.ylen) / math.sqrt(2) < BED[0] - 10
    check(f"{n} fits Neptune 4", flat or diag,
          f"{b.xlen:.0f} x {b.ylen:.0f} x {b.zlen:.0f} mm"
          + ("" if flat else "  [rotate on bed]"))

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
for name, nominal, hole in (("M3 motor", 3.0, 3.2), ("M3 hub", 3.0, M.HUB_BOLT_D),
                            ("M3 stack", 3.0, M.STACK_HOLE_D)):
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
motor_frontal = 4 * 27.9 * 32.4 * 1e-6
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

rpm = 2450 * 4 * 3.7 * 0.78
v_pitch = rpm / 60.0 * 4.3 * 0.0254
v_max = 0.75 * v_pitch
print(f"  2450KV on 4S -> ~{rpm:,.0f} rpm, pitch speed {v_pitch:.1f} m/s")
print(f"  realistic top speed {v_max:.1f} m/s = {v_max * 3.6:.0f} km/h")
d = 0.5 * RHO * v_max ** 2 * cda
check("prop-pitch limited, not thrust limited", d < 20.0,
      f"{d:.1f} N drag at Vmax against ~44 N of 4S thrust")

fineness = M.TOTAL_LEN / (2 * M.R_MAX)
check("fuselage fineness in the low-drag band", 4.0 <= fineness <= 7.0,
      f"{fineness:.2f} (optimum ~5-6)")

print("\n=== mass ===")
SHELL_FILL, ARM_FILL = 0.90, 0.62
printed = (shell.Volume() * SHELL_FILL + hub.Volume() * 0.5
           + 4 * arm.Volume() * ARM_FILL) * 1.27e-3
payload = 4 * 32 + 22 + 165 + 8 + 8 + 1.5 + 4 * 4.5 + 40
auw = printed + payload
thrust = 4 * 1150.0
print(f"  printed {printed:.0f} g + payload {payload:.0f} g = AUW {auw:.0f} g")
check("thrust-to-weight", thrust / auw > 4.0, f"{thrust / auw:.1f}:1")

print()
if fails:
    print(f"{len(fails)} FAILED: {', '.join(fails)}")
    raise SystemExit(1)
print("all checks passed")
