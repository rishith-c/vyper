"""Generate the VYPER-F4 Rev A electrical schematic with SKiDL/KiCad 9.

The schematic is intentionally generated from code so pin resources, values,
and footprints remain reviewable in git.  It is an engineering prototype, not
a released flight controller: PCB routing, signal-integrity review, bring-up,
and flight qualification are still mandatory.

Run from the repository root:
    KICAD9_SYMBOL_DIR=/Applications/KiCad.app/Contents/SharedSupport/symbols \
        .venv/bin/python pcb/vyper_f4_schematic.py
"""

import os
import builtins
from pathlib import Path

KICAD_SHARE = Path("/Applications/KiCad.app/Contents/SharedSupport")
os.environ.setdefault("KICAD9_SYMBOL_DIR", str(KICAD_SHARE / "symbols"))
os.environ.setdefault("KICAD_SYMBOL_DIR", str(KICAD_SHARE / "symbols"))

from skidl import (  # noqa: E402
    ERC, KICAD9, POWER, Net, Part, generate_netlist, generate_schematic,
    set_default_tool
)

set_default_tool(KICAD9)
NC = builtins.NC
OUT = Path(__file__).resolve().parent

R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
D_SMA = "Diode_SMD:D_SMA"


def resistor(value, a, b, ref=None, footprint=R0402):
    part = Part("Device", "R", value=value, ref=ref, footprint=footprint)
    part[1] += a
    part[2] += b
    return part


def capacitor(value, a, b, ref=None, footprint=C0402):
    part = Part("Device", "C", value=value, ref=ref, footprint=footprint)
    part[1] += a
    part[2] += b
    return part


def schottky(value, anode, cathode, ref=None, footprint=D_SMA):
    part = Part("Device", "D_Schottky", value=value, ref=ref,
                footprint=footprint)
    part["A"] += anode
    part["K"] += cathode
    return part


# Power and interfaces.
gnd = Net("GND")
vbat = Net("VBAT_6S")
v5 = Net("V5_BUCK")
usb5 = Net("USB_5V")
logic_in = Net("LOGIC_IN")
v3 = Net("V3V3")
v3a = Net("V3V3_A")
vgyro = Net("V3V3_GYRO")
for rail in (gnd, vbat, v5, usb5, logic_in, v3, v3a, vgyro):
    rail.drive = POWER

# ---------------------------------------------------------------------------
# J2: exact 8-pin ESC harness contract.  Pins are fixed here and in config.h.
# ---------------------------------------------------------------------------
j2 = Part("Connector_Generic", "Conn_01x08", ref="J2",
          value="ESC_SH1.0_8P",
          footprint="Connector_JST:JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal")
esc_current = Net("ESC_CURRENT")
esc_telem = Net("ESC_TELEM")
m1, m2, m3, m4 = [Net(f"MOTOR_{n}") for n in range(1, 5)]
for pin, net in zip(range(1, 9),
                    (gnd, vbat, esc_current, esc_telem, m1, m2, m3, m4)):
    j2[pin] += net

# ---------------------------------------------------------------------------
# 60 V-rated 6S -> 5 V / 3.5 A supply copied from TI Figure 34.
# This replaces the earlier 28 V TPS54331, which had inadequate 6S margin.
# ---------------------------------------------------------------------------
u3 = Part("Regulator_Switching", "TPS54360DDA", ref="U3")
sw = Net("BUCK_SW")
fb = Net("BUCK_FB")
comp_mid = Net("BUCK_COMP_MID")
comp_rc = Net("BUCK_COMP_RC")
rt = Net("BUCK_RT")
boot = Net("BUCK_BOOT")
en = Net("BUCK_EN")
u3["VIN"] += vbat
u3["EN"] += en
u3["RT/CLK"] += rt
resistor("162k 1%", rt, gnd)
u3["GND", "GNDPAD"] += gnd
u3["SW"] += sw
u3["FB"] += fb
u3["COMP"] += comp_mid
resistor("523k 1%", vbat, en)
resistor("84.5k 1%", en, gnd)
resistor("53.6k 1%", v5, fb)
resistor("10.2k 1%", fb, gnd)
resistor("13.0k 1%", comp_mid, comp_rc)
capacitor("6.8nF C0G", comp_rc, gnd)
capacitor("39pF C0G", comp_mid, gnd)
u3["BOOT"] += boot
capacitor("100nF 16V X7R", boot, sw)
schottky("B560C 60V 5A", gnd, sw, ref="D1")
l1 = Part("Device", "L", ref="L1", value="8.2uH Isat>=5.8A",
          footprint="Inductor_SMD:L_Wuerth_HCI-7050")
