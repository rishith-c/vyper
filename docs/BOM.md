# Peregreen-X — Bill of Materials, under $150

Every line carries the **exact dimensions the CAD is cut to**. Substituting a
part with different dimensions means editing the parameter named in the last
column and re-running the script.

Links are **search pages, not single listings** — deliberately. AliExpress
listings churn weekly and a dead link is worse than no link; a search that
still resolves in six months is more useful. Filter by the dimensions in the
table, which are what the CAD is actually cut to.

Prices are typical AliExpress street, July 2026. AliExpress hides item pages
behind a login wall so I could not verify them line by line — treat them as a
budget, not a quote, and check before ordering.

## Section A — the aircraft

| # | Part | **Exact dimensions** | Mass | $ | CAD parameter |
|---|---|---|---|---|---|
| 1 | [2207 motor ×4, **2450KV** (4S)](https://www.aliexpress.com/w/wholesale-2207-2450kv-motor.html) | Ø27.9 × 32.4 mm; **16×16 mm M3** bolt square; M5 shaft; **4.5 mm blind thread depth** (2207s ship for 4–5 mm arms) | 32 g ea | 44 | `MOTOR_PATTERN = 16.0` |
| 2 | [F405 FC + 40A 4in1 ESC stack](https://www.aliexpress.com/w/wholesale-f405-40a-4in1-stack-30.5.html) | ESC **36.0 × 36.0 × 7.5 mm**; FC 36.0 × 36.0 × 6.5 mm; **30.5 × 30.5 M3**; 15 mm stacked | 22 g | 30 | `STACK_PITCH = 30.5` |
| 3 | [4S 1500 mAh LiPo, XT60](https://www.aliexpress.com/w/wholesale-4s-1500mah-lipo-xt60.html) | **75 × 35 × 30 mm** | 165 g | 16 | `R_MAX` (see note) |
| 4 | [Micro FPV camera, 19 mm](https://www.aliexpress.com/w/wholesale-19mm-micro-fpv-camera.html) | **19.0 × 19.0 × 21 mm** body; M2 side pivot, 19 mm across ears | 8 g | 11 | — |
| 5 | [5.8 GHz VTX, 25–400 mW](https://www.aliexpress.com/w/wholesale-5.8g-vtx-400mw-mmcx.html) | **26 × 26 × 6 mm**; MMCX | 8 g | 10 | — |
| 6 | [ExpressLRS 2.4 GHz nano RX](https://www.aliexpress.com/w/wholesale-expresslrs-2.4ghz-nano-receiver.html) | **15 × 11 × 4 mm** | 1.5 g | 8 | — |
| 7 | [5×4.3×3 props, 2 sets (8)](https://www.aliexpress.com/w/wholesale-5x4.3x3-propeller.html) | **127 mm** dia; 5.0 mm bore | 4.5 g ea | 5 | `PROP_DIA` |
| 8 | [M3 hardware assortment](https://www.amazon.com/s?k=m3+socket+cap+screw+assortment+stainless) | — | 40 g | 12 | — |
| 9 | [PETG filament, ~250 g](https://www.amazon.com/s?k=petg+filament+1.75mm) | 1.75 mm | — | 6 | — |
| | | | | **$142** | |

**Why 4S, not 6S.** It is the single cleanest $10 saving, and the 4S pack is
*smaller* — which is the interesting part. See the note below.

## The budget change made the airframe faster

The $200 build was sized around a SpeedyBee ESC at **45.6 × 44 mm** and a 6S
1050 at 76 × 38 × 31 mm. That 44 mm ESC forced a 60 mm body.

The budget stack is **36 × 36 mm** and the 4S 1500 is **75 × 35 × 30 mm**:

```
battery half-diagonal = sqrt(17.5^2 + 15.0^2) = 23.0 mm
required internal radius                      = 23.0 + 1.0 fit = 24.0 mm
required outer radius                         = 24.0 + 2.0 wall = 26.0 mm
```

So `R_MAX` drops **30 → 26 mm**, a **52 mm body instead of 60 mm**. Frontal
area falls from 28.3 to 21.2 cm², **25 % less**. Cheaper parts, slimmer
aircraft — the constraint that set the diameter was the expensive ESC.

## Section B — hardware (line 8)

| Item | Size | Qty | Where |
|---|---|---|---|
| M3 × 8 socket cap | ISO 4762, Ø5.5 head | 16 | Motors. 4.0 mm pad → **4.0 mm engagement** in a 4.5 mm blind hole |
| M3 washer, Ø7 × 0.5 | | 16 | **Under every motor screw** — see note |
| M3 × 20 socket cap | | 4 | Arm root → internal hub |
| M3 × 8 button head | | 4 | Stack → shelf, 30.5 × 30.5 |
| M3 washer | Ø7 × 0.5 | 8 | Frame bolts |
| M2 × 8 | | 2 | Camera pivot |
| XT60 pigtail | 14 AWG, 100 mm | 1 | |
| Capacitor | **470 µF / 35 V**, Ø10 × 20 mm low-ESR | 1 | Across XT60. Not optional |
| Heatshrink / zip ties | | | |

## Motor screws — the numbers

```
pad thickness            4.0 mm
screw M3 x 8             8.0 mm
engagement = 8.0 - 4.0 = 4.0 mm   into a 4.5 mm blind thread
remaining clearance      0.5 mm    -> does NOT bottom out
```

**I previously told you the thread depth was 3.0 mm and to consider M3×6.
That was wrong.** 2207-class motors are built for 4–5 mm carbon arms and ship
M3×8 for exactly this stack-up; their blind holes are 4.5–5 mm. A 4.0 mm pad
with M3×8 is the standard, correct combination. M3×6 would leave only 2 mm of
engagement and is the worse choice.

**Still measure yours before the first build.** Run an M3×8 into a bare motor
by hand: it should turn freely to ~4 mm and stop against thread, not jam. If
it jams early the hole is shallower than spec and you drop to M3×6.

Two things that *are* worth doing, because the pad is PETG and not carbon:

* **Washer under every motor screw.** An M3 socket head is Ø5.5 mm, giving
  15.7 mm² of bearing. At max thrust each screw sees ~4.8 N → 0.3 MPa, which
  is nothing — but vibration cycling a bare head against plastic will slowly
  embed it. A Ø7 washer nearly doubles the seat area for 0.1 g.
* **Blue threadlocker in the motor threads, not the plastic.** The thread is
  aluminium; that is where the locking happens. Never put threadlocker on the
  printed pad.

The screw head seats on a **flat, machined-square pocket ceiling** — the pad
is hollowed from below, so the head bears on a true flat, not on a curved
nacelle surface. There is 2.4 mm of material outboard of each hole.

## NOT included — you cannot fly without these

| Item | $ |
|---|---|
| ELRS radio (RadioMaster Pocket) | 65–95 |
| Analog FPV goggles | 70–160 |
| 4S-capable balance charger | 30–60 |
| LiPo safe bag | 10 |
| | **$175–325** |

If you already own these, $142 is the whole aircraft. If not, the real
first-time cost is **$317–467** and no BOM can change that.
