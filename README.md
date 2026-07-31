# VYPER-5W

A fully 3D-printed high-speed quadcopter in the style of the **Peregreen V4**
(the 657 km/h Guinness record holder): a rocket fuselage with the battery and
stack buried inside, and two swept arrowhead **wing panels** carrying the
motors. Not arms — the motors sit on the wing, which is drawn around them.

Seven printed parts, no supports, no carbon fibre, Elegoo Neptune 4 in PETG.

![VYPER-5W](docs/img/v_iso.png)

**Printed frame 168 g. AUW 613 g. Static thrust ~6.4 kg. T/W 10.4:1.**

**41 automated checks pass.** Full output in [docs/VERIFY_REPORT.txt](docs/VERIFY_REPORT.txt)
and [docs/AERO_REPORT.txt](docs/AERO_REPORT.txt).

The earlier flat-plate version is in git history (`git log`) if you want the
lighter, cheaper-to-crash airframe.

---

## Fit is checked, not claimed

Every bought part is modelled at its spec-sheet size in
[cad/components.py](cad/components.py), and the bays are **carved out of the
structure using those solids** rather than drawn by hand and hoped to be big
enough. [cad/verify.py](cad/verify.py) then boolean-tests 39 conditions:
every component against every printed part, every component against the
fuselage cavity, everything against the prop discs, every part against every
other, and every part against the bed.

It earned its keep. It caught, in order:

| What | How it showed up |
|---|---|
| Pylon backing ribs through the battery and stack bays | 9,363 and 8,361 mm³ of clash |
| Camera 6 mm too far forward for the nose taper | 19 mm square needs 13.5 mm half-diagonal; nose only gives 11.5 at X=98 |
| Fin spigot punching out the bottom of the tail | tail radius is 11 mm there, spigot was 20 |
| Nose inlet larger than the nose | a 22 mm hole at X=104 where the radius is 10.6 |
| Stack posts floating in mid-air | exported as 3 disconnected solids |
| Saddle joints biting into the shell when rotated to another station | 147 mm³, fixed with 0.6 mm clearance |
| Two 0.0 mm³ boolean specks on the canopy parting edge | connectivity check |

**Run it after any change:**

```bash
cd cad && ../.venv/bin/python verify.py
```

### This means fit to *these* parts

The design is cut to a **SpeedyBee F405 V4 ESC (45.6 × 44 × 8 mm)** and a
**CNHL Ultra Black 6S 1050 (76 × 38 × 31 mm)**. The 44 mm ESC width is what
sets the 62 mm fuselage diameter — it is the widest rigid object in the
aircraft and it cannot be bent around anything.

Different stack or pack? Edit the dimensions in `components.py`, re-run
`verify.py`, regenerate. That is the whole point of the setup.

---

## What the tests say

Run `python cad/aero.py` and `python cad/verify.py`. The headline results:

| | |
|---|---|
| Blade frontal silhouette (measured) | 34.8 cm² |
| Arms | two 9×18 mm blades, half-lapped, crossing at 77° |
| Total drag area (CdA) | 44.5 cm² |
| vs. a conventional open racer | **41 % less drag** |
| Top speed | **149 km/h — limited by prop pitch, not thrust** |
| Hover download from the blades under the discs | **0.5 % (31 g)**, measured by boolean |

Three findings worth acting on:

1. **The motors are now 79 % of total drag.** Once the body and arms are
   faired, four bare 28 mm bells in crossflow dominate everything else. Motor
   fairings are the single highest-value thing left to add — that is exactly
   what Peregreen does.
2. **Top speed is prop-pitch limited.** At ~30,300 rpm a 5x4.3 has a 55 m/s
   pitch speed, so ~41 m/s is the realistic ceiling and there is 62.8 N of
   thrust available against 4.4 N of drag. Fairing the airframe does **not**
   raise the ceiling. It cuts the power needed to sit at it by 44 %, which
   buys flight time and less voltage sag.
3. **Rotor download is now negligible.** Two thin blades block 8.2 % of the
   disc area against 36 % for the wing panels they replaced — 0.5 % of thrust
   instead of 2.2 %.

## Why this shape, honestly

You asked for high speed, and this is the right answer for it — with a caveat
worth stating plainly.

**The real win is burying the battery and fairing the arms.** On a
conventional racer those are most of the drag: an exposed brick of LiPo, four
flat plates edge-on, and an open stack. That win applies at any attitude.

