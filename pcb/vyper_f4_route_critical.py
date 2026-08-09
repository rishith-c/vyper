"""Seed electrically critical copper on the VYPER-F4 review board.

This script starts from the generated, unrouted board and writes a separate
critical-route candidate. It deliberately does not touch the unrouted source.
The current stage implements the TPS54360 power loop, dedicated gyro supply,
gyro SPI/interrupt bus, HSE crystal network, and a continuous In1 GND plane.
USB and remaining power/signal routes are added in subsequent reviewed stages.
The output is still NOT FOR FAB until every route and release gate passes.

Run with KiCad's bundled Python 3.9.
"""

from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "vyper_f4_unrouted.kicad_pcb"
OUTPUT = HERE / "vyper_f4_critical.kicad_pcb"


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


board = pcbnew.LoadBoard(str(SOURCE))
footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
nets = board.GetNetInfo().NetsByName()


def net(name):
    assert name in nets, f"missing net {name}"
    return nets[name]


def pad(ref, number, expected_net=None):
    matches = [p for p in footprints[ref].Pads()
               if p.GetNumber() == str(number)]
    assert matches, f"missing pad {ref}.{number}"
    selected = matches[0]
    if expected_net is not None:
        assert selected.GetNetname() == expected_net, (
            f"{ref}.{number}: {selected.GetNetname()} != {expected_net}")
    return selected


def xy(item):
    position = item.GetPosition()
    return pcbnew.ToMM(position.x), pcbnew.ToMM(position.y)


def add_track(net_name, layer, width, points):
    """Add a same-layer polyline whose first/last points land on pads/vias."""
    n = net(net_name)
    for start, end in zip(points, points[1:]):
        segment = pcbnew.PCB_TRACK(board)
        segment.SetStart(point(*start))
        segment.SetEnd(point(*end))
        segment.SetLayer(layer)
        segment.SetWidth(mm(width))
        segment.SetNetCode(n.GetNetCode())
        board.Add(segment)


def add_via(net_name, position, size=0.65, drill=0.30):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(*position))
    via.SetWidth(mm(size))
    via.SetDrill(mm(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNetCode(net(net_name).GetNetCode())
    board.Add(via)
    return position


def add_ground_plane():
    """Create the uninterrupted In1 GND reference plane, inset from edges."""
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.In1_Cu)
    zone.SetNetCode(net("GND").GetNetCode())
    zone.SetLocalClearance(mm(0.20))
    zone.SetMinThickness(mm(0.20))
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((-12.0, -31.5), (12.0, -31.5), (14.5, -29.0),
                 (14.5, 29.0), (12.0, 31.5), (-12.0, 31.5),
                 (-14.5, 29.0), (-14.5, -29.0)):
        outline.Append(mm(x), mm(y))
    board.Add(zone)


def add_logic_plane():
    """Create the In2 3V3 distribution plane around routed signal keepouts."""
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.In2_Cu)
    zone.SetNetCode(net("V3V3").GetNetCode())
    zone.SetLocalClearance(mm(0.20))
    zone.SetMinThickness(mm(0.20))
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((-12.0, -31.5), (12.0, -31.5), (14.5, -29.0),
                 (14.5, 29.0), (12.0, 31.5), (-12.0, 31.5),
                 (-14.5, 29.0), (-14.5, -29.0)):
        outline.Append(mm(x), mm(y))
    board.Add(zone)


# ------------------------------------------------------------------ GND plane
add_ground_plane()
add_logic_plane()

# ------------------------------------------------------------ compact SW node
u3_sw = xy(pad("U3", 8, "BUCK_SW"))
l1_sw = xy(pad("L1", 1, "BUCK_SW"))
d1_sw = xy(pad("D1", 1, "BUCK_SW"))
c3_sw = xy(pad("C3", 2, "BUCK_SW"))

