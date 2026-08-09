"""VYPER-F4 -- board definition shared by the generator and the test suite.

Everything geometric lives HERE, once. vyper_f4_gen.py turns it into a
.kicad_pcb; test_vyper_f4.py interrogates the same numbers for interactions.
If a dimension is not in this file, it does not exist.

WHY THESE NUMBERS
-----------------
The board is 22 x 64 mm with R3 corners for the longitudinal vertical cassette.
Its 16 x 56 mm M2 pattern is independent of the ESC pattern so the FC can use
soft grommets while the power board remains rigidly coupled to its spreader.
Each 3.2 mm bore and 6 mm keepout is checked on both faces.

GYRO ICM-42688-P at (0, +4) remains close to the board centre. The switcher is
at the opposite longitudinal end, more than 20 mm away.

STM32F405RGT6 immediately below it: SPI1 remains below the 10 mm guideline,
<10 mm guideline for gyro-to-MCU traces.

POWER STAGE pinned to the +Y edge: the inductor sits 15.5 mm from the gyro
centre (rule is >= 10), and its courtyard clears the grommet keepouts.

The 4-pin USB service harness and 8-pin SH1.0 ESC socket are on the BOTTOM
face. The ESC harness plugs straight up, while the removable USB pigtail faces
the open tail; the shell needs no drag-producing side hatch.
"""

BOARD_W = 22.0
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
    "U2_gyro_ICM42688P": dict(pos=(0.0, 4.0), side="F", courtyard=(4.5, 5.0),
                              pkg="LGA-14 2.5x3.0"),
    "U1_mcu_STM32F405RGT6": dict(pos=(0.0, -9.4), side="F",
                                 courtyard=(12.4, 12.4), pkg="LQFP-64 10x10"),
    "Y1_xtal_8MHz": dict(pos=(7.4, -17.6), side="F", courtyard=(3.2, 3.5),
                         pkg="3225"),
    # The first revision intentionally omits analog OSD.  The released netlist
    # uses this quiet area for the mandatory dedicated ICM-42688-P regulator.
    "U5_gyro_ldo_AP2112K": dict(pos=(6.8, 4.0), side="F",
                                courtyard=(3.4, 3.2), pkg="SOT-23-5"),
    "U6_flash_W25Q128": dict(pos=(-5.8, 10.5), side="B", courtyard=(6.5, 5.5),
                             pkg="SOIC-8 blackbox"),
    "U7_baro_BMP280": dict(pos=(-8.0, 3.0), side="B", courtyard=(2.5, 3.0),
                           pkg="LGA-8"),
    "L1_buck_inductor": dict(pos=(-6.3, 21.0), side="F", courtyard=(4.6, 4.6),
                             pkg="4030 shielded", noisy=True),
    "U3_buck_TPS54360": dict(pos=(2.1, 21.0), side="F", courtyard=(6.2, 5.2),
                             pkg="TI PowerPAD-8 60V/3.5A", noisy=True),
    "U4_ldo_3v3": dict(pos=(8.4, 21.0), side="F", courtyard=(3.4, 3.2),
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
}

# Solder pad groups: (x, y, label), 1.6 mm square pads, F side.
PAD_GROUPS = {
    "J3_rx_uart1": [(-9.6, y, l) for y, l in
                     zip((-13.1, -9.4, -5.8, -2.2),
                         ("G", "5V", "T1", "R1"))],
    "J4_gps_uart3": [(-9.6, y, l) for y, l in
                      zip((1.5, 5.1, 8.7, 12.3),
                          ("G", "5V", "T3", "R3"))],
    "J5_aux_uart4": [(9.6, y, l) for y, l in
                      zip((-13.1, -9.4, -5.8, -2.2),
                          ("G", "5V", "T4", "R4"))],
    "J6_vtx_uart6": [(9.6, y, l) for y, l in
                      zip((1.5, 5.1, 8.7, 12.3),
                          ("G", "5V", "T6", "R6"))],
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
    "D5": dict(pos=(-6.5, -13.5), side="B", rot=0),
    "D6": dict(pos=(-3.2, -13.5), side="B", rot=0),
    "D7": dict(pos=(0.2, -13.5), side="B", rot=0),
    "R14": dict(pos=(3.8, -13.5), side="B", rot=0),
    "R15": dict(pos=(5.8, -13.5), side="B", rot=0),

    # ADC filters and status LED.
    "C29": dict(pos=(8.0, -4.0), side="B", rot=0),
    "C30": dict(pos=(8.0, -7.0), side="B", rot=0),
    "R16": dict(pos=(10.0, -4.0), side="B", rot=0),
    "R17": dict(pos=(12.0, -4.0), side="B", rot=0),
    "R18": dict(pos=(10.0, -7.0), side="B", rot=0),
    "D4": dict(pos=(15.0, -4.0), side="F", rot=0),
    "R19": dict(pos=(15.0, -6.0), side="F", rot=0),
}

