# VYPER bill of materials

Price snapshot: 8 August 2026, USD, before tax and shipping. Marketplace prices
change by region and coupons; verify the final cart. The **$189 target** below
uses a purchased FC/ESC stack. A one-off custom FC plus custom ESC cannot
honestly fit inside the same $200 aircraft budget.

## Prototype aircraft target

| Qty | Part and source | CAD / electrical envelope | Mass | Budget |
|---:|---|---|---:|---:|
| 4 | [T-Motor Velox V2207 V3 1950KV — official](https://www.t-hobby.com/products/tmotor-velox-v2207-v3-motor), [AliExpress listing](https://www.aliexpress.us/item/1005011666448428.html) | Ø27.5×31.8 mm; 16×16 M3; 6S; 45 A published bench point | 37.1 g ea | $57.20 |
| 1 | [F405 55–60 A 6S stack — AliExpress search](https://www.aliexpress.us/w/wholesale-f405-60a-stack-30.5.html), [Amazon SpeedyBee reference](https://www.amazon.com/dp/B0DSW7TCYV) | **maximum 36×36 mm**, R5 preferred; 30.5×30.5 M3; stack height ≤16 mm | 30 g allowance | $42.00 |
| 1 | [DOGCOM Pro 1380 mAh 180C 6S — official specification](https://dogcombattery.com/products/dogcom-1380mah-180c-6s-222v), [AliExpress search](https://www.aliexpress.us/w/wholesale-dogcom-1380mah-6s.html) | 81×39×33 mm; 209 g; XT60; claimed 180C must be measured | 209 g | $30.00 |
| 2 sets | [HQProp 5×5V1S — official](https://hqprop.com/hq-durable-prop-5x5v1s-2cw2ccw-poly-carbonate-p0182.html), [AliExpress search](https://www.aliexpress.us/w/wholesale-hqprop-5x5v1s.html) | 127 mm; 5-inch pitch; 5 mm hub; 2 CW + 2 CCW per set | 3.33 g ea | $5.98 |
| 1 | [19 mm analog camera/VTX combo — Amazon search](https://www.amazon.com/s?k=5.8ghz+aio+fpv+camera+vtx+19mm), [AliExpress search](https://www.aliexpress.us/w/wholesale-19mm-aio-fpv-camera-vtx.html) | camera ≤19×19×21 mm; VTX supply compatible with FC BEC | 12 g allowance | $15.00 |
| 1 | [2.4 GHz ELRS nano RX — AliExpress listing](https://www.aliexpress.us/item/1005007730545007.html), [Amazon search](https://www.amazon.com/s?k=expresslrs+2.4ghz+nano+receiver) | ≤15×11×4 mm; CRSF | 1.5 g | $12.95 |
| 1 lot | [M3/M2 hardware — Amazon](https://www.amazon.com/s?k=m3+m2+socket+head+screw+washer+heat+set+insert), [AliExpress](https://www.aliexpress.us/w/wholesale-m2-m3-screw-assortment.html) | exact schedule below | 40 g allowance | $10.00 |
| 1 lot | [12/20/26 AWG silicone wire, XT60, heatshrink — Amazon](https://www.amazon.com/s?k=silicone+wire+xt60+heatshrink), [AliExpress](https://www.aliexpress.us/w/wholesale-silicone-wire-xt60-kit.html) | motor: 20 AWG; battery: 12 AWG; signals: 26 AWG | included | $10.00 |
| 1 | [470–1000 µF 50 V low-ESR capacitor — Amazon](https://www.amazon.com/s?k=1000uf+50v+low+esr+capacitor), [AliExpress](https://www.aliexpress.us/w/wholesale-1000uf-50v-low-esr.html) | mounted directly at ESC battery pigtail | 8 g allowance | $4.00 |
| 300 g | [PETG or PA-CF filament — Amazon](https://www.amazon.com/s?k=petg+filament+1.75mm) | 1.75 mm; slicer estimate 257.1 g plus purge/test allowance; final material requires coupon/proof test | — | $6.00 |
| | **Target before tax/shipping** | | | **$193.13** |

The $42 stack line is a budget gate, not a recommendation to buy an unknown
board. If a documented genuine 55–60 A stack cannot be delivered while keeping
the cart below $200, raise the budget; do not substitute an under-rated ESC.

## Exact hardware schedule

| Qty | Hardware | Location / stack-up |
|---:|---|---|
| 16 | ISO 4762 M3×8 socket cap | motors; 4 mm printed pad leaves 4 mm nominal thread engagement |
| 16 | M3 washer, Ø7×0.5 | under every motor screw |
| 4 | M3×20 socket cap + washer + locknut | arm roots through the internal hub; final length to be trimmed after physical coupon fit |
| 4 | M3×25 stack screws | ESC/FC/grommet/standoff/shelf assembly; choose final length from purchased stack |
| 8 | M3 silicone grommets | FC and ESC vibration/clearance stack |
| 3 | M2×10 low-profile screw | radial tail-cap retention |
| 3 | M2 heat-set insert, Ø3.5–3.6×4 mm | printed tail-cap internal bosses |
| 2 | M2×8 + locknut | camera pivot; shell window/mount still open CAD work |

The repository includes the exact M3×8 ISO 4762 STEP from
[STEP.PARTS](https://www.step.parts/parts/iso4762_socket_head_cap_screw_m3x8)
at `cad/vendor/iso4762_socket_head_cap_screw_m3x8.step`. Electronics did not
have exact downloadable STEP matches, so their manufacturer dimensions are
modeled as conservative envelopes rather than disguised generic geometry.

## Custom-board development cost

The custom ESC's active power/control subset currently screens at about
**$65.15**: 24 Infineon MOSFETs, four TI drivers, four AT32 MCUs, the 60 V
logic regulator/inductor, current-sum amplifier and four high-power shunts.
That still excludes the remaining passives, PCB, assembly, stencil and
minimum-order quantities. It is a separate EVT program, not part of the $193
prototype cart. See `pcb/ESC_ARCHITECTURE.md`.

Radio, goggles, charger, LiPo-safe storage, radar/GNSS instrumentation and
test shielding are also not included in the aircraft total.