# U3-to-L1 is the high-current spine. C3 and D1 branch at U3 without allowing
# the switch copper to spread into a large EMI-radiating polygon.
add_track("BUCK_SW", pcbnew.F_Cu, 1.00, (l1_sw, u3_sw))
add_track("BUCK_SW", pcbnew.F_Cu, 0.50,
          (c3_sw, (c3_sw[0], u3_sw[1]), u3_sw))
add_track("BUCK_SW", pcbnew.F_Cu, 0.90,
          (u3_sw, (-2.20, -21.10), d1_sw))

# Bootstrap capacitor: short, symmetric route back to BOOT while its other end
# already lands on the compact switch branch above.
u3_boot = xy(pad("U3", 1, "BUCK_BOOT"))
c3_boot = xy(pad("C3", 1, "BUCK_BOOT"))
add_track("BUCK_BOOT", pcbnew.F_Cu, 0.25,
          (u3_boot, (-2.55, -14.95), c3_boot))

# --------------------------------------------------------- input hot-loop side
u3_vin = xy(pad("U3", 2, "VBAT_6S"))
c4_vin = xy(pad("C4", 1, "VBAT_6S"))
c6_vin = xy(pad("C6", 1, "VBAT_6S"))
add_track("VBAT_6S", pcbnew.F_Cu, 0.80, (u3_vin, c4_vin))
add_track("VBAT_6S", pcbnew.F_Cu, 0.80,
          (c4_vin, (0.20, c4_vin[1]), c6_vin))

# Each input capacitor gets its own low-inductance return via into the In1 plane.
for ref, x_offset in (("C4", -0.40), ("C6", 0.40)):
    cap_gnd = xy(pad(ref, 2, "GND"))
    via_pos = (cap_gnd[0] + x_offset, cap_gnd[1])
    add_track("GND", pcbnew.F_Cu, 0.65, (cap_gnd, via_pos))
    add_via("GND", via_pos, size=0.70, drill=0.30)

# Catch-diode anode uses two returns to the plane. U3's exposed PowerPAD already
# contains a checked thermal-via array tied to the same plane.
d1_gnd = xy(pad("D1", 2, "GND"))
for via_pos in ((4.65, -22.30), (4.65, -23.30)):
    add_track("GND", pcbnew.F_Cu, 0.90, (d1_gnd, via_pos))
    add_via("GND", via_pos, size=0.75, drill=0.35)

# --------------------------------------------------------------- output stage
l1_v5 = xy(pad("L1", 2, "V5_BUCK"))
c5_v5 = xy(pad("C5", 1, "V5_BUCK"))
c7_v5 = xy(pad("C7", 1, "V5_BUCK"))
v5_via = add_via("V5_BUCK", (-10.00, -19.70), size=0.80, drill=0.35)
add_track("V5_BUCK", pcbnew.F_Cu, 1.00, (l1_v5, v5_via))
add_track("V5_BUCK", pcbnew.B_Cu, 1.00, (v5_via, c7_v5))
add_track("V5_BUCK", pcbnew.F_Cu, 0.90,
          (l1_v5, (-10.55, -15.00), c5_v5))

for ref, via_pos in (("C5", (-7.10, -13.50)),
                     ("C7", (-6.50, -23.50))):
    cap_gnd = xy(pad(ref, 2, "GND"))
    layer = pcbnew.B_Cu if footprints[ref].GetLayer() == pcbnew.B_Cu else pcbnew.F_Cu
    add_track("GND", layer, 0.80, (cap_gnd, via_pos))
    add_via("GND", via_pos, size=0.75, drill=0.35)

# -------------------------------------------------------------- gyro SPI bus
# U1's alternate PB3/PB4/PB5 SPI1 group and adjacent PB6/PB7 GPIOs face the
# gyro. INT and CS stay on F.Cu; the three bus conductors use short, controlled
# layer changes to avoid crossings around the LGA perimeter.
add_track("GYRO_INT1", pcbnew.F_Cu, 0.18,
          (xy(pad("U1", 58, "GYRO_INT1")), (1.25, 2.20),
           xy(pad("U2", 4, "GYRO_INT1"))))

