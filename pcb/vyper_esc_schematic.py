"""Generate the authored VYPER-55A four-channel ESC KiCad netlist.

This is the electrical source of truth for the EVT schematic.  It deliberately
generates a reviewable legacy KiCad netlist before any copper is routed.  The
board is not orderable or flight-safe until the routing, DRC, thermal and bench
gates in ESC_ARCHITECTURE.md are complete.

Run from the repository root:
    KICAD9_SYMBOL_DIR=/Applications/KiCad.app/Contents/SharedSupport/symbols \
        .venv/bin/python pcb/vyper_esc_schematic.py
"""

import builtins
import os
from pathlib import Path

KICAD_SHARE = Path("/Applications/KiCad.app/Contents/SharedSupport")
os.environ.setdefault("KICAD9_SYMBOL_DIR", str(KICAD_SHARE / "symbols"))
os.environ.setdefault("KICAD_SYMBOL_DIR", str(KICAD_SHARE / "symbols"))

from skidl import ERC, KICAD9, POWER, Net, Part, Pin, SKIDL, generate_netlist, set_default_tool  # noqa: E402
from skidl.pin import pin_types  # noqa: E402

set_default_tool(KICAD9)
NC = builtins.NC
OUT = Path(__file__).resolve().parent

R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"


def resistor(value, a, b, ref=None, footprint=R0402):
    p = Part("Device", "R", value=value, ref=ref, footprint=footprint)
    p[1] += a
    p[2] += b
    return p


def capacitor(value, a, b, ref=None, footprint=C0402):
    p = Part("Device", "C", value=value, ref=ref, footprint=footprint)
    p[1] += a
    p[2] += b
    return p


def diode(value, anode, cathode, ref=None,
          footprint="Diode_SMD:D_SOD-323_HandSoldering"):
    p = Part("Device", "D_Schottky", value=value, ref=ref,
             footprint=footprint)
    p["A"] += anode
    p["K"] += cathode
    return p


def custom_part(name, ref, prefix, footprint, pins, datasheet):
    """Create an instantiated symbol with exact package pin numbers."""
    return Part(
        name=name,
        tool=SKIDL,
        ref_prefix=prefix,
        ref=ref,
        value=name,
        footprint=footprint,
        datasheet=datasheet,
        pins=[Pin(num=str(number), name=pin_name, func=pin_types.PASSIVE)
              for number, pin_name in pins],
    )


AT32_PINS = (
    (1, "VDD1"), (2, "PF0"), (3, "PF1"), (4, "NRST"), (5, "VDDA"),
    (6, "PA0"), (7, "PA1"), (8, "PA2"), (9, "PA3"), (10, "PA4"),
    (11, "PA5"), (12, "PA6"), (13, "PA7"), (14, "PB0"), (15, "PB1"),
    (16, "PB2"), (17, "VDD2"), (18, "PA8"), (19, "PA9"), (20, "PA10"),
    (21, "PA11"), (22, "PA12"), (23, "PA13_SWDIO"), (24, "PA14_SWCLK"),
    (25, "PA15"), (26, "PB3"), (27, "PB4_DSHOT"), (28, "PB5"),
    (29, "PB6_TX"), (30, "PB7"), (31, "BOOT0"), (32, "PB8"),
    (33, "VSS_VSSA_EP"),
)

DRV8323H_PINS = (
    (1, "CPL"), (2, "CPH"), (3, "VCP"), (4, "VM"), (5, "VDRAIN"),
    (6, "GHA"), (7, "SHA"), (8, "GLA"), (9, "SPA"), (10, "SNA"),
    (11, "SNB"), (12, "SPB"), (13, "GLB"), (14, "SHB"), (15, "GHB"),
    (16, "GHC"), (17, "SHC"), (18, "GLC"), (19, "SPC"), (20, "SNC"),
    (21, "SOC"), (22, "SOB"), (23, "SOA"), (24, "VREF"),
    (25, "NFAULT"), (26, "MODE"), (27, "IDRIVE"), (28, "VDS"),
    (29, "GAIN"), (30, "ENABLE"), (31, "CAL"), (32, "AGND"),
    (33, "DVDD"), (34, "INHA"), (35, "INLA"), (36, "INHB"),
    (37, "INLB"), (38, "INHC"), (39, "INLC"), (40, "PGND"),
    (41, "EP"),
)

# KiCad's manufacturer-derived TDSON-8-1 land pattern has three source lands,
# one gate land and one continuous drain land.  Package leads 5-8 share that
# drain copper, so representing four overlapping drain pad numbers would be
# electrically redundant and would create false DRC overlaps.
FET_PINS = ((1, "S1"), (2, "S2"), (3, "S3"), (4, "G"), (5, "D"))


