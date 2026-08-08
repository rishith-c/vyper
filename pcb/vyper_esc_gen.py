"""Emit the VYPER-55A EVT mechanical floorplan as a KiCad 9 board.

This file intentionally contains no electrical nets or copper.  It exists to
make the tested 40-part floorplan reviewable in KiCad while the schematic is
being completed.  Do not order it; ESC_ARCHITECTURE.md defines the gates.
"""

import math
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import vyper_esc_layout as L

OUT = Path(__file__).parent / "vyper_55a_esc.kicad_pcb"
W2, H2, R = L.BOARD_W / 2, L.BOARD_H / 2, L.CORNER_R


def uid():
    return f'(uuid "{uuid.uuid4()}")'


def ky(y):
    return -y


HEADER = """(kicad_pcb
\t(version 20241229)
\t(generator "vyper_esc_gen")
\t(generator_version "9.0")
\t(general (thickness 1.6) (legacy_teardrops no))
\t(paper "A4")
\t(title_block
\t\t(title "VYPER-55A 4-in-1 ESC EVT floorplan")
\t\t(rev "A0-MECH")
\t\t(comment 1 "NOT ORDERABLE: no schematic, nets or copper")
\t)
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(4 "In1.Cu" power)
\t\t(6 "In2.Cu" power)
\t\t(8 "In3.Cu" power)
\t\t(10 "In4.Cu" power)
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
\t\t(25 "Edge.Cuts" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t)
\t(setup (pad_to_mask_clearance 0))
\t(net 0 "")
"""


def gr_line(x1, y1, x2, y2, layer="Edge.Cuts", width=0.15):
    return (f'\t(gr_line (start {x1:.3f} {ky(y1):.3f}) '
            f'(end {x2:.3f} {ky(y2):.3f}) '
            f'(stroke (width {width}) (type solid)) '
            f'(layer "{layer}") {uid()})\n')


def gr_arc(cx, cy, a0, a1, radius):
    points = []
    for angle in (a0, (a0 + a1) / 2, a1):
        points.append((cx + radius * math.cos(math.radians(angle)),
                       cy + radius * math.sin(math.radians(angle))))
    (sx, sy), (mx, my), (ex, ey) = points
    return (f'\t(gr_arc (start {sx:.3f} {ky(sy):.3f}) '
            f'(mid {mx:.3f} {ky(my):.3f}) (end {ex:.3f} {ky(ey):.3f}) '
            f'(stroke (width 0.15) (type solid)) '
            f'(layer "Edge.Cuts") {uid()})\n')


def gr_rect(x, y, w, h, layer):
    return (f'\t(gr_rect (start {x-w/2:.3f} {ky(y+h/2):.3f}) '
            f'(end {x+w/2:.3f} {ky(y-h/2):.3f}) '
            f'(stroke (width 0.05) (type solid)) (fill no) '
            f'(layer "{layer}") {uid()})\n')


def footprint(name, ref, x, y, side, w, h, pad_w=1.2, pad_h=1.2):
    copper = "B.Cu" if side == "B" else "F.Cu"
    silk = "B.SilkS" if side == "B" else "F.SilkS"
    courtyard = "B.CrtYd" if side == "B" else "F.CrtYd"
    layers = '"B.Cu" "B.Paste" "B.Mask"' if side == "B" else '"F.Cu" "F.Paste" "F.Mask"'
    mirror = " (justify mirror)" if side == "B" else ""
    out = [gr_rect(x, y, w, h, courtyard)]
    out.append(f'\t(footprint "VYPER_EVT:{name}" (layer "{copper}") {uid()}\n')
    out.append(f'\t\t(at {x:.3f} {ky(y):.3f})\n')
    out.append('\t\t(attr exclude_from_bom exclude_from_pos_files)\n')
    out.append(f'\t\t(property "Reference" "{ref}" (at 0 0 0) '
               f'(layer "{silk}") {uid()}\n')
    out.append(f'\t\t\t(effects (font (size 0.55 0.55) (thickness 0.08)){mirror})\n\t\t)\n')
    out.append(f'\t\t(property "Value" "{name}" (at 0 1.2 0) '
               f'(layer "{silk}") hide {uid()}\n')
    out.append('\t\t\t(effects (font (size 0.5 0.5) (thickness 0.08)))\n\t\t)\n')
    out.append(f'\t\t(fp_rect (start {-w/2:.3f} {-h/2:.3f}) '
               f'(end {w/2:.3f} {h/2:.3f}) '
               f'(stroke (width 0.1) (type solid)) (fill no) '
               f'(layer "{silk}") {uid()})\n')
    out.append(f'\t\t(pad "1" smd roundrect (at 0 0) '
               f'(size {pad_w:.2f} {pad_h:.2f}) (layers {layers}) '
               f'(roundrect_rratio 0.2) {uid()})\n\t)\n')
    return "".join(out)