l1[1] += sw
l1[2] += v5
for _ in range(2):
    capacitor("2.2uF 100V X7R", vbat, gnd, footprint=C0603)
    capacitor("47uF 10V X7R", v5, gnd,
              footprint="Capacitor_SMD:C_1210_3225Metric")

# USB powers only the logic LDO inputs; it cannot back-feed the 5 V accessory
# rail.  The buck and USB paths are diode-ORed at LOGIC_IN.
schottky("SS14", v5, logic_in, ref="D2",
         footprint="Diode_SMD:D_SMA_Handsoldering")
schottky("SS14", usb5, logic_in, ref="D3",
         footprint="Diode_SMD:D_SMA_Handsoldering")

# Main and dedicated gyro regulators.  Betaflight requires a separate low-noise
# supply for ICM-42688-P designs.
u4 = Part("Regulator_Linear", "AP2112K-3.3", ref="U4")
u5 = Part("Regulator_Linear", "AP2112K-3.3", ref="U5")
for reg, out in ((u4, v3), (u5, vgyro)):
    reg["VIN", "EN"] += logic_in
    reg["GND"] += gnd
    reg["VOUT"] += out
    NC += reg["NC"]
    capacitor("1uF 10V X7R", logic_in, gnd)
    capacitor("1uF 10V X7R", out, gnd)

# ---------------------------------------------------------------------------
# STM32F405 core and pin resources.  Pin choices track a supported F405 target
# and are checked by firmware/vyper_f405/config.h.
# ---------------------------------------------------------------------------
u1 = Part("MCU_ST_STM32F4", "STM32F405RGTx", ref="U1",
          footprint="Package_QFP:LQFP-64_10x10mm_P0.5mm")
u1["VDD", "VBAT"] += v3
u1["VSS", "VSSA"] += gnd

# Analog supply isolation.
fb1 = Part("Device", "FerriteBead", ref="FB1", value="600R@100MHz",
           footprint=R0402)
fb1[1] += v3
fb1[2] += v3a
u1["VDDA"] += v3a
capacitor("100nF X7R", v3a, gnd)
capacitor("1uF X7R", v3a, gnd)
for _ in range(4):
    capacitor("100nF X7R", v3, gnd)
capacitor("4.7uF X7R", v3, gnd, footprint=C0603)
vcap1, vcap2 = Net("VCAP1"), Net("VCAP2")
u1["VCAP_1"] += vcap1
u1["VCAP_2"] += vcap2
capacitor("2.2uF low-ESR", vcap1, gnd, footprint=C0603)
capacitor("2.2uF low-ESR", vcap2, gnd, footprint=C0603)

