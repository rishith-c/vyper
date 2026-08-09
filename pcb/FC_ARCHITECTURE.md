# VYPER-F4 Rev A electrical architecture

Status: **authored netlist passes SKiDL ERC with zero errors and zero warnings;
not orderable**. A four-layer true-footprint review board now transfers all 77
references and 250 netlist nodes to physical pads. All 58 passives are placed
in-outline with functional proximity gates and no placement/copper DRC errors;
192 connections remain unrouted.
The current mechanical form is a 30×64 mm R3 longitudinal board on a 16×56 mm
M2 soft-mount pattern. It mounts vertically behind the ESC in the removable
electronics cassette; it is not a standard square flight-stack board.
The automatically drawn KiCad preview is excluded from release because its
flat-sheet placer can overlap labels. `vyper_f4.net` remains the reviewed
connectivity artifact; a zero-error human-readable schematic is a release gate.

## Power tree

```text
6S VBAT (25.2 V full)
  └─ TPS54360DDA, 60 V / 3.5 A reference design → V5_BUCK
       ├─ external 5 V pads
       └─ SS14 diode ─┐
USB service VBUS ─ SS14 ─┘  LOGIC_IN
                         ├─ AP2112K-3.3 → V3V3 (MCU/flash/baro)
                         └─ AP2112K-3.3 → V3V3_GYRO (ICM-42688-P only)
```

The TPS54360 values follow TI Figure 34: 600 kHz (162 kΩ), 8.2 µH,
B560C catch diode, 53.6/10.2 kΩ feedback, 13.0 kΩ + 6.8 nF / 39 pF
compensation, two 2.2 µF/100 V inputs and two 47 µF outputs. This replaces the
earlier 28 V TPS54331, which had inadequate transient margin on 6S.

## Resource map

| Function | STM32F405 pin | Peripheral |
|---|---:|---|
| Gyro SPI | PA5/PA6/PA7, PA4 CS, PC4 INT | ICM-42688-P |
| Blackbox SPI | PB13/PB14/PB15, PB12 CS | W25Q128JVS |
| Barometer I2C | PB6/PB7 | BMP280 at 0x76 |
| Motors 1–4 | PB1, PB0, PA3, PA2 | timer/DShot outputs |
| ESC telemetry | PD2 | UART5 RX |
| Receiver | PA9/PA10 | UART1 |
| GPS | PB10/PB11 | UART3 |
| External compass | PB6/PB7 | I2C1, remote QMC5883/LIS2MDL breakout |
| VTX control | PC6/PC7 | UART6 |
| RGB status | PA8 | SN74AHCT1G125 level shifter + SK6812MINI-E |
| VBAT/current ADC | PC5/PC3 | 100k:10k divider / filtered ESC current |
| USB | PA11/PA12 | USB FS, 4-pin JST-SH service harness, 22 Ω and low-C TVS |
| SWD | PA13/PA14 | 4-pin debug header |

The three UART groups and external I2C group use plated 2.4×2.0 mm pads, 1.0 mm finished holes,
and standard 2.54 mm pitch. They accept ordinary 0.64 mm
header pins or hand-soldered 26--28 AWG wire and retain copper on every layer.

The matching Betaflight resource contract is
`firmware/vyper_f405/config.h`. The 8-pin ESC harness contract is GND, VBAT,
CURRENT, TELEMETRY, M1, M2, M3, M4.

## Reproduce and verify

```bash
uv pip install --python .venv/bin/python -r pcb/requirements-ecad.txt
KICAD9_SYMBOL_DIR=/Applications/KiCad.app/Contents/SharedSupport/symbols \
KICAD_SYMBOL_DIR=/Applications/KiCad.app/Contents/SharedSupport/symbols \
  .venv/bin/python pcb/vyper_f4_schematic.py
python3 pcb/test_vyper_f4_netlist.py
/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
  pcb/vyper_f4_unrouted_gen.py
/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
  pcb/test_vyper_f4_board.py
python3 pcb/test_vyper_f4_drc.py
```

The generator's authored circuit reports zero SKiDL ERC warnings/errors and
the tests independently check 58 named nets, unique pin ownership, the complete
gyro bus, motor/ESC/UART/USB/SWD mapping, ADC and power members, exact gyro
value, 60 V buck selection and netlist-to-pad transfer.

## Primary references

- [Betaflight manufacturer design guidelines](https://betaflight.com/docs/development/manufacturer/manufacturer-design-guidelines)
- [ST STM32F405/407 data sheet](https://www.st.com/resource/en/datasheet/stm32f405rg.pdf)
- [TDK ICM-42688-P data sheet](https://invensense.tdk.com/wp-content/uploads/2020/04/ds-000347_icm-42688-p-datasheet.pdf)
- [TI TPS54360 product and data sheet](https://www.ti.com/product/TPS54360)
- [Betaflight target configuration repository](https://github.com/betaflight/config)

## Remaining release gates

- Redraw/review the human-readable KiCad schematic with zero ERC errors and no
  merged-net warnings.
- Repack the TPS54360 switching loop, then route all 192 remaining connections
  on four layers and pass fab-profile DRC
  with zero warnings/errors.
- Independent schematic/layout review, assembly outputs, bench bring-up,
  vibration/thermal tests, and Betaflight target build/USB/DFU validation.