add_track("GYRO_CS", pcbnew.F_Cu, 0.18,
          (xy(pad("U1", 59, "GYRO_CS")), (0.75, 2.60),
           (-2.60, 2.60),
           (-2.60, -0.90), xy(pad("U2", 12, "GYRO_CS"))))

# SCK uses In2 and MOSI uses B.Cu so their short diagonals can cross in
# projection without crossing electrically. In1 remains the uninterrupted GND
# reference plane.
for net_name, mcu_pin, gyro_pin, source_via, dest_via in (
        ("SPI1_SCK", 55, 13, (3.80, 1.80), (-2.00, 0.10)),
        ("SPI1_MOSI", 57, 14, (2.50, 0.00), (-1.60, 1.00))):
    source = add_via(net_name, source_via, size=0.60, drill=0.30)
    dest = add_via(net_name, dest_via, size=0.60, drill=0.30)
    mcu_xy = xy(pad("U1", mcu_pin, net_name))
    add_track(net_name, pcbnew.F_Cu, 0.18,
              (mcu_xy, (mcu_xy[0], 2.60), source))
    route_layer = pcbnew.In2_Cu if net_name == "SPI1_SCK" else pcbnew.B_Cu
    add_track(net_name, route_layer, 0.18, (source, dest))
    add_track(net_name, pcbnew.F_Cu, 0.18,
              (dest, xy(pad("U2", gyro_pin, net_name))))

# MISO uses a direct B.Cu diagonal for the remaining ordering inversion and
# rejoins F.Cu outside the gyro package.
miso_source = add_via("SPI1_MISO", (3.00, 0.70), size=0.60, drill=0.30)
miso_dest = add_via("SPI1_MISO", (-1.40, 2.00), size=0.60, drill=0.30)
add_track("SPI1_MISO", pcbnew.F_Cu, 0.18,
          (xy(pad("U1", 56, "SPI1_MISO")), (2.25, 2.60), miso_source))
add_track("SPI1_MISO", pcbnew.B_Cu, 0.18,
          (miso_source, miso_dest))
add_track("SPI1_MISO", pcbnew.F_Cu, 0.18,
          (miso_dest, xy(pad("U2", 1, "SPI1_MISO"))))

# ------------------------------------------------------- gyro low-noise rail
# Keep the AP2112 input bypass local, then route its dedicated 3.3 V output
# through the 1 uF output capacitor and 2.2 uF gyro bulk capacitor before it
# reaches the IMU VDD pin. The B-side 100 nF capacitor rejoins through a paired
# power/ground via set immediately below the package.
u5_in_1 = xy(pad("U5", 1, "LOGIC_IN"))
u5_in_3 = xy(pad("U5", 3, "LOGIC_IN"))
c10_in = xy(pad("C10", 1, "LOGIC_IN"))
add_track("LOGIC_IN", pcbnew.F_Cu, 0.30,
          (u5_in_1, (6.80, -1.05), c10_in))
add_track("LOGIC_IN", pcbnew.F_Cu, 0.30,
          (u5_in_3, (6.80, -2.95), c10_in))

u5_out = xy(pad("U5", 5, "V3V3_GYRO"))
c11_v = xy(pad("C11", 1, "V3V3_GYRO"))
c25_v = xy(pad("C25", 1, "V3V3_GYRO"))
u2_vdd = xy(pad("U2", 8, "V3V3_GYRO"))
add_track("V3V3_GYRO", pcbnew.F_Cu, 0.30,
          (u5_out, (2.80, -1.05), (1.80, -2.00),
           (1.80, -3.50), c11_v))
add_track("V3V3_GYRO", pcbnew.F_Cu, 0.30,
          (c11_v, (2.52, -5.30), (-1.20, -5.30), c25_v))
add_track("V3V3_GYRO", pcbnew.F_Cu, 0.30,
          ((2.00, -5.30), (2.00, -2.00), u2_vdd))

