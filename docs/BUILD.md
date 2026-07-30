# VYPER-5 — Printing and Assembly

## Part 1: Printing

### Settings (Elegoo Neptune 4, 0.4 mm nozzle, PETG)

| | |
|---|---|
| Layer height | 0.20 mm |
| **Walls / perimeters** | **5** — this is the important one |
| Top / bottom layers | 5 |
| Infill | 40% gyroid (plates), 50% gyroid (arms) |
| Nozzle | 240 °C |
| Bed | 80 °C |
| Cooling | 40-50% |
| Speed | ≤ 60 mm/s on walls |
| Supports | **None. Not on any part.** |
| Brim | None needed |

**Why 5 walls matters more than infill.** These parts are thin. At 9 mm wide
with 0.4 mm extrusions, five perimeters per side is already 4 mm of the 9 —
the walls *are* the structure and infill is close to irrelevant. Going from
40% to 80% infill adds mass and buys you almost nothing. Going from 3 walls to
5 is most of the strength.

Slow the walls down. Peak stress is carried by the outer perimeters running the
length of the arm; a wall laid down at 100 mm/s bonds worse than one at 50.

### Orientation — the part that actually matters

| Part | Orientation | Why |
|---|---|---|
| **Arm** | **Motor pad face DOWN on the bed. Flat side down.** | Non-negotiable. See below. |
| Bottom plate | Flat, as exported | Plate loads are in-plane |
| Top plate | Flat, as exported | |
| Camera cage | Base down, as exported | |
| Antenna mount | Base down, as exported | Blade rakes ≤34° from vertical |
| Standoff | Standing up | |

Every STL is already oriented correctly. **Drop them in the slicer and do not
rotate anything.**

#### If you take one thing from this document

The arm's flat face is the motor mounting surface, and it goes **on the bed**.

- All the arm's taper is on the *other* side, so the cross-section only shrinks
  going upward. No overhangs, no supports, nothing to clean up.
- Bed contact is the entire 111 x 26 mm plan area. It will not lift.
- The bending fibres end up as continuous perimeters running the full length.
- Layer adhesion only sees transverse shear (~0.6 MPa against a bond good for
  25+ MPa).

Print an arm standing on edge or on its end and it will snap at the root on
the first hard landing, because you will have put the layer boundaries square
across the tension face.

### Print order

Print **one arm first** and check it: the two root holes should pass an M3
freely, the motor pad should sit flat on glass with no rock, and the pad should
measure 4.0 mm. If that arm is good, print the other three plus everything else.

Total print time is roughly 7-9 hours for the full set. About 80 g of filament.

### Post-print

- Run a **2 mm drill by hand** through the camera cage's M2 pivot holes. They
  are horizontal and will bridge with slight droop — the only hole on the whole
  frame that needs cleanup.
- Test-fit an M3 through the arm and plate holes. If tight, run a 3.3 mm drill
  through rather than forcing the bolt; forcing it splits the layers.
- Deburr the motor pads so the motors seat flat.

---

## Part 2: Assembly

### Vertical stack-up, for reference

```
   0.0 .. 4.0    bottom plate
   3.2 .. 17.2   arms (seated 0.8 mm down into the locating grooves)
  17.2 .. 37.2   M3x20 standoffs; ESC and FC live in this space
  37.2 .. 40.2   top plate
  40.2 ..        battery
  ~43.2          prop disc
```

### Order

**1. Arms to bottom plate.**
Each arm drops into its 0.8 mm locating groove — that groove is what makes the
arms land straight without a jig, so make sure each one is properly seated
before bolting. Two M3 per arm, both from underneath, **washer under every
head**:

- inner bolt (R = 21.6 mm) — **M3x35**, this is also the stack column
- outer bolt (R = 38 mm) — **M3x25**, this also carries the top-plate standoff

Do not fully tighten yet.

**2. Standoffs.**
Thread the four aluminium M3x20 standoffs onto the four M3x25 outer bolts, on
top of the arms. Now tighten all eight arm bolts, working diagonally.

**3. Motors.**
Four **M3x8** each, up through the pad into the motor. The pad is 4.0 mm, so
the screw reaches 4 mm into the bell. **Nothing longer.** Snug, not gorilla —
you are threading into aluminium.

Route the phase wires along the top of the arm and take up the slack through
the 2.6 mm hole at mid-arm with a zip tie.

**4. ESC.**
It sits on top of the four arm roots on its rubber grommets, over the M3x35
bolts. Solder the four motors (order does not matter yet — you fix rotation in
software), then the XT60 pigtail, then the **470 µF capacitor directly across
the XT60 pads**. On 6S the capacitor is not optional; without it, switching
spikes will eventually take out the ESC.

Feed the XT60 lead down through the slot at the rear of the bottom plate as
strain relief.

**5. FC.**
Nylon spacers above the ESC, then the FC, then M3 nylocs. Arrow points forward
(+X, toward the camera). Connect the ESC ribbon, RX, VTX, and camera.

**6. Camera cage.**
Two **M3x12** up through the bottom plate, nylocs on top of the cage base.
Camera drops between the walls, one **M2x8** per side. Set the tilt as you
tighten — **30-40°** for this power class. Friction on the M2s is what holds
the angle; that is how every micro camera mount works.

**7. Antenna mount.**
Same two-bolt pattern at the rear. Antenna shaft through the 6 mm bore, zip tie
through the cross hole. The bore already points the antenna up and aft, clear
of the rear prop discs.

**8. Top plate.**
Four **M3x8** down into the standoff tops. Tie the RX and VTX leads through the
four 4 mm holes near the corners — those sit outboard of the battery footprint
so nothing gets crushed.

**9. Battery.**
Strap through the two slots. Pack centred fore-aft; the CG wants to be at the
frame centre.

### Before the first flight

**Props off for all of this.**

1. Flash/verify Betaflight. Set the correct motor order and directions in the
   Motors tab.
2. Bind the RX. Check failsafe actually cuts the motors.
3. Check the accelerometer and that the FC arrow really is forward.
4. Set the VTX band and power. **25 mW indoors**, and never power the VTX
   without an antenna — it will cook the output stage.
5. Set a **3.5 V/cell** low-voltage warning. A 6S 1050 at 100 A does not last
   long and racing packs do not like being run flat.
6. Props on last, and check each direction against the Betaflight diagram.

### Expect to break things

The camera cage and the antenna mount are **designed as fuses**. They hang off
the nose and tail on two bolts each and are meant to snap before they lever the
bottom plate. That is 6-7 g of filament each. Print a spare of both with the
first batch, and a spare arm.

If you break the bottom plate, you hit something hard enough that a carbon
frame would have bent its arms instead.
