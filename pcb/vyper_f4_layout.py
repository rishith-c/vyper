"""VYPER-F4 -- board definition shared by the generator and the test suite.

Everything geometric lives HERE, once. vyper_f4_gen.py turns it into a
.kicad_pcb; test_vyper_f4.py interrogates the same numbers for interactions.
If a dimension is not in this file, it does not exist.

WHY THESE NUMBERS
-----------------
Board 36 x 36 mm on the 30.5 x 30.5 pattern: that is the standard FC format
the VYPER fuselage shelf was already cut for, and it fits the 53 mm clear
shelf diameter with room for a wire loom.
shelf clear-width accepts.

CORNER RADIUS 5.0 leaves extra edge clearance for the curved fuselage wall and
soft-mount grommets. The rounded corner reach is sqrt(2)*(18-5)+5 = 23.38 mm
against a 26.5 mm cavity radius. After the 6S battery forced the body to Ø57,
even a sharp 36 mm square would fit at 25.46 mm radius, but with only 1.04 mm
radial margin; R5 keeps 3.12 mm.

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

STM32F405RGT6 immediately below it: SPI1 runs ~4 mm pad-to-pad, against the
<10 mm guideline for gyro-to-MCU traces.

POWER STAGE pinned to the +Y edge: the inductor sits 10.7 mm from the gyro
centre (rule is >= 10), and its courtyard clears the grommet keepouts.

USB-C and the 8-pin SH1.0 ESC socket are on the BOTTOM face -- the ESC stacks
below the FC, so its harness plugs straight up, and the USB faces the open
tail of the fuselage (config access is by a short right-angle extension
through the tail opening; the shell has no side hatch).
"""

BOARD_W = 36.0
BOARD_H = 36.0
CORNER_R = 5.0
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
    "U1_mcu_STM32F405RGT6": dict(pos=(0.0, -8.2), side="F",
                                 courtyard=(12.4, 12.4), pkg="LQFP-64 10x10"),
    "Y1_xtal_8MHz": dict(pos=(4.8, 0.3), side="F", courtyard=(3.2, 3.5),
                         pkg="3225"),
    # The first revision intentionally omits analog OSD.  The released netlist
    # uses this quiet area for the mandatory dedicated ICM-42688-P regulator.
    "U5_gyro_ldo_AP2112K": dict(pos=(7.0, 6.0), side="F",
                                courtyard=(3.4, 3.2), pkg="SOT-23-5"),
    "U6_flash_W25Q128": dict(pos=(-11.0, 6.2), side="F", courtyard=(6.5, 5.5),
                             pkg="SOIC-8 blackbox"),
    "U7_baro_BMP280": dict(pos=(-13.5, 0.0), side="F", courtyard=(2.5, 3.0),
                           pkg="LGA-8"),
    "L1_buck_inductor": dict(pos=(0.0, 13.2), side="F", courtyard=(4.6, 4.6),
                             pkg="4030 shielded", noisy=True),
    "U3_buck_TPS54360": dict(pos=(7.2, 13.2), side="F", courtyard=(6.2, 5.2),
                             pkg="TI PowerPAD-8 60V/3.5A", noisy=True),
    "U4_ldo_3v3": dict(pos=(-7.2, 13.2), side="F", courtyard=(3.4, 3.2),
                       pkg="SOT-23-5"),
    # -14.0 puts the receptacle mouth exactly flush with the -Y board edge,
    # which is where a USB-C mouth belongs; at -14.6 it overhung by 0.6.
    "J1_usbc": dict(pos=(0.0, -14.0), side="B", courtyard=(9.6, 8.0),
                    pkg="USB-C 16p receptacle"),
    # 5.5, not 8.2: at 8.2 the socket's corner sat 2.9 mm from the top-right
    # grommet centre, inside its Phi 8 keepout.
    "J2_esc_SH8": dict(pos=(5.5, 12.4), side="B", courtyard=(10.4, 4.4),
                       pkg="JST-SH 1.0 8-pin, standard 4-in-1 harness"),
}

# Solder pad groups: (x, y, label), 1.6 mm square pads, F side.
PAD_GROUPS = {
    "uart_left": [(-16.6, y, l) for y, l in
                  ((-9.0, "T2"), (-6.5, "R2"), (-4.0, "T4"), (-1.5, "R4"),
                   (1.0, "5V"), (3.5, "G"))],
    "vtx_cam_right": [(16.6, y, l) for y, l in
                      ((-9.0, "VTX"), (-6.5, "CAM"), (-4.0, "T6"),
                       (-1.5, "R6"), (1.0, "9V"), (3.5, "G"))],
    # Motor signal pads pulled inboard of the grommet keepouts: at the
    # traditional (+-13, +-13) corners every one of them sat inside a
    # keepout, and M3 additionally landed inside the blackbox flash courtyard.
    "motor_pads": [(-10.2, -13.2, "M1"), (10.2, -13.2, "M2"),
                   (-11.5, 11.0, "M3"), (11.5, 11.0, "M4")],
}

# Gyro rules (Betaflight manufacturer guidelines + IMU app notes)
GYRO_MAX_OFFCENTRE = 4.0
GYRO_MIN_TO_NOISY = 10.0
GYRO_MCU_TRACE_MAX = 10.0

HOLES = [(sx * HOLE_PITCH / 2, sy * HOLE_PITCH / 2)
         for sx in (-1, 1) for sy in (-1, 1)]
