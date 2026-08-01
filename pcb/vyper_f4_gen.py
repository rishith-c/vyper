"""Emit vyper_f4.kicad_pcb directly as KiCad 9 s-expressions.

Why not the pcbnew Python API: on macOS, BOARD.Save() from a headless script
dies in wxWidgets (fatal 'create wxApp' assert, then SIGSEGV even with a
wx.App constructed). Emitting the file format directly is deterministic, and
`kicad-cli pcb render` doubles as the format validator -- if KiCad's own
parser accepts and renders the file, it is a real board file.

The board is PLACEMENT-COMPLETE, not routed: outline, mounting holes, every
courtyard, anchor pads, solder-pad groups, silk. Routing belongs in the KiCad
GUI or an AI router (Quilter / DeepPCB -- see docs/PCB_DESIGN.md). What is
locked here is what silently kills FC spins: dimensions, holes, clearances --
all checked by test_vyper_f4.py against the same layout module.

Run:  python3 vyper_f4_gen.py        (any python3; stdlib only)
"""

import math
import uuid
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
import vyper_f4_layout as L

OUT = Path(__file__).parent / "vyper_f4.kicad_pcb"
W2, H2, R = L.BOARD_W / 2, L.BOARD_H / 2, L.CORNER_R


def uid():
    return f'(uuid "{uuid.uuid4()}")'


def K(y):
    """Layout is Y-up; KiCad files are Y-down."""
    return -y


HEADER = """(kicad_pcb
\t(version 20241229)
\t(generator "vyper_f4_gen")
\t(generator_version "9.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(title_block
\t\t(title "VYPER-F4 flight controller")
\t\t(rev "A")
\t\t(comment 1 "36x36, 30.5x30.5 M3, placement-complete / unrouted")
\t)
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(2 "B.Cu" signal)
\t\t(9 "F.Adhes" user "F.Adhesive")
\t\t(11 "B.Adhes" user "B.Adhesive")
\t\t(13 "F.Paste" user)
\t\t(15 "B.Paste" user)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(17 "Dwgs.User" user "User.Drawings")
\t\t(19 "Cmts.User" user "User.Comments")
\t\t(21 "Eco1.User" user "User.Eco1")
\t\t(23 "Eco2.User" user "User.Eco2")
\t\t(25 "Edge.Cuts" user)
\t\t(27 "Margin" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t)
\t(net 0 "")
"""


def gr_line(x1, y1, x2, y2, layer, w=0.15):
    return (f'\t(gr_line (start {x1:.3f} {K(y1):.3f}) (end {x2:.3f} {K(y2):.3f}) '
            f'(stroke (width {w}) (type solid)) (layer "{layer}") {uid()})\n')


def gr_arc(cx, cy, a0, a1, r, layer, w=0.15):
    """Arc by centre + CCW angle range in the LAYOUT frame (Y-up). Emitted as
    start/mid/end points, so the Y flip cannot corrupt the sweep direction."""
    am = (a0 + a1) / 2
    pts = []
    for a in (a0, am, a1):
        pts.append((cx + r * math.cos(math.radians(a)),
                    cy + r * math.sin(math.radians(a))))
    (sx, sy), (mx, my), (ex, ey) = pts
    return (f'\t(gr_arc (start {sx:.3f} {K(sy):.3f}) (mid {mx:.3f} {K(my):.3f}) '
            f'(end {ex:.3f} {K(ey):.3f}) (stroke (width {w}) (type solid)) '
            f'(layer "{layer}") {uid()})\n')


def gr_rect(cx, cy, w, h, layer, sw=0.12):
    x1, y1 = cx - w / 2, cy + h / 2
    x2, y2 = cx + w / 2, cy - h / 2
    return (f'\t(gr_rect (start {x1:.3f} {K(y1):.3f}) (end {x2:.3f} {K(y2):.3f}) '
            f'(stroke (width {sw}) (type solid)) (fill no) (layer "{layer}") {uid()})\n')


def gr_text(txt, x, y, layer, size=1.0, mirror=False):
    j = " (justify mirror)" if mirror else ""
    return (f'\t(gr_text "{txt}" (at {x:.3f} {K(y):.3f} 0) (layer "{layer}") {uid()}\n'
            f'\t\t(effects (font (size {size} {size}) (thickness {size * 0.15:.3f})){j})\n\t)\n')


