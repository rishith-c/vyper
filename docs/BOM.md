# VYPER-5F — Bill of Materials

> **The airframe is cut to specific parts.** Bays are carved from the actual
> component solids in `cad/components.py`, so the two below are not
> interchangeable with anything of a different size without editing that file
> and re-running `cad/verify.py`:
>
> * **SpeedyBee F405 V4 stack** — ESC 45.6 x 44 x 8 mm, FC 41.6 x 39.4 x 7.8 mm,
>   16.1 mm assembled. The 44 mm ESC width sets the 62 mm fuselage diameter.
> * **CNHL Ultra Black 6S 1050** — 76 x 38 x 31 mm, 180 g. It drops into a
>   31 mm bay and the canopy closes on it, so there is no strap.
>
> A cheaper AliExpress stack is usually *smaller* than the SpeedyBee, so it will
> fit the bay — but check its width against 44 mm before ordering.

## Read this first

**"Under $200" covers the aircraft plus one battery.** It does not cover a
radio, goggles, or a charger. You cannot fly without those three, and they add
**$180-300**. They are listed at the bottom as Section C.

**The $200 target only works at AliExpress prices.** Buying the same build from
US retailers costs about **$306**. Both columns are below.

### On the prices

Prices marked **(verified)** were checked against live listings in July 2026 and
the source is linked. Prices marked *(est.)* are typical AliExpress street
prices — AliExpress puts item pages behind a login wall, so I could not confirm
those directly. **Treat the est. column as a budgeting guide, not a quote.**
AliExpress pricing also swings ±30% with coupons and sale events.

---

## Section A — the aircraft (AliExpress budget path)

| # | Item | Spec that matters | Qty | Est. |
|---|---|---|---|---|
| 1 | 2207 brushless motors | **1750KV** (6S), 16x16 M3 mount, M3 shaft | 4 | $45-55 |
| 2 | F405 FC + 4in1 ESC stack | **30.5x30.5**, 3-6S, ≥45 A, BLHeli_S/AM32 | 1 | $35-45 |
| 3 | 6S 1050 mAh LiPo | XT60, ≥100C, ~85x34x30 mm | 1 | $22-30 |
| 4 | Micro FPV camera | **19 mm** body, analog, single M2 side pivot | 1 | $12-18 |
| 5 | 5.8 GHz VTX | 25-600 mW switchable, MMCX or SMA | 1 | $10-15 |
| 6 | ExpressLRS 2.4 GHz RX | nano, UART | 1 | $7-11 |
| 7 | 5x4.3x3 props | 5 mm bore, tri-blade | 8 (2 sets) | $4-6 |
| 8 | Hardware kit (below) | | 1 | $10-15 |
| 9 | PETG filament | ~350 g incl. a failed print | | $7 |
| | | | **Total** | **$150-200** |

**Budget midpoint: ~$174.**

### The same build at US retail (verified)