c24_v = xy(pad("C24", 1, "V3V3_GYRO"))
c24_via = add_via("V3V3_GYRO", (-0.48, -2.60), size=0.65, drill=0.30)
add_track("V3V3_GYRO", pcbnew.B_Cu, 0.30, (c24_v, c24_via))
add_track("V3V3_GYRO", pcbnew.F_Cu, 0.30,
          (c24_via, (-1.20, -2.60), (-1.20, -5.30)))

# Local regulator and capacitor returns enter the uninterrupted In1 plane.
for ref, via_pos in (("U5", (5.65, -2.00)),
                     ("C10", (8.48, -2.80)),
                     ("C11", (3.48, -5.20)),
                     ("C25", (0.775, -4.60))):
    gnd_pad = xy(pad(ref, 2, "GND"))
    add_track("GND", pcbnew.F_Cu, 0.35, (gnd_pad, via_pos))
    add_via("GND", via_pos, size=0.65, drill=0.30)

c24_gnd = xy(pad("C24", 2, "GND"))
c24_gnd_via = add_via("GND", (0.48, -2.60), size=0.65, drill=0.30)
add_track("GND", pcbnew.B_Cu, 0.35, (c24_gnd, c24_gnd_via))

# -------------------------------------------------------------- 8 MHz HSE
# Each oscillator pin escapes perpendicular to the MCU edge before changing
# layer. The crystal and its C0G load capacitors form compact B.Cu trees; no
# unrelated trace enters the clock-loop area.
hse_in_mcu = xy(pad("U1", 5, "HSE_IN"))
hse_out_mcu = xy(pad("U1", 6, "HSE_OUT"))
hse_in_via = add_via("HSE_IN", (-5.20, 5.80), size=0.60, drill=0.30)
hse_out_via = add_via("HSE_OUT", (-9.50, 7.80), size=0.60, drill=0.30)
add_track("HSE_IN", pcbnew.F_Cu, 0.18,
          (hse_in_mcu, (-5.20, 7.75), hse_in_via))
add_track("HSE_OUT", pcbnew.F_Cu, 0.18,
          (hse_out_mcu, (-5.20, 8.25), hse_out_via))

y1_in = xy(pad("Y1", 1, "HSE_IN"))
y1_out = xy(pad("Y1", 2, "HSE_OUT"))
c21_in = xy(pad("C21", 1, "HSE_IN"))
c22_out = xy(pad("C22", 1, "HSE_OUT"))
r7_in = xy(pad("R7", 1, "HSE_IN"))
r7_out = xy(pad("R7", 2, "HSE_OUT"))
add_track("HSE_IN", pcbnew.B_Cu, 0.18,
          (hse_in_via, (-4.80, 5.80), (-4.80, 8.85), y1_in))
add_track("HSE_IN", pcbnew.B_Cu, 0.18, (y1_in, c21_in, r7_in))
add_track("HSE_OUT", pcbnew.B_Cu, 0.18, (hse_out_via, y1_out))
add_track("HSE_OUT", pcbnew.B_Cu, 0.18, (y1_out, c22_out))
add_track("HSE_OUT", pcbnew.B_Cu, 0.18, (y1_out, r7_out))

for ref, via_pos in (("C21", (-2.00, 10.50)),
                     ("C22", (-9.20, 12.50))):
    clock_gnd = xy(pad(ref, 2, "GND"))
    add_track("GND", pcbnew.B_Cu, 0.25, (clock_gnd, via_pos))
    add_via("GND", via_pos, size=0.65, drill=0.30)

# STM32 internal-regulator capacitors. VCAP is neither 3V3 nor a routable
# power rail: each pin gets one dedicated low-ESR capacitor and a short ground
# return. Both remain entirely on F.Cu.
vcap1_mcu = xy(pad("U1", 31, "VCAP1"))
vcap1_cap = xy(pad("C19", 1, "VCAP1"))
add_track("VCAP1", pcbnew.F_Cu, 0.30, (vcap1_mcu, vcap1_cap))