def at32(ref):
    return custom_part(
        "AT32F421K8U7-4", ref, "U",
        "Package_DFN_QFN:QFN-32-1EP_4x4mm_P0.4mm_EP2.65x2.65mm",
        AT32_PINS,
        "https://www.arterychip.com/download/DS/DS_AT32F421_V2.02_EN.pdf",
    )


def drv8323(ref):
    return custom_part(
        "DRV8323HRTAR", ref, "U",
        "VYPER:TI_RTA0040_WQFN40_6x6_P0.5_EP",
        DRV8323H_PINS,
        "https://www.ti.com/lit/ds/symlink/drv8323r.pdf",
    )


def bsc012(ref):
    return custom_part(
        "BSC012N06NS", ref, "Q",
        "Package_TO_SOT_SMD:TDSON-8-1", FET_PINS,
        "https://www.infineon.com/dgdl/Infineon-BSC012N06NS-DataSheet-v02_04-EN.pdf",
    )


# Global rails and the exact 8-pin FC/ESC interface.
gnd = Net("PGND")
vbat = Net("VBAT_6S")
v3 = Net("V3V3_ESC")
for rail in (gnd, vbat, v3):
    rail.drive = POWER

j1 = Part("Connector_Generic", "Conn_01x08", ref="J1",
          value="FC_ESC_SH1.0_8P",
          footprint="VYPER:FC_HARNESS_2X4_P1.27_SOLDER")
esc_current = Net("ESC_CURRENT_TOTAL")
esc_telem = Net("ESC_TELEM")
dshot = [Net(f"DSHOT_M{n}") for n in range(1, 5)]
for pin, net in zip(range(1, 9),
                    (gnd, vbat, esc_current, esc_telem, *dshot)):
    j1[pin] += net
jbat = Part("Connector_Generic", "Conn_01x02", ref="JBAT",
            value="12AWG_BATTERY_PIGTAIL",
            footprint="VYPER:BATTERY_PIGTAIL_2X")
jbat[1] += vbat
jbat[2] += gnd

# One defined 60 V regulator powers all four MCUs.  Four AT32F421 devices draw
# <=82.8 mA at the datasheet's 105 C / 120 MHz maximum; the 600 mA regulator
# therefore retains >7x DC-current margin before analog support loads.
u1 = custom_part(
    "LMR16006XDDCR", "U1", "U", "Package_TO_SOT_SMD:SOT-23-6",
    ((1, "CB"), (2, "GND"), (3, "FB"), (4, "SHDN"), (5, "VIN"), (6, "SW")),
    "https://www.ti.com/lit/ds/symlink/lmr16006.pdf",
)
buck_sw, buck_cb, buck_fb, buck_en = [Net(n) for n in
                                      ("BUCK_SW", "BUCK_CB", "BUCK_FB", "BUCK_EN")]
u1["VIN"] += vbat
u1["GND"] += gnd
u1["SW"] += buck_sw
u1["CB"] += buck_cb
u1["FB"] += buck_fb
u1["SHDN"] += buck_en
resistor("100k", vbat, buck_en, ref="R1")
capacitor("100nF 16V X7R", buck_cb, buck_sw, ref="C1")
diode("PMEG6010CEH 60V 1A", gnd, buck_sw, ref="D1",
      footprint="Diode_SMD:D_SOD-123F")
l1 = Part("Device", "L", ref="L1", value="XGL5030-223MEC 22uH",
          footprint="Inductor_SMD:L_Coilcraft_XAL5030-XXX")
l1[1] += buck_sw
l1[2] += v3
resistor("33.2k 1%", v3, buck_fb, ref="R2")
resistor("10.0k 1%", buck_fb, gnd, ref="R3")
for ref in ("C2", "C3"):
    capacitor("2.2uF 100V X7R", vbat, gnd, ref=ref, footprint=C0603)
for ref in ("C4", "C5"):
    capacitor("22uF 10V X7R", v3, gnd, ref=ref,
              footprint="Capacitor_SMD:C_0805_2012Metric")


