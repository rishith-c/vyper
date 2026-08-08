# VYPER-F4 — custom flight controller PCB

A dimensionally verified FC study plus a true-footprint, true-net unrouted
review board for the VYPER airframe.

![dimensions](../pcb/vyper_f4_dimensions.png)

## What exists and what doesn't — read this first

| Done | Not done |
|---|---|
| Board outline, cut to the fuselage | Reviewed graphical KiCad schematic |
| 30.5×30.5 Φ4.0 grommet holes | Copper routing |
| Major ICs and all interfaces placed with true footprints | Final passive placement |
| Courtyard / hole / pad interaction checks | Ordering files (gerbers/BOM/CPL) |
| 59-net / 74-component authored connectivity | 183 routed connections |
| All 242 authored nodes reach physical pads | Production approval |

`vyper_f4.kicad_pcb` remains the mechanical drawing. The generated
`vyper_f4_unrouted.kicad_pcb` carries all real footprints and nets. KiCad finds
no shorts, clearance failures, courtyard overlaps, edge errors or footprint
errors among placed parts, but 57 passives are staged and 183 connections are
unrouted. It is therefore **not an orderable FC**.

## The AI-tool landscape (verified August 2026)

| Tool | What it actually does | Use here? |
|---|---|---|
| [Quilter](https://www.quilter.ai/product) | Generates placement/routing candidates from a schematic and constraints, with physics checks. | Candidate after schematic review |
| [DeepPCB](https://deeppcb.ai/) | AI placement/routing with native KiCad support; its own site requires qualified review. | Alternative candidate |
| [Flux](https://www.flux.ai/p) | AI-assisted schematic and PCB design environment. | Review aid, not qualification |
| KiCad 9 + this repo | Deterministic generation from a Python layout file | What we did |

None of them design a *flight controller* for you: every tool above starts
from a schematic and placement intent. The intelligence in an FC layout is the
placement rules — which is exactly the part encoded and tested here.

## Design principles applied (and where each came from)

Sources: [Betaflight manufacturer design guidelines](https://betaflight.com/docs/development/manufacturer/manufacturer-design-guidelines),
[STM32F405 data sheet](https://www.st.com/resource/en/datasheet/stm32f405rg.pdf),
[ICM-42688-P data sheet](https://invensense.tdk.com/wp-content/uploads/2020/04/ds-000347_icm-42688-p-datasheet.pdf), and
[TPS54360 data sheet/product page](https://www.ti.com/product/TPS54360).

1. **Gyro near the rotation centre, on the board axes.** ICM-42688-P at
   (0, +2.5) — 2.5 mm off centre, limit 4. A FWD axis mark is on the silk
   because a rotated gyro is a config error you chase for a week.
2. **Gyro ≥ 10 mm from anything that switches.** The buck inductor's field
   couples into the MEMS structure and reads as vibration that no filter
   fully removes. Measured on this board: **10.7 mm**, checked.
3. **Gyro-to-MCU SPI under 10 mm.** Courtyard gap here: ~0.3 mm.
4. **Soft mounting is a requirement, not a preference.** Hard-bolting the
   board flexes it and permanently shifts gyro bias — hence Φ4.0 holes for
   M3 grommets and a Φ8 keepout ring at each corner *on both faces*.
5. **Solid ground under the IMU; 4-layer stack** (sig / GND / PWR / sig)
   when routed — a continuous plane under high-frequency parts is the
   cheapest EMI fix there is.
6. **Power entry short and fat, cap at the connector.** The FC now uses a
   60 V TPS54360 reference-design buck; bulk low-ESR capacitance still belongs
   at the ESC battery entry, close to the switching current loop.
7. **USB and ESC service harnesses on the bottom face** — the ESC harness
   plugs straight up from below; a removable four-wire JST-SH-to-USB-C pigtail
   faces the open tail. This avoids a through-hole USB shell colliding with the
   LQFP64 and avoids a drag-producing side hatch.

## Why the board is shaped by the fuselage

Two findings the checks enforce forever:

- **R5 corners preserve service clearance.** The 6S battery enlarged the
  cavity radius to 26.5 mm, so a square 36 mm board now fits at a 25.46 mm
  half-diagonal, but leaves only 1.04 mm radial allowance. R5 reduces corner
  reach to 23.38 mm and leaves 3.12 mm for wire and assembly tolerance.
- **Duplicate corner motor pads were rejected.** The tested 8-pin ESC harness
  already carries M1–M4. Extra corner pads entered grommet/part keepouts and
  added stubs, so the physical design removes them instead of hiding the clash.

## ESC: custom EVT architecture, not flight hardware

The requested custom ESC is now specified in
[`ESC_ARCHITECTURE.md`](../pcb/ESC_ARCHITECTURE.md) and mechanically encoded in
`vyper_esc_layout.py`. It uses four AM32-supported AT32F421 MCUs, four TI
DRV8323 smart gate drivers and 24 Infineon 60 V MOSFETs.
`vyper_esc_schematic.py` now emits the 159-net electrical design, and
`vyper_esc_unrouted_gen.py` transfers all 195 references and 715 authored
netlist nodes to true physical pads. The ESC was enlarged from the rejected
36 mm packing study to a 43×43 mm R12 outline; its 25.44 mm corner reach still
fits the 26.5 mm fuselage cavity. The generator intentionally stages 142
passives outside the outline and contains zero tracks/zones. KiCad now finds
no shorts, clearance failures, courtyard overlaps, edge errors, or footprint
errors among the placed parts; its 499 unconnected items are an explicit
routing backlog, not a release. It remains an EVT design until placement,
routing, independent review and the full
current-limited/dyno test matrix pass. The repository does not claim it cannot
catch fire; no responsible design can make that claim before hardware validation.

## Reproduce

```bash
cd pcb
python3 vyper_f4_gen.py                 # emit vyper_f4.kicad_pcb
python3 test_vyper_f4.py                # 15 interaction checks
../.venv/bin/python vyper_f4_schematic.py # emit authored KiCad netlist
python3 test_vyper_f4_netlist.py        # connectivity/resource assertions
../.venv/bin/python vyper_f4_drawing.py # dimensioned drawing
/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
  vyper_f4_unrouted_gen.py               # true footprints/nets, still unrouted
/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
  test_vyper_f4_board.py                 # 74 refs / 242 nodes transferred
python3 test_vyper_f4_drc.py              # rejects hidden placement/copper errors
/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
  vyper_esc_unrouted_gen.py              # true footprints/nets, still unrouted
/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
  test_vyper_esc_board.py                # 195 refs / 715 nodes transferred
python3 test_vyper_esc_drc.py             # rejects hidden placement/copper errors
kicad-cli pcb render --side top --output top.png vyper_f4.kicad_pcb
```

Both `.kicad_pcb` files open directly in KiCad 9. Only the `_unrouted` board
contains the authored electrical nets, and it must be placed and routed before
it can pass the release gates.