| Item | Product | Price |
|---|---|---|
| Motors x4 | [iFlight XING2 2207 1750KV](https://shop.iflight.com/XING2-2207-4S-6S-FPV-Motor-Unibell-Black-for-Nazgul-Evoque-F5-pro1610) @ $22.09 | $88 |
| Stack | [SpeedyBee F405 V4 BLS 55A 30x30](https://www.speedybee.com/speedybee-f405-v4-bls-55a-30x30-fc-esc-stack/) | $70 |
| Battery | [CNHL Ultra Black 6S 1050 150C](https://pyrodrone.com/products/cnhl-ultra-black-series-1050mah-22-2v-6s-150c-lipo-battery-xt60) (180 g) | $42 |
| RX | [RadioMaster RP1 V2 ELRS](https://radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver) | $19 |
| Camera, VTX, props, hardware, filament | | ~$87 |
| | | **~$306** |

Alternate battery, also verified:
[Auline EX 6S 1050 120C](https://www.racedayquads.com/products/auline-ex-22-2v-6s-1050mah-120c-lipo-battery-xt60), $43.49, 193.6 g.

---

## Section B — hardware (line 8, broken out)

Buy an **M3 stainless socket-cap assortment** and an **M3 nyloc + washer
assortment**; that is cheaper than the individual sizes and you will want the
spares. Quantities below are what the airframe consumes.

| Item | Qty | Where it goes |
|---|---|---|
| M3 x 20 socket cap | 16 | Pylon flanges: 4 per pylon, through the shell into the backing ribs |
| M3 x 10 button head | 4 | Canopy → lower shell |
| M3 x 12 button head | 4 | Nose cone and tail cone → main body |
| M3 x 12 button head | 2 | Tail fin → tail cone |
| M3 x 8 button head | 4 | Stack → posts (self-tapping into printed bosses) |
| M3 washer | 8 | **Under every head.** Bearing in printed plastic is the weak link |
| M3 x 8 motor screws | 16 | Usually ship with the motors — see the warning below |
| M2 x 8 | 2 | Camera pivot — usually ships with the camera |
| XT60 pigtail, 14 AWG | 1 | |
| 470 µF / 35 V low-ESR capacitor | 1 | Across the XT60. **Not optional on 6S** |
| Heatshrink, zip ties | | |

### The motor screw warning

The nacelle is 17 mm deep, so the belly is hollowed out to leave a **4.0 mm**
pad under the motor, so an M3x8 reaches exactly 4 mm into the
motor. **Do not use anything longer.** A screw that is too long punches into the
windings and destroys a brand-new motor — it is the single most common way
people kill their first set. If your motors ship with M3x6, use those and the
pad still holds fine.

---

## Section C — ground equipment (NOT in the $200)

You need all three. There is no way around it.

| Item | Budget option | Typical |
|---|---|---|
| Radio (ELRS, must match your RX) | RadioMaster Pocket / Boxer | $65-130 |
| FPV goggles (analog) | Skyzone / Eachine budget box goggles | $70-160 |
| LiPo charger (must do 6S balance) | ISDT / HOTA 300 W class | $35-70 |
| LiPo safe bag | | $10 |
| | | **$180-370** |

Buy the radio and RX **as a matched pair on ExpressLRS**. Mismatched protocols
are the most common reason a first build never arms.

---

## Substitutions worth knowing

**4S instead of 6S.** Use **2207 2400-2550KV** motors and a 4S 1500 mAh pack.
Saves maybe $8 total, costs you meaningful top speed. Only worth it if you
already own 4S packs and a 4S charger. The frame does not change.

**2306 instead of 2207.** Same 16x16 M3 pattern, drops straight in. Slightly
more torque, slightly heavier.

**Digital video (HDZero / DJI / Walksnail).** Do not try. The cheapest digital
VTX alone is most of this budget, and the air units do not fit the 19 mm camera
cage. Analog is what makes a sub-$200 racer possible.

**Printed standoffs.** [stl/standoff.stl](../stl/standoff.stl) exists, but it
is a plain spacer with no thread — you would need a single M3x45 all the way
through and a nyloc on top, and it crushes if you overtighten. The aluminium
set is $4. Buy the aluminium set.

---

## Filament

**PETG.** Tougher on impact than PLA and it does not go brittle in a hot car,
which matters for a part that lives in the sun and gets thrown at the ground.
PLA+ works and prints easier but cracks more readily in cold weather. ASA/ABS
are better again but warp badly on the Neptune 4's open frame.

One 1 kg spool prints roughly a dozen complete airframes. Budget 250 g for the
first build including one failure.

---

Sources for verified prices:
[SpeedyBee](https://www.speedybee.com/speedybee-f405-v4-bls-55a-30x30-fc-esc-stack/),
[iFlight](https://shop.iflight.com/XING2-2207-4S-6S-FPV-Motor-Unibell-Black-for-Nazgul-Evoque-F5-pro1610),
[RadioMaster](https://radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver),
[Pyrodrone](https://pyrodrone.com/products/cnhl-ultra-black-series-1050mah-22-2v-6s-150c-lipo-battery-xt60),
[RaceDayQuads](https://www.racedayquads.com/products/auline-ex-22-2v-6s-1050mah-120c-lipo-battery-xt60)
