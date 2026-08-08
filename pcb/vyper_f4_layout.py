"""VYPER-F4 -- board definition shared by the generator and the test suite.

Everything geometric lives HERE, once. vyper_f4_gen.py turns it into a
.kicad_pcb; test_vyper_f4.py interrogates the same numbers for interactions.
If a dimension is not in this file, it does not exist.

WHY THESE NUMBERS
-----------------
The custom board is 43 x 43 mm with R12 corners on the 30.5 x 30.5 pattern.
Its 25.44 mm corner reach fits the 26.5 mm cavity radius with 1.06 mm radial
allowance. The original 36 mm study could place the ICs but could not keep the
TPS54360 power loop compact and 10 mm away from the gyro once true passive
footprints were considered. The purchased prototype stack remains 36 mm.

MOUNTING HOLES Phi 4.0, not 3.2: M3 bolts pass through rubber soft-mount
grommets, per the Betaflight manufacturer guidelines -- board flex from hard
mounting shifts the gyro bias, and the grommet needs the extra bore. Hole
edge lands 0.75 mm from the board edge, which is tight but standard for this
format. Each grommet claims a Phi 8 mechanical keepout ON BOTH SIDES.

GYRO ICM-42688-P at (0, +2.5), 2.5 mm off true centre: dead centre is blocked
by the one-courtyard-wide ring every other part needs. 2.5 mm from the
rotation axes is well inside Betaflight's "near centre" guidance; what
matters far more is the 10 mm exclusion from the buck inductor (magnetic
coupling reads as vibration) and a solid ground pour under the package.

STM32F405RGT6 immediately below it: SPI1 remains below the 10 mm guideline,
<10 mm guideline for gyro-to-MCU traces.

POWER STAGE pinned to the +Y edge: the inductor sits 15.5 mm from the gyro
centre (rule is >= 10), and its courtyard clears the grommet keepouts.

The 4-pin USB service harness and 8-pin SH1.0 ESC socket are on the BOTTOM
face. The ESC harness plugs straight up, while the removable USB pigtail faces
the open tail; the shell needs no drag-producing side hatch.
"""

BOARD_W = 43.0
BOARD_H = 43.0
CORNER_R = 12.0
FUSE_CAVITY_R = 26.5          # from vyper_shell.py: R_MAX 28.5 - WALL 2
SHELF_CLEAR_R = 27.0          # printed shelf radius the board rests on
SHELF_VENT_D = 18.0           # central loom hole in the shelf

HOLE_PITCH = 30.5
HOLE_D = 4.0                  # M3 + soft-mount grommet
GROMMET_KEEPOUT_D = 8.0       # mechanical, both sides

# ---------------------------------------------------------------------------
# Parts. courtyard = (w, h) centred on pos unless noted. side: F or B.
# ---------------------------------------------------------------------------
PARTS = {
    "U2_gyro_ICM42688P": dict(pos=(0.0, 2.5), side="F", courtyard=(4.5, 5.0),
                              pkg="LGA-14 2.5x3.0"),
    "U1_mcu_STM32F405RGT6": dict(pos=(0.0, -6.5), side="F",
                                 courtyard=(12.4, 12.4), pkg="LQFP-64 10x10"),
    "Y1_xtal_8MHz": dict(pos=(9.5, -1.0), side="F", courtyard=(3.2, 3.5),
                         pkg="3225"),
    # The first revision intentionally omits analog OSD.  The released netlist
    # uses this quiet area for the mandatory dedicated ICM-42688-P regulator.
    "U5_gyro_ldo_AP2112K": dict(pos=(8.0, 2.8), side="F",
                                courtyard=(3.4, 3.2), pkg="SOT-23-5"),
    "U6_flash_W25Q128": dict(pos=(-13.0, 7.0), side="F", courtyard=(6.5, 5.5),
                             pkg="SOIC-8 blackbox"),
    "U7_baro_BMP280": dict(pos=(-17.0, 0.0), side="F", courtyard=(2.5, 3.0),
                           pkg="LGA-8"),
    "L1_buck_inductor": dict(pos=(0.0, 18.0), side="F", courtyard=(4.6, 4.6),
                             pkg="4030 shielded", noisy=True),
    "U3_buck_TPS54360": dict(pos=(8.0, 15.5), side="F", courtyard=(6.2, 5.2),
                             pkg="TI PowerPAD-8 60V/3.5A", noisy=True),
    "U4_ldo_3v3": dict(pos=(-8.0, 12.0), side="F", courtyard=(3.4, 3.2),
                       pkg="SOT-23-5"),
    "J1_usb_service_SH4": dict(pos=(0.0, -18.0), side="B",
                                courtyard=(7.0, 4.6),
                                pkg="JST-SH 1.0 4-pin USB service harness"),
    # 5.5, not 8.2: at 8.2 the socket's corner sat 2.9 mm from the top-right
    # grommet centre, inside its Phi 8 keepout.
    "J2_esc_SH8": dict(pos=(0.0, 18.0), side="B", courtyard=(10.4, 4.4),
                       pkg="JST-SH 1.0 8-pin, standard 4-in-1 harness"),
    "J7_swd_testpads": dict(pos=(-8.0, 0.0), side="B", courtyard=(3.2, 3.2),
                             pkg="2x2 1.27 mm SWD test pads"),
    "J8_beeper_pads": dict(pos=(-10.0, 11.5), side="B", courtyard=(4.0, 2.4),
                            pkg="1x2 1.27 mm beeper pads"),
}

# Solder pad groups: (x, y, label), 1.6 mm square pads, F side.
PAD_GROUPS = {
    "J3_rx_uart1": [(-20.1, y, l) for y, l in
                     zip((-9.0, -6.5, -4.0, -1.5),
                         ("G", "5V", "T1", "R1"))],
    "J4_gps_uart3": [(-20.1, y, l) for y, l in
                      zip((1.0, 3.5, 6.0, 8.5),
                          ("G", "5V", "T3", "R3"))],
    "J5_aux_uart4": [(20.1, y, l) for y, l in
                      zip((-9.0, -6.5, -4.0, -1.5),
                          ("G", "5V", "T4", "R4"))],
    "J6_vtx_uart6": [(20.1, y, l) for y, l in
                      zip((1.0, 3.5, 6.0, 8.5),
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

# Gyro rules (Betaflight manufacturer guidelines + IMU app notes)
GYRO_MAX_OFFCENTRE = 4.0
GYRO_MIN_TO_NOISY = 10.0
GYRO_MCU_TRACE_MAX = 10.0

HOLES = [(sx * HOLE_PITCH / 2, sy * HOLE_PITCH / 2)
         for sx in (-1, 1) for sy in (-1, 1)]
