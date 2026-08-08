# VYPER printing and assembly

This is an EVT build procedure. Do not install props until the restrained-
vehicle gate in `VALIDATION_GATES.md`.

## Print first, measure first

Use the supplied `stl/tolerance_coupon.stl` before any flight part. Hole and
slot compensation depends on material, moisture, nozzle and machine—not the
printer name alone. The current CAD assumes:

- 0.4 mm nozzle, 0.20 mm layers;
- five perimeters for the 2.0 mm shell;
- 0.20 mm diametral allowance on M3 clearance holes;
- 0.40 mm total arm-slot fit;
- 0.25 mm radial nose-lap clearance.

Start with dry PETG for fit prototypes. PA-CF may improve temperature and
stiffness, but only after a hardened nozzle, material-specific drying and new
tolerance/proof-load coupons. Do not transfer PETG compensation blindly.

## Neptune 4 build envelopes

| STL | Quantity | Model envelope | Orientation |
|---|---:|---:|---|
| `vyper_shell_body.stl` | 1 | 57×57×170 mm | open tail on bed, vertical |
| `vyper_shell_nose.stl` | 1 | 57×57×155 mm including lap | joint down, vertical |
| `vyper_tail_cap.stl` | 1 | 57×57×72 mm | wide shoulder on bed |
| `vyper_arm_print.stl` | 4 | 124×31×70 mm | exported print orientation; use brim |
| `vyper_hub.stl` | 1 | 52×52×26 mm | broad face on bed |

The repository's OrcaSlicer 2.4.2 profile produces **259.1 g total PETG** and
**19 h 03 min** estimated machine time: body 76.57 g, nose 36.92 g, four arms
at 24.39 g each, hub 27.31 g and tail 20.77 g. These are G-code estimates, not
scale measurements. All five generated files pass static movement, extrusion,
temperature and machine-bound checks; see `GCODE_REPORT.md`.

The arm contains a horizontal Ø5.5 mm bore. Inspect the bridge and hand-ream
only enough for three 20 AWG silicone leads. A split wall or exposed infill is
a reject.

## Assembly order

1. Install three Ø3.5–3.6×4 mm M2 heat-set inserts in the tail-cap bosses.
   Use a temperature-controlled iron and verify each insert is coaxial with its
   radial hole. Dry-fit three M2×10 screws; the cap must seat on the shoulder,
   not bottom on a screw.
2. Slide each arm into the shell slot and internal hub. Install the four M3
   root bolts finger-tight. Confirm all motor pads share one plane, then torque
   evenly with washers and locknuts.
3. Pull three 20 AWG motor leads through each arm before installing motors.
   Add chafe sleeve at both bore exits and leave service loops inside the body.
4. Measure each motor's blind thread depth. Install each motor with four
   M3×8 screws and Ø7 washers only if the measured depth leaves at least 0.3 mm
   bottoming clearance. Use removable threadlocker in the aluminium threads.
5. Mount the purchased ESC below the FC on the 30.5 mm pattern. Use silicone
   grommets on the FC; keep the stack below the modeled 16 mm height envelope.
   Route motor wires radially from the 18 mm shelf opening with no sharp folds.
6. Solder motor phases, then a 12 AWG XT60 pigtail and a 470–1000 µF 50 V
   low-ESR capacitor directly at the ESC battery pads. Add strain relief that
   carries cable load into the hub/shelf, not the solder joints.
7. Install battery from the full-diameter tail opening. It occupies Z=14–95 mm;
   no board, wire loop or screw may enter that envelope. Add non-slip pad and a
   positive internal restraint before flight.
8. Install tail cap and all three M2×10 retainers. Install the nose only after
   the camera optical window/mount CAD is complete; the present shell has no
   validated camera aperture.

## Wire schedule

| Circuit | Wire | Route |
|---|---|---|
| Battery | 12 AWG silicone | tail opening → strain relief → central ESC pads |
| Motor phases | 20 AWG silicone, 3 per arm | ESC → shelf opening → hub → Ø5.5 arm bore |
| FC/ESC harness | supplied SH1.0 | vertical, ESC to FC, restrained clear of gyro |
| Camera/VTX power/video | 26 AWG | nose side of stack; twist power/ground |
| ELRS CRSF | 26–28 AWG | opposite the VTX and high-current loom |
| RX antennas | manufacturer coax | outside carbon-filled material and prop discs |

## Stop conditions

Stop assembly for any cracked layer, motor that does not seat flat, screw that
bottoms, battery contact with a sharp edge, wire pinched by the tail spigot,
board corner touching the shell, or tail cap that can move with all screws
tight. Then return to CAD or print compensation; do not force the part.
