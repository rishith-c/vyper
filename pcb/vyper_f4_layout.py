"""VYPER-F4 -- board definition shared by the generator and the test suite.

Everything geometric lives HERE, once. vyper_f4_gen.py turns it into a
.kicad_pcb; test_vyper_f4.py interrogates the same numbers for interactions.
If a dimension is not in this file, it does not exist.

WHY THESE NUMBERS
-----------------
The board is 30 x 64 mm with R3 corners for the longitudinal vertical cassette.
Its 16 x 56 mm M2 pattern is independent of the ESC pattern so the FC can use
soft grommets while the power board remains rigidly coupled to its spreader.
Each 3.2 mm bore and 6 mm keepout is checked on both faces.

GYRO ICM-42688-P at the board centre keeps rotational vibration coupling low.
The switcher is at the opposite longitudinal end, more than 20 mm away.

STM32F405RGT6 immediately below it keeps the SPI1 courtyard gap below the
10 mm routing guideline.

POWER STAGE pinned to the +Y edge: the inductor sits 15.5 mm from the gyro
centre (rule is >= 10), and its courtyard clears the grommet keepouts.

The 4-pin USB service harness and 8-pin SH1.0 ESC socket are on the BOTTOM
face. The ESC harness plugs straight up, while the removable USB pigtail faces
the open tail; the shell needs no drag-producing side hatch.
"""

BOARD_W = 30.0
BOARD_H = 64.0
CORNER_R = 3.0
HOLE_PITCH_X = 16.0
HOLE_PITCH_Y = 56.0
HOLE_D = 3.2                  # M2 bolt through soft grommet
GROMMET_KEEPOUT_D = 6.0       # mechanical, both sides

# ---------------------------------------------------------------------------
# Parts. courtyard = (w, h) centred on pos unless noted. side: F or B.
# ---------------------------------------------------------------------------
PARTS = {
    # Rotate the IMU so its signal edges face the MCU escape channel. Firmware
    # applies the matching CW90 alignment; this is a routing/EMI choice, not an
    # axis assumption.
    "U2_gyro_ICM42688P": dict(pos=(0.0, 0.0), side="F", rot=90,
                              courtyard=(4.5, 5.0), pkg="LGA-14 2.5x3.0"),
    # Rot0 puts alternate SPI1 pins PB3/PB4/PB5 and adjacent gyro CS/INT
    # GPIOs on the gyro-facing edge. This eliminates the package-crossing
    # routes required by the default PA5/PA6/PA7 pin group.
    "U1_mcu_STM32F405RGT6": dict(pos=(2.0, -9.5), side="F", rot=0,
                                 courtyard=(12.4, 12.4), pkg="LQFP-64 10x10"),
    "Y1_xtal_8MHz": dict(pos=(-7.0, -8.0), side="B", rot=180,
                         courtyard=(4.3, 3.6),
                         pkg="3225"),
    # The first revision intentionally omits analog OSD.  The released netlist
    # uses this quiet area for the mandatory dedicated ICM-42688-P regulator.
    "U5_gyro_ldo_AP2112K": dict(pos=(5.0, 2.0), side="F", rot=180,
                                courtyard=(3.4, 3.2), pkg="SOT-23-5"),
    # The flash sits below the MCU's SPI2-facing edge and is rotated so its
    # narrow courtyard leaves a central passive-routing channel.
    "U6_flash_W25Q128": dict(pos=(8.0, -10.0), side="B", rot=90,
                             courtyard=(5.6, 7.3),
                             pkg="W25Q128JVPIM WSON-8 6x5 blackbox"),
    "U7_baro_BMP280": dict(pos=(-9.5, -1.0), side="B", courtyard=(2.5, 3.0),
                            pkg="LGA-8"),
    # TPS54360 rotated 90 degrees places SW/GND on its forward edge. The
    # inductor, catch diode and bootstrap capacitor surround that edge so the
    # high-di/dt loop is physically small before routing begins.
    "L1_buck_inductor": dict(pos=(-8.0, 19.7), side="F", rot=180,
                             courtyard=(8.4, 7.5),
                             pkg="Wuerth HCI-7050 8.2uH", noisy=True),
    "U3_buck_TPS54360": dict(pos=(0.0, 17.0), side="F", rot=90,
                             courtyard=(5.6, 7.6),
                             pkg="TI PowerPAD-8 60V/3.5A", noisy=True),
    # The logic LDO moves to B.Cu, outside the switch-node field but beside
    # its two local bypass capacitors.
    "U4_ldo_3v3": dict(pos=(8.5, 18.0), side="B", courtyard=(4.2, 3.5),
                       pkg="SOT-23-5"),
    "J1_usb_service_SH4": dict(pos=(0.0, -28.5), side="B",
                                courtyard=(7.0, 4.6),
                                pkg="JST-SH 1.0 4-pin USB service harness"),
    # 5.5, not 8.2: at 8.2 the socket's corner sat 2.9 mm from the top-right
    # grommet centre, inside its Phi 8 keepout.
    "J2_esc_SH8": dict(pos=(0.0, -18.5), side="B", rot=90,
                       courtyard=(6.65, 11.9),
                       pkg="JST-SH 1.0 8-pin, standard 4-in-1 harness"),
    "J7_swd_testpads": dict(pos=(-7.0, -17.5), side="B", courtyard=(3.2, 3.2),
                             pkg="2x2 1.27 mm SWD test pads"),
    "J8_beeper_pads": dict(pos=(7.0, -17.5), side="B", courtyard=(4.0, 2.4),
                            pkg="1x2 1.27 mm beeper pads"),
    "U8_rgb_level_shifter": dict(pos=(-8.0, -20.5), side="F",
                                  courtyard=(3.4, 3.2),
                                  pkg="SN74AHCT1G125 SOT-23-5"),
    # Horizontal flow-through orientation preserves D-/D+ order through the
    # right-to-left bend: the MCU pair enters pins 3/1 and exits pins 4/6.
    "U9_usb_esd_USBLC6": dict(pos=(0.0, -21.5), side="F", rot=180,
                               courtyard=(3.5, 4.2),
                               pkg="USBLC6-2SC6 SOT-23-6"),
    "D4_rgb_status": dict(pos=(-2.0, -26.0), side="F", courtyard=(4.0, 4.0),
                           pkg="SK6812MINI-E 3.5x3.5"),
}