def footprint_open(name, x, y, side, ref):
    layer = "B.Cu" if side == "B" else "F.Cu"
    silk = "B.SilkS" if side == "B" else "F.SilkS"
    mir = " (justify mirror)" if side == "B" else ""
    return (f'\t(footprint "VYPER:{name}" (layer "{layer}") {uid()}\n'
            f'\t\t(at {x:.3f} {K(y):.3f})\n'
            f'\t\t(attr exclude_from_pos_files)\n'
            f'\t\t(property "Reference" "{ref}" (at 0 -2.4 0) (layer "{silk}") {uid()}\n'
            f'\t\t\t(effects (font (size 0.8 0.8) (thickness 0.12)){mir})\n\t\t)\n'
            f'\t\t(property "Value" "{name}" (at 0 2.4 0) (layer "{silk}") {uid()}\n'
            f'\t\t\t(effects (font (size 0.5 0.5) (thickness 0.08)) (hide yes))\n\t\t)\n')


def smd_pad(num, x, y, w, h, side):
    layers = '"B.Cu" "B.Paste" "B.Mask"' if side == "B" else '"F.Cu" "F.Paste" "F.Mask"'
    return (f'\t\t(pad "{num}" smd roundrect (at {x:.3f} {y:.3f}) '
            f'(size {w} {h}) (layers {layers}) (roundrect_rratio 0.25) {uid()})\n')


def build():
    out = [HEADER]

    # ---- outline: 4 lines + 4 corner arcs -----------------------------------
    E = "Edge.Cuts"
    out += [
        gr_line(-W2 + R, H2, W2 - R, H2, E),
        gr_line(-W2 + R, -H2, W2 - R, -H2, E),
        gr_line(-W2, -H2 + R, -W2, H2 - R, E),
        gr_line(W2, -H2 + R, W2, H2 - R, E),
        gr_arc(W2 - R, H2 - R, 0, 90, R, E),
        gr_arc(-W2 + R, H2 - R, 90, 180, R, E),
        gr_arc(-W2 + R, -H2 + R, 180, 270, R, E),
        gr_arc(W2 - R, -H2 + R, 270, 360, R, E),
    ]

    # ---- mounting holes + grommet keepouts (dashed, Dwgs.User) --------------
    for i, (hx, hy) in enumerate(L.HOLES, 1):
        out.append(footprint_open("MTG_M3_grommet", hx, hy, "F", f"H{i}"))
        out.append(f'\t\t(pad "" np_thru_hole circle (at 0 0) '
                   f'(size {L.HOLE_D} {L.HOLE_D}) (drill {L.HOLE_D}) '
                   f'(layers "*.Cu" "*.Mask") {uid()})\n')
        out.append("\t)\n")
        out.append(f'\t(gr_circle (center {hx:.3f} {K(hy):.3f}) '
                   f'(end {hx + L.GROMMET_KEEPOUT_D / 2:.3f} {K(hy):.3f}) '
                   f'(stroke (width 0.08) (type dash)) (fill no) '
                   f'(layer "Dwgs.User") {uid()})\n')

    # ---- parts: courtyard + silk outline + anchor pad ------------------------
    for name, spec in L.PARTS.items():
        x, y = spec["pos"]
        w, h = spec["courtyard"]
        side = spec["side"]
        ref = name.split("_")[0]
        crt = "B.CrtYd" if side == "B" else "F.CrtYd"
        silk = "B.SilkS" if side == "B" else "F.SilkS"
        out.append(gr_rect(x, y, w, h, crt, 0.05))
        out.append(gr_rect(x, y, w, h, silk, 0.12))
        out.append(footprint_open(name, x, y, side, ref))
        out.append(smd_pad("1", 0, 0, min(w, 2.0), min(h, 2.0), side))
        out.append("\t)\n")

    # ---- solder pad groups ----------------------------------------------------
    for pads in L.PAD_GROUPS.values():
        for x, y, label in pads:
            out.append(footprint_open(f"PAD_{label}", x, y, "F", label))
            out.append(smd_pad("1", 0, 0, 1.6, 1.6, "F"))
            out.append("\t)\n")

    # ---- gyro forward-axis marker + titles -----------------------------------
    gx, gy = L.PARTS["U2_gyro_ICM42688P"]["pos"]
    out.append(gr_line(gx, gy + 3.4, gx, gy + 5.2, "F.SilkS", 0.2))
    out.append(gr_text("FWD", gx + 2.8, gy + 4.3, "F.SilkS", 0.7))
    out.append(gr_text("VYPER-F4", 0, 16.6, "F.SilkS", 1.1))
    out.append(gr_text("36x36 / 30.5", 0, -16.9, "F.SilkS", 0.8))

    out.append(")\n")
    OUT.write_text("".join(out))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