def plated_pad(name, ref, x, y, w, h):
    return (f'\t(footprint "VYPER_EVT:{name}" (layer "F.Cu") {uid()}\n'
            f'\t\t(at {x:.3f} {ky(y):.3f})\n'
            f'\t\t(attr exclude_from_bom exclude_from_pos_files)\n'
            f'\t\t(property "Reference" "{ref}" (at 0 0 0) '
            f'(layer "F.SilkS") hide {uid()} '
            f'(effects (font (size 0.5 0.5) (thickness 0.08))))\n'
            f'\t\t(pad "1" thru_hole oval (at 0 0) (size {w:.2f} {h:.2f}) '
            f'(drill oval {max(0.9, w-0.7):.2f} {max(0.9, h-0.7):.2f}) '
            f'(layers "*.Cu" "*.Mask") {uid()})\n\t)\n')


def build():
    out = [HEADER]
    out += [
        gr_line(-W2 + R, H2, W2 - R, H2),
        gr_line(-W2 + R, -H2, W2 - R, -H2),
        gr_line(-W2, -H2 + R, -W2, H2 - R),
        gr_line(W2, -H2 + R, W2, H2 - R),
        gr_arc(W2 - R, H2 - R, 0, 90, R),
        gr_arc(-W2 + R, H2 - R, 90, 180, R),
        gr_arc(-W2 + R, -H2 + R, 180, 270, R),
        gr_arc(W2 - R, -H2 + R, 270, 360, R),
    ]

    for index, (x, y) in enumerate(L.HOLES, 1):
        out.append(f'\t(footprint "VYPER_EVT:M3_CLEAR" (layer "F.Cu") {uid()}\n')
        out.append(f'\t\t(at {x:.3f} {ky(y):.3f})\n')
        out.append(f'\t\t(property "Reference" "H{index}" (at 0 0 0) '
                   f'(layer "F.SilkS") hide {uid()} '
                   f'(effects (font (size 0.5 0.5) (thickness 0.08))))\n')
        out.append(f'\t\t(pad "" np_thru_hole circle (at 0 0) '
                   f'(size {L.HOLE_D} {L.HOLE_D}) (drill {L.HOLE_D}) '
                   f'(layers "*.Cu" "*.Mask") {uid()})\n\t)\n')

    counters = {"Q": 0, "U": 0, "RN": 0, "TH": 0, "RSH": 0, "L": 0}
    for name, spec in L.PARTS.items():
        prefix = "Q" if name.startswith("Q_") else (
            "RN" if name.startswith("RN_") else (
                "TH" if name.startswith("TH_") else (
                    "RSH" if name.startswith("RSH_") else (
                        "L" if name.startswith("L_") else "U"))))
        counters[prefix] += 1
        ref = f"{prefix}{counters[prefix]}"
        x, y = spec["pos"]
        w, h = spec["courtyard"]
        out.append(footprint(name, ref, x, y, spec["side"], w, h))

    for channel, pads in L.MOTOR_PADS.items():
        pad_size = (L.MOTOR_PAD_SIZE[1], L.MOTOR_PAD_SIZE[0]) \
            if channel in ("M2", "M4") else L.MOTOR_PAD_SIZE
        for phase, (x, y) in zip("ABC", pads):
            out.append(plated_pad(f"{channel}_{phase}", f"{channel}{phase}",
                                  x, y, *pad_size))
    for label, (x, y) in L.BATTERY_PADS.items():
        out.append(plated_pad(label, label, x, y, *L.BATTERY_PAD_SIZE))

    out.append('\t(gr_text "VYPER-55A EVT / NOT FOR FAB" (at 0 0 0) '
               f'(layer "Dwgs.User") {uid()} '
               '(effects (font (size 1.0 1.0) (thickness 0.15))))\n')
    out.append(")\n")
    OUT.write_text("".join(out))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