**The fuselage itself does less than it looks like it should.** A quad at speed
pitches over 40–60°, so a body aligned with the airframe X axis sits at a large
angle of attack and stops behaving like a streamlined body. That is exactly why
conventional racers have no fuselage. The fix is motor tilt — cant the pads
nose-down so the airframe makes thrust while the body stays closer to the flow.
`MOTOR_TILT` exists in [cad/vy_params.py](cad/vy_params.py) and **ships at 0**,
because tilt re-cuts the pylon-to-fuselage joint at a compound angle and needs
`board_align_pitch` set in Betaflight. Raise it for a dedicated speed airframe
and re-run verify.

So: meaningfully faster than the plate version. Not the 40 % a wind-tunnel-
aligned body would give.

**It costs 191 g.** 267 g printed against 76 g for the flat-plate frame. T/W
falls from 11.8 to 9.0, still firmly in racing territory.

---

## Print orientation is still the whole design

**Each wing panel is flat-topped over its entire area.** That one plane is
simultaneously the bed face and *both* motor mounting faces; every bit of
fairing hangs below it, so the section only ever shrinks going up and there is
no overhang anywhere on the part.

That also makes hollowing free. The panel is a shell — 2.2 mm skin, 1.8 mm
perimeter, six chordwise ribs, and a lightening bay between the motors — and
because the belly is the **last** surface laid, an open underside needs no
bridging at all. That took each panel from 92 g solid to 31 g.

The shells split so nose and tail cones print **open end down** (domes,
shrinking to the tip) and the main body splits horizontally at Z = +13 so both
halves print **cut face down**. The fin is separate because a fin moulded into
the tail cone would be a horizontal plate hanging in mid-air.

**Nothing needs supports.** [cad/tolerance_coupon.py](cad/tolerance_coupon.py)
includes an overhang fan so you can confirm that on your own machine rather
than taking my word for it.

---

## Specs

| | |
|---|---|
| Layout | **stretched X 1.26:1** — 176 mm fore-aft / 140 mm lateral, 225 mm diagonal |
| Fuselage | 320 mm long, 62 mm max dia, fineness 5.2 |
| Arms | 2 crossed blades, 9×18 mm, 255 mm — **print diagonally** |
| Motors | 2207 1750KV, 6S, 5x4.3x3 |
| Battery | 6S 1050, **inside the fuselage**; the canopy is the retainer |
| Printed frame | 168 g (7 parts, 7 prints) |
| AUW | 613 g |
| Thrust-to-weight | 10.4:1 |
| Min prop tip gap | 13.0 mm (lateral pair, at the 127 mm prop minimum) |

Cooling is **not optional**: annular nose inlet around the camera, ducted the
length of the cavity over the stack, out through the tail, with side gills as
the local exit. Seal these up and a 55 A ESC in a closed tube will
thermal-throttle.

---

## Files

| Part | Qty | Mass | STL |
|---|---|---|---|
| Fuselage lower (structure) | 1 | 68 g | [stl/fuselage_lower.stl](stl/fuselage_lower.stl) |
| Fuselage upper (canopy) | 1 | 24 g | [stl/fuselage_upper.stl](stl/fuselage_upper.stl) |
| Nose cone | 1 | 10 g | [stl/nose_cone.stl](stl/nose_cone.stl) |
| Tail cone | 1 | 7 g | [stl/tail_cone.stl](stl/tail_cone.stl) |
| Tail fin (carries the VTX antenna) | 1 | 15 g | [stl/tail_fin.stl](stl/tail_fin.stl) |
| Wing panel, left | 1 | 31 g | [stl/wing_l.stl](stl/wing_l.stl) |
| Wing panel, right | 1 | 31 g | [stl/wing_r.stl](stl/wing_r.stl) |
| **Tolerance coupon — print this FIRST** | 1 | 39 g | [stl/tolerance_coupon.stl](stl/tolerance_coupon.stl) |

Two wing hands, mirror images of each other.

**Print [tolerance_coupon.stl](stl/tolerance_coupon.stl) before anything else.**
It carries M3 and M2 hole ladders, a saddle gauge cut to the real fuselage
radius, the real 16×16 motor pattern in a real 4.0 mm pad, a wall-thickness
ladder, bridge tests at both bore sizes used, and an overhang fan. Twenty
minutes and 39 g, against nine hours for a fuselage half that might not fit.

Read next: [docs/BOM.md](docs/BOM.md), [docs/BUILD.md](docs/BUILD.md).

Safety: 6.4 kg of thrust behind four unguarded blades at 30,000 RPM. Props off
for every bench test.
