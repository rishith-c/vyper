# VYPER-5F — Printing and Assembly

## Part 1: Printing

### Settings (Elegoo Neptune 4, 0.4 mm nozzle, PETG)

| | |
|---|---|
| Layer height | 0.20 mm |
| **Walls / perimeters** | **5** — this is the important one |
| Top / bottom layers | 5 |
| Infill | 20% gyroid (shells), 15% gyroid (pylons) |
| Nozzle | 240 °C |
| Bed | 80 °C |
| Cooling | 40-50% |
| Speed | ≤ 60 mm/s on walls |
| Supports | **None. Not on any part.** |
| Brim | None needed |

**Why 5 walls matters more than infill.** Almost every part here is a shell.
The walls *are* the structure and infill is close to irrelevant — the pylon
strut only sees about 1.8 MPa against ~45 MPa PETG yield, because a fairing
gets a deep section for free. Going from 3 walls to 5 is most of the strength;
going from 20 % to 60 % infill just adds mass.

Slow the walls down. Peak stress is carried by the outer perimeters running the
length of the pylon; a wall laid down at 100 mm/s bonds worse than one at 50.

### Orientation — the part that actually matters

| Part | Orientation | Why |
|---|---|---|
| **Pylon A / B** | **Flat top DOWN on the bed** | Non-negotiable. See below. |
| Fuselage lower | Cut face down (as exported) | Half-tube, section shrinks upward |
| Fuselage upper | Cut face down (as exported) | Same |
| Nose cone | Open end down (as exported) | A dome; shrinks all the way to the tip |
| Tail cone | Open end down (as exported) | Same |
| Tail fin | Flat on its side (as exported) | Loads are in-plane |

Every STL is already oriented correctly. **Drop them in the slicer and do not
rotate anything.**

#### If you take one thing from this document

The pylon's flat top is the motor mounting surface, and it goes **on the bed**.

- All the pylon's fairing hangs on the *other* side, so the cross-section only shrinks
  going upward. No overhangs, no supports, nothing to clean up.
- Bed contact is the entire 90 x 67 mm plan area. It will not lift.
- The bending fibres end up as continuous perimeters running the full length.
- Layer adhesion only sees transverse shear (~0.6 MPa against a bond good for
  25+ MPa).

Print a pylon on its side or on its end and it will snap at the root on the
first hard landing, because you will have put the layer boundaries square
across the tension face. It also puts a 77 degree overhang along the whole
upper surface.

### Print order

Print **one pylon first** and check it: the four flange holes should pass an M3
freely, the flat top should sit on glass with no rock, and the pad under the
motor should measure 4.0 mm. Then print the rest.

Total print time is roughly 18-24 hours for the full set. About 190 g of
filament, so budget 350 g including one failure.

### Post-print

- The **wire tunnel** through each pylon and the **M2 camera holes** are the
  only horizontal bores; they bridge with slight droop. Run a drill through by
  hand before assembly.
- Test-fit an M3 through the pylon flange holes. If tight, run a 3.3 mm drill
  rather than forcing the bolt — forcing it splits the layers.
- Deburr the motor pads so the motors seat flat.
- Dry-fit the pylon saddles against the fuselage before you bolt anything. They
  are cut from the mould line with 0.6 mm of clearance, so they should drop on
  without persuasion.

---

## Part 2: Assembly

### Layout, for reference

```
  X = +112 .. +68   nose cone (removable) -- camera + cooling inlet
  X = +68 .. -92    main body: lower shell (structure) + canopy
  X = -92 .. -142   tail cone -- cooling exit; fin bolts on top
  X = +60 .. -16    battery bay, floor at Z = -18, canopy closes at Z = +13
  X = -39           stack, on four posts at 30.5 x 30.5
  Z = +16           pylon roots on the shoulder, and the motor pad plane
  Z = +42           prop plane
```

### Order

**1. Pylons to the lower shell.**
Four **M3x20** per pylon, from outside, through the shell wall into the backing
ribs. Washer under every head. The saddle face is cut from the fuselage mould
line itself, so each pylon should sit flush with no rocking — if it does rock,
you have the wrong hand. Hand A goes to the 45° and 225° stations, hand B to
315° and 135°.

Work diagonally and do not fully tighten until all four are on.

**2. Motors.**
Four **M3x8** each, up through the 4 mm pad into the motor. **Nothing longer** —
the belly pocket exists precisely so an M3x8 is right; a longer screw goes into
the windings and kills the motor.

Drop the phase wires through the bell bore into the belly pocket, then feed them
through the wire tunnel and out the flange into the fuselage.

**3. Stack.**
Four **M3x8** self-tapping into the printed posts, ESC below, FC above. FC arrow
points forward (+X). Solder the four motors, then the XT60 pigtail, then the
**470 µF capacitor directly across the XT60 pads** — on 6S that capacitor is not
optional.

**4. VTX and RX.**
Their bays are aft of the stack. Keep the VTX against a gill so it has airflow.

**5. Tail cone and fin.**
Two **M3x12** join the tail cone to the main body. The fin saddles on top of the
cone with two more. Antenna shaft up the 6 mm bore in the fin — the centreline
is the one place on this airframe that is prop-safe at any height, because the
rear discs sit 77.8 mm off centre against a 63.5 mm radius.

**6. Nose cone and camera.**
Camera slides into its socket from behind; one **M2x8** per side sets the tilt by
friction, **30-40°** for this power class. Two **M3x12** hold the nose cone on.
Leave enough slack in the camera lead to pull the nose off without unplugging.

**7. Battery and canopy.**
The pack drops into the bay onto the floor at Z = -18. **The canopy is the
retainer** — there is no strap. Four **M3x10** close it. If the lid will not sit
down, the pack is not fully seated.

### Before the first flight

**Props off for all of this.**

1. Flash/verify Betaflight; set motor order and directions in the Motors tab.
2. Bind the RX. Confirm failsafe actually cuts the motors.
3. Check the FC arrow really is forward.
4. Set VTX band and power. **25 mW indoors**, and never power a VTX without an
   antenna.
5. Set a **3.5 V/cell** low-voltage warning.
6. **Run a 30-second bench spool-up with the canopy ON and feel the ESC after.**
   This airframe is a closed tube; if the cooling path is blocked the ESC will
   thermal-throttle and you want to find that out on the bench.
7. Props on last, checking each direction against the Betaflight diagram.

### Expect to break things

The **nose cone, tail cone and fin** are the fuses — they are on two bolts each
and are meant to come off rather than lever the shell. 7-15 g of filament each.
Print spares of all three with the first batch, plus one pylon of each hand.

The expensive part to lose is the **lower shell** at 68 g and several hours. It
is the one part worth protecting, which is the real cost of a faired airframe
compared with the plate version, where the sacrificial item was a 10 g arm.