# Dual-purpose 2.54 mm header / wire groups.  Each location is a 2.4 mm plated
# through-hole pad with a 1.0 mm finished drill, accepting a 0.64 mm square
# header pin or 26--28 AWG stripped wire.  The order follows Betaflight's
# GND, 5V, TX, RX connector convention.
IO_PAD_SIZE = (2.4, 2.0)
IO_PAD_DRILL = 1.0
IO_PAD_PITCH = 2.54
IO_PAD_X = 13.2
IO_GROUP_Y = (-7.65, 6.90)


def io_group(x, center_y, labels):
    return [(x, center_y + (index - 1.5) * IO_PAD_PITCH, label)
            for index, label in enumerate(labels)]


PAD_GROUPS = {
    "J3_rx_uart1": io_group(-IO_PAD_X, IO_GROUP_Y[0], ("G", "5V", "T1", "R1")),
    "J4_gps_uart3": io_group(-IO_PAD_X, IO_GROUP_Y[1], ("G", "5V", "T3", "R3")),
    "J5_external_i2c": io_group(IO_PAD_X, IO_GROUP_Y[0], ("G", "5V", "DA", "CL")),
    "J6_vtx_uart6": io_group(IO_PAD_X, IO_GROUP_Y[1], ("G", "5V", "T6", "R6")),
}