channel_currents = []
for index in range(1, 5):
    prefix = f"M{index}"
    mcu = at32(f"U{index}1")
    drv = drv8323(f"U{index}2")
    phase = {letter: Net(f"{prefix}_PHASE_{letter}") for letter in "ABC"}
    power_return = Net(f"{prefix}_POWER_RETURN")
    current_adc = Net(f"{prefix}_CURRENT_ADC")
    channel_currents.append(current_adc)

    # AT32 power, reset, boot and programming.  No external crystal is used;
    # AM32's F421 build uses the internal clock/PLL.
    mcu["VDD1", "VDD2"] += v3
    mcu["VSS_VSSA_EP"] += gnd
    vdda = Net(f"{prefix}_VDDA")
    fb = Part("Device", "FerriteBead", ref=f"FB{index}", value="600R@100MHz",
              footprint=R0402)
    fb[1] += v3
    fb[2] += vdda
    mcu["VDDA"] += vdda
    capacitor("100nF X7R", v3, gnd, ref=f"C{index}01")
    capacitor("100nF X7R", v3, gnd, ref=f"C{index}02")
    capacitor("1uF X7R", vdda, gnd, ref=f"C{index}03")
    nrst = Net(f"{prefix}_NRST")
    mcu["NRST"] += nrst
    resistor("10k", nrst, v3, ref=f"R{index}01")
    boot = Net(f"{prefix}_BOOT0")
    mcu["BOOT0"] += boot
    resistor("100k", boot, gnd, ref=f"R{index}02")
    swd = Part("Connector_Generic", "Conn_01x04", ref=f"J{index + 1}",
               value=f"{prefix}_SWD_PADS",
               footprint="VYPER:SWD_2X2_P1.27_TESTPADS")
    swd[1] += v3
    swd[2] += mcu["PA13_SWDIO"]
    swd[3] += mcu["PA14_SWCLK"]
    swd[4] += gnd

    # AM32 SEQURE-style F421 contract: PB4 input, TMR1 complementary PWM,
    # comparator phases 0/4/5, current PA2, NTC PA3 and voltage PA6.
    mcu["PB4_DSHOT"] += dshot[index - 1]
    pwm_nets = {}
    for signal, pin_name in (("AH", "PA10"), ("AL", "PB1"),
                             ("BH", "PA9"), ("BL", "PB0"),
                             ("CH", "PA8"), ("CL", "PA7")):
        pwm_nets[signal] = Net(f"{prefix}_PWM_{signal}")
        mcu[pin_name] += pwm_nets[signal]
    for drv_pin, signal in (("INHA", "AH"), ("INLA", "AL"),
                            ("INHB", "BH"), ("INLB", "BL"),
                            ("INHC", "CH"), ("INLC", "CL")):
        drv[drv_pin] += pwm_nets[signal]

    # Phase dividers stay below 2.3 V at a 25.2 V full pack.  The 220 pF C0G
    # filter keeps the pole near 80 kHz so a 14-pole motor at 31.6 krpm does
    # not acquire the excessive phase delay of a 1 nF network.
    for letter, pin_name in (("A", "PA0"), ("B", "PA4"), ("C", "PA5")):
        bemf = Net(f"{prefix}_BEMF_{letter}")
        resistor("100k 1% 50V", phase[letter], bemf,
                 ref=f"R{index}{letter}1")
        resistor("10k 1%", bemf, gnd, ref=f"R{index}{letter}2")
        capacitor("220pF C0G", bemf, gnd, ref=f"C{index}{letter}1")
        mcu[pin_name] += bemf

    # Shared bus voltage and local bridge temperature telemetry.
    voltage_adc = Net(f"{prefix}_VOLTAGE_ADC")
    resistor("100k 1% 50V", vbat, voltage_adc, ref=f"R{index}V1")
    resistor("10k 1%", voltage_adc, gnd, ref=f"R{index}V2")
    capacitor("1nF C0G", voltage_adc, gnd, ref=f"C{index}V1")
    mcu["PA6"] += voltage_adc
    ntc_adc = Net(f"{prefix}_NTC_ADC")
    resistor("10k 1%", v3, ntc_adc, ref=f"R{index}T1")
    ntc = Part("Device", "Thermistor_NTC", ref=f"TH{index}", value="10k B3435",
               footprint=R0402)
    ntc[1] += ntc_adc
    ntc[2] += gnd
    capacitor("10nF X7R", ntc_adc, gnd, ref=f"C{index}T1")
    mcu["PA3"] += ntc_adc

    # Driver supplies and TI-mandated charge-pump capacitors.
    drv["VM", "VDRAIN"] += vbat
    drv["AGND", "PGND", "EP", "VREF", "CAL"] += gnd
    dvdd = Net(f"{prefix}_DRV_DVDD")
    drv["DVDD"] += dvdd
    capacitor("1uF 6.3V X7R", dvdd, gnd, ref=f"C{index}D1")
    capacitor("100nF 100V X7R", vbat, gnd, ref=f"C{index}D2",
              footprint=C0603)
    capacitor("10uF 50V X7R", vbat, gnd, ref=f"C{index}D3",
              footprint="Capacitor_SMD:C_1210_3225Metric")
    capacitor("47nF 100V X7R", drv["CPH"], drv["CPL"], ref=f"C{index}D4")
    capacitor("1uF 25V X7R", drv["VCP"], vbat, ref=f"C{index}D5",
              footprint=C0603)

    # Hardware-interface straps from TI Figure 8-23/8-24:
    # MODE=AGND -> 6-PWM; IDRIVE=Hi-Z -> 120/240 mA; VDS=18k to AGND ->
    # 0.13 V OCP; GAIN=47k to AGND -> 10 V/V.
    drv["MODE"] += gnd
    NC += drv["IDRIVE"]
    resistor("18k 5%", drv["VDS"], gnd, ref=f"R{index}D1")
    resistor("47k 5%", drv["GAIN"], gnd, ref=f"R{index}D2")
    enable = Net(f"{prefix}_DRV_ENABLE")
    drv["ENABLE"] += enable
    resistor("10k", v3, enable, ref=f"R{index}D3")
    capacitor("100nF", enable, gnd, ref=f"C{index}D6")
    nfault = Net(f"{prefix}_NFAULT")
    drv["NFAULT"] += nfault
    resistor("10k", nfault, v3, ref=f"R{index}D4")
    mcu["PB5"] += nfault

    # Six exact SuperSO8 MOSFETs form three half bridges.  Every low-side
    # source returns through a single Kelvin-sensed 0.5 mOhm / 10 W shunt.
    for phase_number, letter in enumerate("ABC", 1):
        qh = bsc012(f"Q{index}{phase_number * 2 - 1}")
        ql = bsc012(f"Q{index}{phase_number * 2}")
        gate_h = Net(f"{prefix}_GATE_{letter}H")
        gate_l = Net(f"{prefix}_GATE_{letter}L")
        drv[f"GH{letter}"] += gate_h
        drv[f"GL{letter}"] += gate_l
        drv[f"SH{letter}"] += phase[letter]
        qh["G"] += gate_h
        qh["D"] += vbat
        qh["S1", "S2", "S3"] += phase[letter]
        ql["G"] += gate_l
        ql["D"] += phase[letter]
        ql["S1", "S2", "S3"] += power_return

    shunt = Part("Device", "R", ref=f"RSH{index}",
                 value="WSLF2512R0005FEA 0.5m 1% 10W",
                 footprint="Resistor_SMD:R_2512_6332Metric")
    shunt[1] += power_return
    shunt[2] += gnd
    drv["SPA"] += power_return
    drv["SNA"] += gnd
    drv["SPB", "SNB", "SPC", "SNC"] += gnd
    drv["SOA"] += current_adc
    mcu["PA2"] += current_adc
    NC += drv["SOB", "SOC"]

    # PB6 is AM32's 115200-baud serial telemetry pin.  A cathode-at-MCU
    # Schottky gives four-channel wired-low isolation onto the shared line.
    diode("BAT54H", esc_telem, mcu["PB6_TX"], ref=f"DT{index}")

    # Motor edge pads and currently unused GPIOs are explicit.
    motor = Part("Connector_Generic", "Conn_01x03", ref=f"JM{index}",
                 value=f"{prefix}_MOTOR_PADS",
                 footprint="VYPER:MOTOR_EDGE_PADS_3X")
    for pin, letter in enumerate("ABC", 1):
        motor[pin] += phase[letter]
    NC += mcu["PF0", "PF1", "PA1", "PA11", "PA12", "PA15", "PB2",
              "PB3", "PB7", "PB8"]


# Shared telemetry pullup.  The four current outputs are averaged by equal
# resistors and amplified by exactly 4, producing 5 mV/A total-current scale.
resistor("4.7k", esc_telem, v3, ref="RT1")
current_average = Net("CURRENT_AVERAGE")
for index, net in enumerate(channel_currents, 1):
    resistor("10k 0.1%", net, current_average, ref=f"RS{index}")
u2 = Part("Amplifier_Operational", "TLV9061xDBV", ref="U2",
          value="TLV9061IDBVR", footprint="Package_TO_SOT_SMD:SOT-23-5")
u2["V+"] += v3
u2["V-"] += gnd
u2["+"] += current_average
current_feedback = Net("CURRENT_SUM_FB")
u2["-"] += current_feedback
u2["~"] += esc_current
resistor("10.0k 0.1%", current_feedback, gnd, ref="RS5")
resistor("30.1k 0.1%", esc_current, current_feedback, ref="RS6")
capacitor("100pF C0G", esc_current, current_feedback, ref="CS1")
capacitor("100nF X7R", v3, gnd, ref="CS2")

ERC()
generate_netlist(file_=str(OUT / "vyper_55a_esc.net"), tool=KICAD9)
print(f"wrote {OUT / 'vyper_55a_esc.net'}")
