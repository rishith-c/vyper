# VYPER-F4 — custom flight controller PCB

A placement-complete, dimensionally verified KiCad floorplan for the VYPER
airframe. **15 automated interaction checks pass** (`pcb/test_vyper_f4.py`).

![dimensions](../pcb/vyper_f4_dimensions.png)

## What exists and what doesn't — read this first

| Done | Not done |
|---|---|
| Board outline, cut to the fuselage | Reviewed graphical KiCad schematic |
| 30.5×30.5 Φ4.0 grommet holes | Copper routing |
| Every major part placed, real package sizes | DRC against a fab profile |
| Courtyard / hole / pad interaction checks | Ordering files (gerbers/BOM/CPL) |
| 61-net authored FC connectivity + automated test | Exact footprints linked into PCB |
| KiCad 9 file that parses | Production approval |

The present `.kicad_pcb` is **not an orderable FC**: it still has anchor pads
rather than the 61-net `vyper_f4.net`, and no copper. KiCad reports zero
unconnected pads only because the board has no imported electrical nets; that
is not a pass. See `FC_ARCHITECTURE.md` for the clean authored-netlist result
and the remaining graphical-schematic gate.

## The AI-tool landscape (researched July 2026)

| Tool | What it actually does | Use here? |
|---|---|---|
| [Quilter](https://www.quilter.ai/product) | Cloud PCB layout from a completed circuit and constraints. | Candidate after schematic review |
| [DeepPCB](https://deeppcb.ai/) | AI-assisted PCB routing service. | Alternative candidate |
| [Flux Copilot](https://www.flux.ai/COPILOT) | Schematic/PCB design assistant in Flux. | Review aid, not qualification |
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
3. **Gyro-to-MCU SPI under 10 mm.** Courtyard gap here: ~0.8 mm.
4. **Soft mounting is a requirement, not a preference.** Hard-bolting the
   board flexes it and permanently shifts gyro bias — hence Φ4.0 holes for
   M3 grommets and a Φ8 keepout ring at each corner *on both faces*.
5. **Solid ground under the IMU; 4-layer stack** (sig / GND / PWR / sig)
   when routed — a continuous plane under high-frequency parts is the
   cheapest EMI fix there is.
6. **Power entry short and fat, cap at the connector.** The FC now uses a
   60 V TPS54360 reference-design buck; bulk low-ESR capacitance still belongs
   at the ESC battery entry, close to the switching current loop.
7. **USB and ESC socket on the bottom face** — the ESC harness plugs
   straight up from the stack below; USB faces the open tail of the
   fuselage. This is a case where the *airframe* dictated the PCB.

## Why the board is shaped by the fuselage

Two findings the checks enforce forever:

- **R5 corners preserve service clearance.** The 6S battery enlarged the
  cavity radius to 26.5 mm, so a square 36 mm board now fits at a 25.46 mm
  half-diagonal, but leaves only 1.04 mm radial allowance. R5 reduces corner
  reach to 23.38 mm and leaves 3.12 mm for wire and assembly tolerance.
- **The classic corner motor-pad position is illegal on this board.** At
  (±13, ±13) all four pads sit inside the grommet keepouts — and M3
  additionally landed inside the blackbox-flash courtyard. The checks caught
  both; pads moved inboard.

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
  vyper_esc_unrouted_gen.py              # true footprints/nets, still unrouted
/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
  test_vyper_esc_board.py                # 195 refs / 715 nodes transferred
python3 test_vyper_esc_drc.py             # rejects hidden placement/copper errors
kicad-cli pcb render --side top --output top.png vyper_f4.kicad_pcb
```

The `.kicad_pcb` opens directly in KiCad 9, but it must be updated from the
reviewed netlist and routed before it can pass the release gates.