# Explicit functional placement for every passive in vyper_f4.net. Critical
# switching parts stay on F.Cu around U3/L1; sensor and MCU support parts hug
# their consumers; USB/ADC service parts use the quiet B.Cu regions. Rotation
# is in degrees before any B-side flip.
PASSIVES = {
    # TPS54360 power loop and compensation.
    "D1": dict(pos=(0.0, 12.5), side="F", rot=0),
    "C3": dict(pos=(6.5, 11.0), side="F", rot=0),
    "C4": dict(pos=(4.0, 8.5), side="F", rot=0),
    "C6": dict(pos=(9.0, 10.5), side="F", rot=0),
    "C5": dict(pos=(-7.2, 18.7), side="F", rot=0),
    "C7": dict(pos=(-7.2, 15.3), side="F", rot=0),
    "R1": dict(pos=(10.0, 12.0), side="F", rot=0),
    "R2": dict(pos=(12.0, 12.0), side="F", rot=0),
    "R3": dict(pos=(12.0, 10.0), side="F", rot=0),
    "R4": dict(pos=(8.5, 8.8), side="F", rot=0),
    "R5": dict(pos=(6.5, 8.8), side="F", rot=0),
    "R6": dict(pos=(10.2, 7.3), side="F", rot=0),
    "C1": dict(pos=(12.5, 7.3), side="F", rot=0),
    "C2": dict(pos=(8.0, 7.3), side="F", rot=0),

    # Diode-OR and local LDO support.
    "D2": dict(pos=(-3.0, 12.0), side="B", rot=0),
    "D3": dict(pos=(-7.0, -10.5), side="B", rot=0),
    "C8": dict(pos=(-11.2, 12.0), side="F", rot=0),
    "C9": dict(pos=(-11.2, 14.0), side="F", rot=0),
    "C10": dict(pos=(11.5, 2.5), side="F", rot=0),
    "C11": dict(pos=(11.5, 4.0), side="F", rot=0),

    # STM32 analog rail, VDD and VCAP decoupling, reset and boot.
    "FB1": dict(pos=(-8.0, -2.0), side="F", rot=0),
    "C12": dict(pos=(-8.2, -11.5), side="F", rot=0),
    "C13": dict(pos=(-8.2, -9.5), side="F", rot=0),
    "C14": dict(pos=(-8.2, -7.5), side="F", rot=0),
    "C15": dict(pos=(-8.2, -5.5), side="F", rot=0),
    "C16": dict(pos=(8.2, -11.5), side="F", rot=0),
    "C17": dict(pos=(8.2, -9.5), side="F", rot=0),
    "C18": dict(pos=(8.4, -7.2), side="F", rot=0),
    "C19": dict(pos=(4.5, -14.0), side="F", rot=0),
    "C20": dict(pos=(1.5, -14.0), side="F", rot=0),
    "C23": dict(pos=(-1.5, -14.0), side="F", rot=0),
    "R8": dict(pos=(-4.5, -14.0), side="F", rot=0),
    "R9": dict(pos=(-7.5, -14.0), side="F", rot=0),

    # HSE, gyro, flash and barometer local networks.
    "C21": dict(pos=(13.2, -2.5), side="F", rot=0),
    "C22": dict(pos=(13.2, 0.0), side="F", rot=0),
    "R7": dict(pos=(9.5, -3.6), side="F", rot=0),
    "C24": dict(pos=(-3.0, 3.0), side="F", rot=0),
    "C25": dict(pos=(3.8, 3.0), side="F", rot=0),
    "C26": dict(pos=(-6.8, 7.0), side="F", rot=0),
    "R10": dict(pos=(-6.8, 5.2), side="F", rot=0),
    "R11": dict(pos=(-6.8, 8.8), side="F", rot=0),
    "C27": dict(pos=(-14.5, 1.5), side="F", rot=0),
    "R12": dict(pos=(-14.5, 0.0), side="F", rot=0),
    "R13": dict(pos=(-14.5, -1.5), side="F", rot=0),

    # USB service harness protection and termination.
    "C28": dict(pos=(6.0, -17.0), side="B", rot=0),
    "D7": dict(pos=(0.2, -13.5), side="B", rot=0),
    "R14": dict(pos=(3.8, -13.5), side="B", rot=0),
    "R15": dict(pos=(5.8, -13.5), side="B", rot=0),

    # ADC filters and status LED.
    "C29": dict(pos=(8.0, -4.0), side="B", rot=0),
    "C30": dict(pos=(8.0, -7.0), side="B", rot=0),
    "R16": dict(pos=(10.0, -4.0), side="B", rot=0),
    "R17": dict(pos=(12.0, -4.0), side="B", rot=0),
    "R18": dict(pos=(10.0, -7.0), side="B", rot=0),
    "R19": dict(pos=(15.0, -6.0), side="F", rot=0),
    "R20": dict(pos=(14.0, -6.0), side="F", rot=0),
    "C31": dict(pos=(13.0, -6.0), side="F", rot=0),
}

# Stretch the proven functional clusters along the aircraft axis while
# compressing their transverse positions into the narrow board. Package sizes
# are never scaled; the true-footprint board and KiCad DRC remain authoritative.
for _spec in PASSIVES.values():
    _x, _y = _spec["pos"]
    _spec["pos"] = (round(_x * 0.47, 3), round(_y * 1.45, 3))