# Stretch the proven functional clusters along the aircraft axis while
# compressing their transverse positions into the 22 mm board. Package sizes
# are never scaled; the true-footprint board and KiCad DRC remain authoritative.
for _spec in PASSIVES.values():
    _x, _y = _spec["pos"]
    _spec["pos"] = (round(_x * 0.47, 3), round(_y * 1.45, 3))

# True-footprint repack into functional longitudinal bays. Values include
# side and rotation because the narrow board deliberately uses both faces.
VERTICAL_PASSIVE_PLACEMENT = {
    # 60 V buck bay, F.Cu.
    "D1": ((4.3, 14.2), "F", 0),
    "C3": ((1.2, 17.0), "F", 0),
    "C4": ((4.5, 17.0), "F", 0),
    "C6": ((8.3, 17.0), "F", 0),
    "C5": ((-6.5, 15.0), "F", 0),
    "C7": ((-1.7, 14.5), "F", 0),
    "R1": ((0.0, 11.0), "F", 0),
    "R2": ((2.2, 11.0), "F", 0),
    "R3": ((4.4, 11.0), "F", 0),
    "R4": ((6.6, 11.0), "F", 0),
    "R5": ((0.0, 9.2), "F", 0),
    "R6": ((2.2, 9.2), "F", 0),
    "C1": ((4.4, 9.2), "F", 0),
    "C2": ((6.6, 9.2), "F", 0),
    "C8": ((7.5, 17.0), "B", 0),
    "C9": ((7.5, 19.0), "B", 0),
    "D2": ((4.8, 12.5), "B", 0),
    "D3": ((0.0, 17.0), "B", 0),

    # Gyro and MCU bay, F.Cu.
    "C10": ((6.8, 7.2), "F", 0),
    "C11": ((9.0, 7.2), "F", 0),
    "FB1": ((-4.0, -1.2), "F", 0),
    "C12": ((-5.5, -3.0), "B", 0),
    "C13": ((-3.0, -3.0), "B", 0),
    "C14": ((-0.5, -3.0), "B", 0),
    "C15": ((2.0, -3.0), "B", 0),
    "C16": ((-5.5, -5.5), "B", 0),
    "C17": ((-3.0, -5.5), "B", 0),
    "C18": ((0.0, -5.5), "B", 0),
    "C19": ((-4.5, -18.2), "F", 0),
    "C20": ((-1.0, -18.2), "F", 0),
    "C23": ((-4.5, -20.2), "F", 0),
    "R8": ((-2.0, -20.2), "F", 0),
    "R9": ((0.2, -20.2), "F", 0),
    "C21": ((5.2, -21.0), "F", 0),
    "C22": ((8.0, -21.5), "F", 0),
    "R7": ((3.8, -17.5), "F", 0),
    "C24": ((-3.2, 4.0), "F", 0),
    "C25": ((0.0, 7.2), "F", 0),

    # Sensor support follows the B-side flash and barometer.
    "C26": ((-5.0, 6.2), "B", 0),
    "R10": ((-7.2, 6.2), "B", 0),
    "R11": ((-9.2, 6.2), "B", 0),
    "C27": ((-5.2, 3.0), "B", 0),
    "R12": ((-7.0, 0.5), "B", 0),
    "R13": ((-9.2, 0.5), "B", 0),

    # USB service and analog monitoring, B.Cu.
    "C28": ((7.5, -24.0), "B", 0),
    "D5": ((-3.8, -10.0), "B", 0),
    "D6": ((0.0, -10.0), "B", 0),
    "D7": ((3.8, -10.0), "B", 0),
    "R14": ((6.5, -10.0), "B", 0),
    "R15": ((8.8, -10.0), "B", 0),
    "C29": ((4.0, -5.0), "B", 0),
    "R16": ((6.2, -5.0), "B", 0),
    "R17": ((8.4, -5.0), "B", 0),
    "C30": ((4.0, -7.5), "B", 0),
    "R18": ((6.2, -7.5), "B", 0),

    # Status LED at the lower service end.
    "D4": ((8.0, -24.0), "F", 0),
    "R19": ((5.2, -24.0), "F", 0),
}
for _ref, (_pos, _side, _rot) in VERTICAL_PASSIVE_PLACEMENT.items():
    PASSIVES[_ref].update(pos=_pos, side=_side, rot=_rot)

# Gyro rules (Betaflight manufacturer guidelines + IMU app notes)
GYRO_MAX_OFFCENTRE = 4.0
GYRO_MIN_TO_NOISY = 10.0
GYRO_MCU_TRACE_MAX = 10.0

HOLES = [(sx * HOLE_PITCH_X / 2, sy * HOLE_PITCH_Y / 2)
         for sx in (-1, 1) for sy in (-1, 1)]
