# VYPER-5W

A fully 3D-printed high-speed quadcopter in the style of the **Peregreen V4**
(the 657 km/h Guinness record holder): a rocket fuselage with the battery and
stack buried inside, and two swept arrowhead **wing panels** carrying the
motors. Not arms — the motors sit on the wing, which is drawn around them.

Seven printed parts, no supports, no carbon fibre, Elegoo Neptune 4 in PETG.

![VYPER-5F](docs/img/asm_iso.png)

*Blue discs are true 127 mm prop keep-out volumes, not parts.*

**Printed frame 267 g. AUW 711 g. Static thrust ~6.4 kg. T/W 9.0:1.**

**39 automated checks pass.** Full output in [docs/VERIFY_REPORT.txt](docs/VERIFY_REPORT.txt)
and [docs/AERO_REPORT.txt](docs/AERO_REPORT.txt).

The earlier flat-plate version is in git history (`git log`) if you want the
lighter, cheaper-to-crash airframe.

---

## Fit is checked, not claimed

Every bought part is modelled at its spec-sheet size in
[cad/components.py](cad/components.py), and the bays are **carved out of the
structure using those solids** rather than drawn by hand and hoped to be big
enough. [cad/verify.py](cad/verify.py) then boolean-tests all 46 conditions:
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
| Wing planform (measured off the solids) | 234 cm² |
| Speed at which the wings carry the **whole aircraft** | 30 m/s (108 km/h) |
| Total drag area (CdA) | 41.8 cm² |
| vs. a conventional open racer | **44 % less drag** |
| Top speed | **149 km/h — limited by prop pitch, not thrust** |
| Hover download from the wing under the discs | 2.4 % (155 g), measured by boolean |

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
3. **The wings genuinely work.** At 108 km/h they carry 100 % of the weight,
   which is what makes this different from bolting fairings onto a quad.

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

**It costs 112 g.** 188 g printed against 76 g for the plate frame. T/W drops
from 11.8 to 10.1, which is still firmly in racing territory.

---

## Print orientation is still the whole design

Same argument as before, applied to a fairing.

**The pylon is flat-topped over its entire length** — strut and nacelle share
one plane at the motor mounting height, and every bit of fairing hangs below
it. That flat top is both the bed face and the motor mounting face, the section
only ever shrinks going up, and the bending fibres are continuous perimeters
root to tip. **This is why the pylons leave the fuselage at Z = +16, on the
shoulder, rather than at the waterline** — a pylon rising from the waterline to
the pad would put a 77° overhang along its whole upper surface and you would be
printing primary structure on supports.

The rounded belly comes from lofting one plan outline downward with a growing
inset, so strut and nacelle round off together and monotonic shrink is
guaranteed by construction.

The shells split three ways for the same reason: nose and tail cones print
**open end down** (domes, section shrinks to the tip), the main body splits
horizontally at Z = +13 so both halves print **cut face down**, and the fin is
separate because a fin moulded into the tail cone would be a horizontal plate
hanging in mid-air.

**Nothing needs supports.**

---

## Specs

| | |
|---|---|
| Class | 5" / 220 mm wheelbase, true X |
| Fuselage | 254 mm long, 62 mm max dia, fineness 4.1 |
| Motors | 2207 1750KV, 6S |
| Battery | 6S 1050, **inside the fuselage**; the canopy is the retainer |
| Printed frame | 188 g (7 parts, 9 prints) |
| AUW | 632 g |
| Static thrust | ~6.4 kg |
| Thrust-to-weight | 10.1:1 |
| Adjacent prop tip gap | 28.6 mm |

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
| Pylon hand A (45° and 225°) | 2 | 17 g | [stl/pylon_a.stl](stl/pylon_a.stl) |
| Pylon hand B (315° and 135°) | 2 | 17 g | [stl/pylon_b.stl](stl/pylon_b.stl) |

Two pylon hands, not one: the nacelle is streamwise while the strut is swept,
so front-left and rear-left are mirror images rather than rotations.

Read next: [docs/BOM.md](docs/BOM.md), [docs/BUILD.md](docs/BUILD.md).

Safety: 6.4 kg of thrust behind four unguarded blades at 30,000 RPM. Props off
for every bench test.
