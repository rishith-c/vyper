# VYPER-5X — Printing and Assembly

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
| **Arm ×2** | **Flat top DOWN, rotated 45° on the bed** | 255 mm will not fit a 225 mm bed square. See below. |
| Fuselage lower | Cut face down (as exported) | Half-tube, section shrinks upward |
| Fuselage upper | Cut face down (as exported) | Same |
| Nose cone | Open end down (as exported) | A dome; shrinks all the way to the tip |
| Tail cone | Open end down (as exported) | Same |
| Tail fin | Flat on its side (as exported) | Loads are in-plane |

**The arms must be rotated on the bed.** They are 255 × 30 mm; rotated 45° they
need (255+30)/√2 = 201 mm in both axes, so they fit a 225 mm bed with 24 mm to
spare. There is no rotation angle at which they fit unrotated — 255 > 225 in one
axis no matter what.


Every STL is already oriented correctly. **Drop them in the slicer and do not
rotate anything.**

#### If you take one thing from this document

The arm's flat top is the motor mounting surface, and it goes **on the bed**.

- The arm's belly rounds away on the *other* side, so the cross-section only shrinks
  going upward. No overhangs, no supports, nothing to clean up.
- Bed contact is a 255 × 9 mm strip plus two 30 mm pads. Use a brim.
- The bending fibres end up as continuous perimeters running the full length.
- Layer adhesion only sees transverse shear (~0.6 MPa against a bond good for
  25+ MPa).

Print an arm on its side or on its end and it will snap at the root on the
first hard landing, because you will have put the layer boundaries square
across the tension face. It also puts a 77 degree overhang along the whole
upper surface.

### Print order

Print the **tolerance coupon** first (20 min, 39 g), then **one arm**. Check the
half-lap notch is 9.0 mm deep, the flat top sits on glass with no rock, and the
pad under each motor measures 4.0 mm. Then print the rest.

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

**1. Interlock the arms.**
`arm_top` is notched from the top, `arm_bottom` from the bottom. They slide
together into a flat X — 9 mm of depth each, so the assembled crossing is the
same 18 mm as the rest of the blade. If they will not seat, check the notch
depth against the coupon rather than forcing them.

**2. Arms to the fuselage spine.**
Four M3 down through the crossing into the shell, two per arm either side of
the centre. Washer under every head.

**3. Motors.**
Four **M3x8** each, up through the 4 mm pad into the bell. **Nothing longer** —
the belly pocket exists so an M3x8 is exactly right. Route the phase wires
along the blade underside into the body.

**4. Stack, VTX, RX.**
Stack on the four printed posts at 30.5 × 30.5. Solder motors, then the XT60,
then the **470 µF capacitor across the XT60 pads** — not optional on 6S.

**5. Nose cone and camera.**
Camera into its socket, one M2 per side sets tilt by friction. Two M3 hold the
nose on. Leave slack in the camera lead so the nose comes off without
unplugging.

**6. Tail cone and fin, then battery and canopy.**
Pack drops into the bay; **the canopy is the retainer**, there is no strap.

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
Print spares of all three with the first batch, plus a spare arm of each notch.

The expensive part to lose is the **lower shell** at 68 g and several hours. It
is the one part worth protecting, which is the real cost of a faired airframe
— though at 21 g an arm is cheap to replace, which is the advantage of
this layout over the wing panels.