# True-footprint repack into functional longitudinal bays. Values include
# side and rotation because the narrow board deliberately uses both faces.
VERTICAL_PASSIVE_PLACEMENT = {
    # 60 V buck bay, F.Cu.
    "D1": ((1.1, 22.8), "F", 0),
    "C3": ((-3.3, 17.0), "F", 90),
    "C4": ((-0.8, 11.5), "F", 270),
    "C6": ((1.2, 11.5), "F", 270),
    "C5": ((-9.0, 13.5), "F", 0),
    # A second output capacitor sits directly under L1 on B.Cu; short power
    # vias will connect it to V5/GND without consuming the F.Cu switch bay.
    "C7": ((-8.0, 19.7), "B", 0),
    "R1": ((4.0, 14.3), "F", 0),
    "R2": ((-1.0, 8.8), "F", 0),
    "R3": ((1.2, 8.8), "F", 0),
    "R4": ((6.3, 18.2), "F", 180),
    "R5": ((6.3, 16.5), "F", 0),
    "R6": ((3.9, 19.2), "F", 0),
    "C1": ((6.3, 20.3), "F", 0),
    "C2": ((4.0, 16.0), "F", 0),
    "C8": ((11.7, 16.0), "B", 0),
    "C9": ((11.8, 18.0), "B", 0),
    "D2": ((7.0, 13.0), "B", 0),
    "D3": ((-8.5, -22.5), "B", 0),

    # Gyro and MCU bay, F.Cu.
    "C10": ((8.0, 2.0), "F", 0),
    "C11": ((3.0, 4.5), "F", 0),
    # VDDA filter and both bypass capacitors form one compact F.Cu island at
    # pin 13. The bead is vertical so its noisy V3V3 side points outward while
    # the filtered side fans directly into the two capacitors and MCU pad.
    "FB1": ((-5.8, -11.75), "F", 90),
    "C12": ((-7.4, -10.7), "F", 180),
    "C13": ((-7.4, -12.0), "F", 180),
    "C14": ((-2.8, -5.0), "B", 180),
    "C15": ((6.2, -5.75), "B", 180),
    "C16": ((4.3, -14.3), "B", 180),
    "C17": ((-5.0, -14.5), "B", 0),
    "C18": ((10.0, -15.0), "B", 0),
    # Rotate VCAP1's capacitor so pad 1 directly faces the matching MCU pin;
    # its ground pad then points outward to a dedicated plane via.
    "C19": ((5.25, -17.85), "F", 270),
    "C20": ((10.4, -6.25), "F", 0),
    "C23": ((-2.0, -8.5), "B", 0),
    "R8": ((0.0, -8.5), "B", 0),
    "R9": ((-3.5, -6.0), "B", 0),
    # Crystal and load network share the quiet B.Cu edge channel beside HSE.
    "C21": ((-4.8, -11.0), "B", 0),
    "C22": ((-9.2, -11.0), "B", 0),
    "R7": ((-7.0, -11.5), "B", 90),
    # The 100 nF gyro bypass sits on B.Cu directly behind the package edge;
    # paired power/ground vias keep its loop short without blocking SPI escape.
    "C24": ((0.0, 1.8), "B", 0),
    "C25": ((0.0, 3.8), "F", 0),

    # Sensor support follows the B-side flash and barometer.
    "C26": ((3.5, -7.0), "B", 0),
    "R10": ((3.5, -9.0), "B", 0),
    "R11": ((3.5, -11.0), "B", 0),
    "C27": ((-9.5, 1.5), "B", 0),
    "R12": ((-7.5, 1.0), "B", 0),
    "R13": ((-11.5, 1.0), "B", 0),

    # USB service and analog monitoring, B.Cu.
    # VBUS TVS/bypass face the service-channel feed; their ground pads point
    # outward to dedicated plane vias instead of lying in the hot path.
    "C28": ((10.5, -24.0), "B", 90),
    "D7": ((7.0, -24.0), "B", 180),
    # Vertical source terminators give D-/D+ a symmetric, non-crossing launch
    # from the MCU into the long service-end pair.
    "R14": ((9.3, -8.3), "F", 90),
    "R15": ((10.6, -8.3), "F", 90),
    "C29": ((9.0, -4.2), "B", 0),
    "R16": ((9.0, -2.0), "B", 0),
    "R17": ((11.0, -2.0), "B", 0),
    "C30": ((-3.8, -12.0), "B", 0),
    "R18": ((-1.8, -12.0), "B", 0),

    # Level-shifted addressable RGB status LED at the lower service end. Keep
    # the data resistor left of the USB ESD array so the protected differential
    # pair owns the central service-channel escape without a courtyard clash.
    "R19": ((-4.5, -22.5), "F", 0),
    "R20": ((-8.0, -18.0), "F", 0),
    # Local LED bypass sits outside D4's optical/package courtyard.
    "C31": ((-7.0, -24.5), "F", 90),
}
for _ref, (_pos, _side, _rot) in VERTICAL_PASSIVE_PLACEMENT.items():
    PASSIVES[_ref].update(pos=_pos, side=_side, rot=_rot)

# Gyro rules (Betaflight manufacturer guidelines + IMU app notes)
GYRO_MAX_OFFCENTRE = 4.0
GYRO_MIN_TO_NOISY = 10.0
GYRO_MCU_TRACE_MAX = 10.0

HOLES = [(sx * HOLE_PITCH_X / 2, sy * HOLE_PITCH_Y / 2)
         for sx in (-1, 1) for sy in (-1, 1)]
