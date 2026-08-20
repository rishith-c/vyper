# VYPER validation gates

Passing software tests means the geometry and first-order equations are
self-consistent. It does **not** prove 200 km/h, structural safety, ESC current
rating, fire safety, or flightworthiness.

## G0 — digital design

- All CadQuery solids closed; battery, stack, wires, prop discs and purchased
  component envelopes clear in the assembly.
- Every printed part fits the Neptune 4 build volume in its documented print
  orientation.
- FC schematic ERC: zero unexplained errors. FC PCB DRC: zero violations and
  zero unconnected pads.
- ESC schematic ERC and fab-profile DRC: same standard; independent power-
  electronics review completed.

## G1 — printed coupons and static structure

- Print the tolerance coupon in the same dry PETG/PA-CF, nozzle, layer height,
  orientation and thermal conditions as the flight parts. Record actual hole,
  slot and spigot corrections.
- Proof-load each arm to 2× the maximum measured motor thrust for 60 s, then
  inspect under magnification. No crack, permanent set, loose insert or motor
  screw movement.
- Vibration sweep with instrumented motor; no arm/hub resonance in the armed
  RPM band and no fastener back-out after thread-lock cure.

## G2 — low-energy electronics

- Resistance and diode-mode map recorded before power. Bench supply current
  limit starts below 100 mA.
- Verify 3.3/5 V and any purchased-stack accessory rails, reset, SWD, USB,
  gyro axes, receiver failsafe and all
  four motor outputs with no LiPo and no props.
- Validate watchdog, brownout, gate-driver `nFAULT`, over-current and
  stuck-rotor response by injection—not by reading source code.

## G3 — propulsion dyno

- One motor/ESC channel at a time behind a polycarbonate shield, remotely
  operated, with current, bus voltage, differential switch-node voltage, RPM
  and thermal imaging logged.
- Step 3S → 4S → 6S and 25% → 50% → 75% → full. Stop on smoke, odor, unstable
  commutation, >50 V switch-node overshoot, >100 °C MOSFET case, >85 °C PCB,
  >60 °C connector or >55 °C battery.
- Repeat 30 A steady-state and 55 A/2 s burst in the closed fuselage. Ratings
  are the lower of the thermal and electrical test results.

## G4 — restrained vehicle

- Props verified for rotation and installed only after every no-prop check.
- Full vehicle restrained behind a shield; verify current sum, receiver loss,
  arming lockout, GPS rescue configuration, motor desync margin and vibration.
- Inspect every print, screw, solder joint and wire for chafe after each run.

## G5 — flight expansion

- Large controlled field, spotter, local authorization, fire containment and
  a documented abort area. Start with hover and low-speed passes.
- Expand speed in small increments while logging voltage, current, RPM, gyro
  vibration, ESC temperature and GPS. The 200 km/h claim exists only after
  two-direction calibrated radar or validated high-rate GNSS runs.
- Retire any prop, arm or shell involved in a strike or unexplained vibration.