# 8 MHz HSE and reset/boot network.
hse_in, hse_out = Net("HSE_IN"), Net("HSE_OUT")
y1 = Part("Device", "Crystal", ref="Y1", value="8MHz 10pF",
          footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
y1[1] += hse_in
y1[2] += hse_out
u1["PH0"] += hse_in
u1["PH1"] += hse_out
capacitor("18pF C0G", hse_in, gnd)
capacitor("18pF C0G", hse_out, gnd)
resistor("1M", hse_in, hse_out)
nrst = Net("NRST")
u1["NRST"] += nrst
resistor("10k", nrst, v3)
capacitor("100nF", nrst, gnd)
boot0 = Net("BOOT0")
u1["BOOT0"] += boot0
resistor("100k", boot0, gnd)

# Gyro: IIM-42652 is KiCad's pin-compatible 14-pin symbol; value and datasheet
# are overridden to the exact ICM-42688-P used here.
u2 = Part("Sensor_Motion", "IIM-42652", ref="U2",
          value="ICM-42688-P",
          footprint="Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm")
u2.datasheet = "https://invensense.tdk.com/wp-content/uploads/2020/04/ds-000347_icm-42688-p-datasheet.pdf"
spi1_sck, spi1_miso, spi1_mosi = Net("SPI1_SCK"), Net("SPI1_MISO"), Net("SPI1_MOSI")
gyro_cs, gyro_int = Net("GYRO_CS"), Net("GYRO_INT1")
u2["VDD", "VDDIO"] += vgyro
u2["GND", "INT2/FSYNC/CLKIN"] += gnd
NC += u2["RESV"]
u2["AP_CS"] += gyro_cs
u2["AP_SCL/AP_SCLK"] += spi1_sck
u2["AP_SDO/AP_AD0"] += spi1_miso
u2["AP_SDA/AP_SDIO/AP_SDI"] += spi1_mosi
u2["INT1/INT"] += gyro_int
capacitor("100nF X7R", vgyro, gnd)
capacitor("2.2uF X7R", vgyro, gnd, footprint=C0603)
# Use SPI1's valid PB3/PB4/PB5 alternate-function group. With U1 rotated 0
# degrees these five consecutive package pins face the gyro, removing every
# package crossover from the timing-critical bus.
for pin_name, net in (("PB3", spi1_sck), ("PB4", spi1_miso),
                      ("PB5", spi1_mosi), ("PB7", gyro_cs),
                      ("PB6", gyro_int)):
    u1[pin_name] += net

# Blackbox flash on SPI2. The exact W25Q128JVPIM uses Winbond's compact
# 6x5 mm WSON-8 package. Pad 9 is a structural, internally unconnected center
# pad per Winbond; the selected footprint leaves it netless and has no vias
# under it.
u6 = Part("Memory_Flash", "W25Q128JVS", ref="U6",
          value="W25Q128JVPIM",
          footprint=("Package_DFN_QFN:"
                     "WDFN-8-1EP_6x5mm_P1.27mm_EP3.4x4mm"))
spi2_sck, spi2_miso, spi2_mosi = Net("SPI2_SCK"), Net("SPI2_MISO"), Net("SPI2_MOSI")
flash_cs = Net("FLASH_CS")
u6["VCC"] += v3
flash_wp, flash_hold = Net("FLASH_WP_N"), Net("FLASH_HOLD_N")
u6["~{WP}/IO_{2}"] += flash_wp
u6["~{HOLD}/~{RESET}/IO_{3}"] += flash_hold
resistor("10k", flash_wp, v3)
resistor("10k", flash_hold, v3)
u6["GND"] += gnd
u6["~{CS}"] += flash_cs
u6["CLK"] += spi2_sck
u6["DO/IO_{1}"] += spi2_miso
u6["DI/IO_{0}"] += spi2_mosi
capacitor("100nF", v3, gnd)
for pin_name, net in (("PB13", spi2_sck), ("PB14", spi2_miso),
                      ("PB15", spi2_mosi), ("PB12", flash_cs)):
    u1[pin_name] += net

# BMP280 barometer on I2C1; CSB high selects I2C, SDO low selects 0x76.
u7 = Part("Sensor_Pressure", "BMP280", ref="U7")
i2c_scl, i2c_sda = Net("I2C1_SCL"), Net("I2C1_SDA")
u7["VDD", "VDDIO", "CSB"] += v3
u7["GND", "SDO"] += gnd
u7["SCK"] += i2c_scl
u7["SDI"] += i2c_sda
# PB8/PB9 are the second valid I2C1 pin pair and free PB6/PB7 for the adjacent
# gyro interrupt/chip-select pins above.
u1["PB8"] += i2c_scl
u1["PB9"] += i2c_sda
resistor("4.7k", i2c_scl, v3)
resistor("4.7k", i2c_sda, v3)
capacitor("100nF", v3, gnd)

# USB service harness, ESD, and 22-ohm source termination. A four-wire
# JST-SH-to-USB-C pigtail keeps the bulky receptacle and through-hole shield
# tabs out of the enclosed FC stack while preserving native USB FS.
j1 = Part("Connector_Generic", "Conn_01x04", ref="J1",
          value="USB_SERVICE_SH1.0_4P",
          footprint="Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal")
usb_dm_raw, usb_dp_raw = Net("USB_DM_RAW"), Net("USB_DP_RAW")
usb_dm, usb_dp = Net("USB_DM"), Net("USB_DP")
# Harness order is GND, VBUS, D+, D-. The data order is deliberate: after the
# pair's natural 90-degree turn on the vertical FC, D- lands on pin 4 and D+
# lands on pin 3 without a crossover. The external USB-C pigtail must follow
# this documented, non-standard JST-SH pinout.
for pin, net in zip(range(1, 5), (gnd, usb5, usb_dp_raw, usb_dm_raw)):
    j1[pin] += net
# Exact two-line flow-through USB ESD array. Pairing both channels in one
# package reduces parasitic mismatch versus two vaguely specified discrete
# clamps. I/O2 carries D- and I/O1 carries D+ so physical routing order remains
# consistent from connector to MCU.
u9 = Part("Power_Protection", "USBLC6-2SC6", ref="U9")
u9[3, 4] += usb_dm_raw
u9[1, 6] += usb_dp_raw
u9[5] += usb5
u9[2] += gnd
# VBUS retains a dedicated surge clamp.
d7 = Part("Device", "D_TVS", ref="D7", value="PESD5V low-C",
          footprint="Diode_SMD:D_SOD-323")
d7[1] += gnd
d7[2] += usb5
# Exact 0402 source terminators satisfy the board's 0.20 mm copper-clearance
# rule while remaining small enough for a direct PA11/PA12 escape.
resistor("ERJ2RKF22R0X 22R 1%", usb_dm_raw, usb_dm, ref="R14")
resistor("ERJ2RKF22R0X 22R 1%", usb_dp_raw, usb_dp, ref="R15")
u1["PA11"] += usb_dm
u1["PA12"] += usb_dp
capacitor("1uF 10V", usb5, gnd, footprint=C0603)

# Motor outputs, UARTs, ESC telemetry and analog acquisition.
for pin_name, net in (("PB1", m1), ("PB0", m2), ("PA3", m3), ("PA2", m4),
                      ("PD2", esc_telem)):
    u1[pin_name] += net

vbat_adc, curr_adc = Net("ADC_VBAT"), Net("ADC_CURRENT")
resistor("100k 0.1%", vbat, vbat_adc, ref="R16")
resistor("10k 0.1%", vbat_adc, gnd, ref="R17")
capacitor("10nF C0G", vbat_adc, gnd)
resistor("1k", esc_current, curr_adc, ref="R18")
capacitor("10nF C0G", curr_adc, gnd)
u1["PC5"] += vbat_adc
u1["PC3"] += curr_adc

# Receiver, GPS/VTX control, and spare UART pad groups follow Betaflight's
# GND / 5V / TX / RX connector sequence.
uart_defs = (("J3", "RX_UART1", "PA9", "PA10"),
             ("J4", "GPS_UART3", "PB10", "PB11"),
             ("J6", "VTX_UART6", "PC6", "PC7"))
for ref, value, tx_pin, rx_pin in uart_defs:
    tx, rx = Net(f"{value}_TX"), Net(f"{value}_RX")
    conn = Part("Connector_Generic", "Conn_01x04", ref=ref, value=value,
                footprint="Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical")
    for pin, net in zip(range(1, 5), (gnd, v5, tx, rx)):
        conn[pin] += net
    u1[tx_pin] += tx
    u1[rx_pin] += rx

# Expose the same I2C bus used by the barometer for an external compass or
# environmental sensor. An onboard magnetometer would sit inside the ESC and
# motor-current field, so the mechanically correct implementation is remote.
j5 = Part("Connector_Generic", "Conn_01x04", ref="J5", value="EXTERNAL_I2C",
          footprint="Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical")
for pin, net in zip(range(1, 5), (gnd, v5, i2c_sda, i2c_scl)):
    j5[pin] += net

# SWD and status outputs.
swdio, swclk = Net("SWDIO"), Net("SWCLK")
j7 = Part("Connector_Generic", "Conn_01x04", ref="J7", value="SWD",
          footprint="Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical")
for pin, net in zip(range(1, 5), (v3, swdio, swclk, gnd)):
    j7[pin] += net
u1["PA13"] += swdio
u1["PA14"] += swclk
beeper = Net("BEEPER")
u1["PC13"] += beeper

# Addressable RGB status LED. SK6812MINI is a 5 V device; a 74AHCT1G125 gives
# deterministic 3.3-to-5 V logic translation instead of relying on an
# out-of-spec direct GPIO connection. The 100 k pulldown keeps DIN low while
# PA8 is high impedance during reset.
led_mcu, led_level, led_din = (Net("LED_RGB_MCU"), Net("LED_RGB_LEVEL"),
                               Net("LED_RGB_DIN"))
u1["PA8"] += led_mcu
resistor("100k", led_mcu, gnd, ref="R20")
u8 = Part("74xGxx", "74AHCT1G125", ref="U8", value="SN74AHCT1G125DBVR",
          footprint="Package_TO_SOT_SMD:SOT-23-5")
u8[1] += gnd                    # active-low output enable: always enabled
u8[2] += led_mcu
u8[3] += gnd
u8[4] += led_level
u8[5] += v5
resistor("33R", led_level, led_din, ref="R19")
rgb = Part("LED", "SK6812MINI", ref="D4", value="SK6812MINI-E",
           footprint="LED_SMD:LED_SK6812MINI_PLCC4_3.5x3.5mm_P1.75mm")
rgb["DIN"] += led_din
rgb["VDD"] += v5
rgb["VSS"] += gnd
NC += rgb["DOUT"]
capacitor("100nF X7R", v5, gnd, ref="C31")
j8 = Part("Connector_Generic", "Conn_01x02", ref="J8", value="BEEPER_PAD",
          footprint="Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical")
j8[1] += v5
j8[2] += beeper

# Explicit no-connects for unused MCU pins make KiCad ERC meaningful.
used = {pin.num for pin in u1.pins if pin.nets}
for pin in u1.pins:
    if pin.num not in used:
        NC += pin

# Write the authored electrical connectivity before any drawing-only stubbing.
# This KiCad netlist is the review source for the PCB update and automated
# connectivity checks.
ERC()
generate_netlist(file_=str(OUT / "vyper_f4.net"), tool=KICAD9,
                 do_backup=False)

# Force a labels-only schematic preview.  The SKiDL router can create accidental
# junctions in a dense 100+ symbol flat sheet; explicit per-pin labels preserve
# most readability.  KiCad ERC is still the authority: this preview is not a
# manufacturing source until its report has zero errors and no merged-net warn.
for net in builtins.default_circuit.nets:
    if not net.valid or not net.pins:
        continue
    net._stub = True
    net._stub_explicit = True
    for pin in net.get_pins():
        pin.stub = True

generate_schematic(filepath=str(OUT), top_name="vyper_f4_preview",
                   title="VYPER-F4 Rev A -- PREVIEW, NOT FOR FAB",
                   tool=KICAD9, flatness=1.0, auto_stub=True,
                   auto_stub_fanout=1, auto_stub_max_wire_pins=1,
                   auto_stub_max_wire_dist=0, label_clearance=True,
                   auto_stub_fallback="labels", retries=3)
print(OUT / "vyper_f4.net")
print(OUT / "vyper_f4_preview.kicad_sch")