c19_ground = xy(pad("C19", 2, "GND"))
c19_ground_via = (5.25, 19.75)
add_track("GND", pcbnew.F_Cu, 0.35,
          (c19_ground, c19_ground_via))
add_via("GND", c19_ground_via, size=0.65, drill=0.30)

vcap2_mcu = xy(pad("U1", 47, "VCAP2"))
vcap2_cap = xy(pad("C20", 1, "VCAP2"))
add_track("VCAP2", pcbnew.F_Cu, 0.30, (vcap2_mcu, vcap2_cap))
c20_ground = xy(pad("C20", 2, "GND"))
c20_ground_via = (11.175, 5.10)
add_track("GND", pcbnew.F_Cu, 0.35,
          (c20_ground, c20_ground_via))
add_via("GND", c20_ground_via, size=0.65, drill=0.30)

# ------------------------------------------------------- MCU logic/analog rail
# The main AP2112 output enters the In2 3V3 plane beside its output capacitor.
# Its ground return goes directly to In1 rather than sharing the input path.
u4_v3 = xy(pad("U4", 5, "V3V3"))
c9_v3 = xy(pad("C9", 1, "V3V3"))
v3_source_via = (10.40, -17.05)
add_track("V3V3", pcbnew.B_Cu, 0.50,
          (u4_v3, v3_source_via, c9_v3))
add_via("V3V3", v3_source_via, size=0.75, drill=0.35)
u4_ground = xy(pad("U4", 2, "GND"))
u4_ground_via = (10.00, -20.00)
add_track("GND", pcbnew.B_Cu, 0.45,
          (u4_ground, (5.50, -18.00), (5.50, -20.00), u4_ground_via))
add_via("GND", u4_ground_via, size=0.65, drill=0.30)
c9_ground = xy(pad("C9", 2, "GND"))
c9_ground_via = (12.60, -18.00)
add_track("GND", pcbnew.B_Cu, 0.45, (c9_ground, c9_ground_via))
add_via("GND", c9_ground_via, size=0.65, drill=0.30)

# VDDA is a deliberately small F.Cu island. The ferrite input reaches the 3V3
# plane through one via; no digital return current is allowed through V3V3_A.
fb_v3 = xy(pad("FB1", 1, "V3V3"))
fb_v3a = xy(pad("FB1", 2, "V3V3_A"))
vdda_mcu = xy(pad("U1", 13, "V3V3_A"))
c12_vdda = xy(pad("C12", 1, "V3V3_A"))
c13_vdda = xy(pad("C13", 1, "V3V3_A"))
vdda_node = (-6.65, 11.24)
add_track("V3V3_A", pcbnew.F_Cu, 0.30,
          (vdda_mcu, (-5.00, 11.75), fb_v3a))
add_track("V3V3_A", pcbnew.F_Cu, 0.30,
          (fb_v3a, vdda_node, c12_vdda))
add_track("V3V3_A", pcbnew.F_Cu, 0.30,
          (vdda_node, (-6.65, 12.00), c13_vdda))
fb_v3_via = (-5.80, 13.05)
add_track("V3V3", pcbnew.F_Cu, 0.35, (fb_v3, fb_v3_via))
add_via("V3V3", fb_v3_via, size=0.65, drill=0.30)
for ref, via_pos in (("C12", (-8.55, 10.70)),
                     ("C13", (-8.55, 12.00))):
    analog_ground = xy(pad(ref, 2, "GND"))
    add_track("GND", pcbnew.F_Cu, 0.35, (analog_ground, via_pos))
    add_via("GND", via_pos, size=0.65, drill=0.30)

# Fill after all vias exist so thermal/clearance geometry is deterministic.
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(OUTPUT), board)

print(f"wrote {OUTPUT}")
print(f"tracks/vias: {len(board.GetTracks())}; zones: {len(board.Zones())}")
print("critical power, gyro, HSE, VCAP and VDDA copper; remaining routing is open")
