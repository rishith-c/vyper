"""Build a true-footprint, true-net KiCad ESC review board.

Run with KiCad's bundled Python (pcbnew is not part of normal CPython):

  /Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
      pcb/vyper_esc_unrouted_gen.py

Major power/control parts are placed at their verified in-board floorplan
coordinates.  Remaining passives are intentionally staged to the right of the
outline.  The result exposes real ratsnest/unconnected counts and is therefore
strictly more honest than the mechanical one-pad preview, but it is NOT a fab
or routing release.
"""

import re
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NETLIST = HERE / "vyper_55a_esc.net"
SOURCE_BOARD = HERE / "vyper_55a_esc.kicad_pcb"
OUT = HERE / "vyper_55a_esc_unrouted.kicad_pcb"
FP_ROOT = Path("/Applications/KiCad.app/Contents/SharedSupport/footprints")
FP_LOADER = None

sys.path.insert(0, str(HERE))
import vyper_esc_layout as L  # noqa: E402


def child_blocks(source, parent_token, child_token):
    start = source.index(parent_token)
    blocks, depth, child_start = [], 0, None
    i = start
    while i < len(source):
        if source[i] == "(":
            if depth == 1 and source.startswith(child_token, i):
                child_start = i
            depth += 1
        elif source[i] == ")":
            depth -= 1
            if child_start is not None and depth == 1:
                blocks.append(source[child_start:i + 1])
                child_start = None
            if depth == 0:
                break
        i += 1
    return blocks


def parse_netlist():
    text = NETLIST.read_text()
    components = {}
    for block in child_blocks(text, "(components", "(comp"):
        def field(name):
            match = re.search(rf'\({name} "([^"]*)"\)', block)
            return match.group(1) if match else ""
        ref = field("ref")
        components[ref] = {"value": field("value"), "footprint": field("footprint")}

    pin_nets = {}
    net_names = []
    for block in child_blocks(text, "(nets", "(net"):
        match = re.search(r'\(name "([^"]+)"\)', block)
        if not match:
            continue
        name = match.group(1)
        net_names.append(name)
        for ref, pin in re.findall(
                r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
            if (ref, pin) in pin_nets:
                raise RuntimeError(f"duplicate net owner for {ref}.{pin}")
            pin_nets[(ref, pin)] = name
    return components, pin_nets, net_names


def smd_layers():
    layers = pcbnew.LSET()
    for layer in (pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_Paste):
        layers.AddLayer(layer)
    return layers


def wire_smd_layers():
    layers = pcbnew.LSET()
    for layer in (pcbnew.F_Cu, pcbnew.F_Mask):
        layers.AddLayer(layer)
    return layers


def pth_layers():
    layers = pcbnew.LSET.AllCuMask()
    layers.AddLayer(pcbnew.F_Mask)
    layers.AddLayer(pcbnew.B_Mask)
    return layers


def base_custom(name):
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPIDAsString(f"VYPER:{name}")
    return fp


def add_smd_pad(fp, number, x, y, sx, sy, shape=pcbnew.PAD_SHAPE_ROUNDRECT):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(number))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(shape)
    pad.SetSize(pcbnew.VECTOR2I_MM(sx, sy))
    pad.SetFPRelativePosition(pcbnew.VECTOR2I_MM(x, y))
    pad.SetLayerSet(smd_layers())
    if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
        pad.SetRoundRectRadiusRatio(0.2)
    fp.Add(pad)
    return pad


def add_wire_smd_pad(fp, number, x, y, sx, sy):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(number))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
    pad.SetRoundRectRadiusRatio(0.15)
    pad.SetSize(pcbnew.VECTOR2I_MM(sx, sy))
    pad.SetFPRelativePosition(pcbnew.VECTOR2I_MM(x, y))
    pad.SetLayerSet(wire_smd_layers())
    fp.Add(pad)
    return pad


def add_pth_pad(fp, number, x, y, sx, sy, dx, dy):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(number))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetShape(pcbnew.PAD_SHAPE_OVAL)
    pad.SetSize(pcbnew.VECTOR2I_MM(sx, sy))
    pad.SetDrillSize(pcbnew.VECTOR2I_MM(dx, dy))
    pad.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)
    pad.SetFPRelativePosition(pcbnew.VECTOR2I_MM(x, y))
    pad.SetLayerSet(pth_layers())
    fp.Add(pad)
    return pad


def custom_footprint(name):
    if name == "TI_RTA0040_WQFN40_6x6_P0.5_EP":
        fp = base_custom(name)
        # TI RTA0040A land pattern: 0.25 x 0.60 mm perimeter lands on 0.5 mm
        # pitch and a 4.6 mm exposed pad (TI drawing 4214989/B).
        stations = [2.25 - 0.5 * i for i in range(10)]
        for i, y in enumerate(stations, 1):
            add_smd_pad(fp, i, -2.9, y, 0.6, 0.25)
        for i, x in enumerate([-2.25 + 0.5 * i for i in range(10)], 11):
            add_smd_pad(fp, i, x, -2.9, 0.25, 0.6)
        for i, y in enumerate([-2.25 + 0.5 * i for i in range(10)], 21):
            add_smd_pad(fp, i, 2.9, y, 0.6, 0.25)
        for i, x in enumerate([2.25 - 0.5 * i for i in range(10)], 31):
            add_smd_pad(fp, i, x, 2.9, 0.25, 0.6)
        add_smd_pad(fp, 41, 0, 0, 4.6, 4.6, pcbnew.PAD_SHAPE_RECT)
        return fp
    if name == "MOTOR_EDGE_PADS_3X":
        fp = base_custom(name)
        for number, y in enumerate(L.MOTOR_PAD_STATIONS, 1):
            add_pth_pad(fp, number, 0, y, *L.MOTOR_PAD_SIZE,
                        *L.MOTOR_PAD_DRILL)
        return fp
    if name == "BATTERY_PIGTAIL_2X":
        fp = base_custom(name)
        for number, (x, y) in enumerate(L.BATTERY_PADS.values(), 1):
            add_wire_smd_pad(fp, number, x, y, *L.BATTERY_PAD_SIZE)
        return fp
    if name == "FC_HARNESS_2X4_P1.27_SOLDER":
        fp = base_custom(name)
        for row, y in enumerate((-0.85, 0.85)):
            for col, x in enumerate((-1.905, -0.635, 0.635, 1.905)):
                add_smd_pad(fp, row * 4 + col + 1, x, y, 0.8, 1.3)
        return fp
    if name == "SWD_2X2_P1.27_TESTPADS":
        fp = base_custom(name)
        for number, (x, y) in enumerate(
                ((-0.635, -0.635), (0.635, -0.635),
                 (-0.635, 0.635), (0.635, 0.635)), 1):
            add_smd_pad(fp, number, x, y, 0.8, 0.8)
        return fp
    raise KeyError(f"no custom footprint generator for VYPER:{name}")


def load_footprint(identifier):
    if identifier.startswith("VYPER:"):
        return custom_footprint(identifier.split(":", 1)[1])
    if ":" not in identifier:
        raise ValueError(f"invalid footprint identifier: {identifier}")
    library, name = identifier.split(":", 1)
    fp = FP_LOADER.FootprintLoad(str(FP_ROOT / f"{library}.pretty"), name)
    if fp is None:
        raise FileNotFoundError(f"footprint not found: {identifier}")
    return fp


def xy_layout(point):
    """Layout uses +Y up; KiCad uses +Y down."""
    return point[0], -point[1]


def add_silk_text(board, value, x, y, side="F", size=0.70, rotation=0.0):
    size = max(size, 0.80)  # PCBWay-readable text height
    item = pcbnew.PCB_TEXT(board)
    item.SetText(value)
    item.SetLayer(pcbnew.B_SilkS if side == "B" else pcbnew.F_SilkS)
    item.SetMirrored(side == "B")
    item.SetTextPos(pcbnew.VECTOR2I_MM(x, -y))
    item.SetTextAngle(pcbnew.EDA_ANGLE(rotation, pcbnew.DEGREES_T))
    item.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
    item.SetTextThickness(pcbnew.FromMM(max(0.10, size * 0.15)))
    item.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    board.Add(item)


def placed_major_components():
    result = {}
    for channel_index, channel in enumerate(L.CHANNELS, 1):
        for phase_index, phase in enumerate("ABC", 1):
            for role, ref_offset in (("HS", -1), ("LS", 0)):
                spec = L.PARTS[f"Q_{channel}_{phase}_{role}"]
                result[f"Q{channel_index}{phase_index * 2 + ref_offset}"] = (
                    *xy_layout(spec["pos"]), spec["side"], 0)
        result[f"U{channel_index}2"] = (
            *xy_layout(L.PARTS[f"U_DRV_{channel}"]["pos"]), "B", 0)
        result[f"U{channel_index}1"] = (
            *xy_layout(L.PARTS[f"U_MCU_{channel}"]["pos"]), "B", 0)
        result[f"RSH{channel_index}"] = (
            *xy_layout(L.PARTS[f"RSH_{channel}"]["pos"]), "B", 0)
        result[f"TH{channel_index}"] = (
            *xy_layout(L.PARTS[f"TH_{channel}"]["pos"]), "B", 0)
        motor = L.MOTOR_CONNECTORS[channel]
        result[f"JM{channel_index}"] = (
            *xy_layout(motor["pos"]), motor["side"], motor["rotation"])
        swd = L.PARTS[f"J_SWD_{channel}"]
        result[f"J{channel_index + 1}"] = (
            *xy_layout(swd["pos"]), swd["side"], 0)

    for ref, key in (("U1", "U_BUCK"), ("L1", "L_BUCK"),
                     ("U2", "U_ISUM"), ("J1", "J_HARNESS")):
        result[ref] = (*xy_layout(L.PARTS[key]["pos"]), L.PARTS[key]["side"], 0)
    result["JBAT"] = (0.0, 0.0, "F", 0)
    return result


def footprint_courtyard_width(fp):
    box = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    width = pcbnew.ToMM(box.GetWidth())
    if width <= 0:
        width = pcbnew.ToMM(fp.GetBoundingBox().GetWidth())
    return width


def pack_support_row(result, loaded, refs, y, span=26.5, gap=0.25,
                     center_x=0.0):
    """Centre a true-footprint row in the quiet B-side control corridor."""
    widths = [footprint_courtyard_width(loaded[ref]) for ref in refs]
    total = sum(widths) + gap * (len(refs) - 1)
    if total > span:
        raise RuntimeError(f"support row {refs} needs {total:.2f} mm > {span:.2f}")
    cursor = center_x - total / 2
    for ref, width in zip(refs, widths):
        x = cursor + width / 2
        result[ref] = (*xy_layout((x, y)), "B", 0)
        cursor += width + gap


def placed_channel_support(loaded):
    """Place all 31 support parts for each inverter, using real courtyards."""
    result = {}
    for index, channel in enumerate(L.CHANNELS, 1):
        cy = L.CHANNEL_Y[channel]
        rows = (
            [f"FB{index}", f"C{index}01", f"C{index}02", f"C{index}03",
             f"R{index}01", f"R{index}02", f"R{index}A1", f"R{index}A2",
             f"C{index}A1", f"R{index}B1"],
            [f"R{index}B2", f"C{index}B1", f"R{index}C1", f"R{index}C2",
             f"C{index}C1", f"R{index}V1", f"R{index}V2", f"C{index}V1",
             f"R{index}T1", f"C{index}T1"],
            [f"C{index}D1", f"C{index}D2", f"C{index}D4", f"C{index}D5",
             f"C{index}D6", f"R{index}D1", f"R{index}D2", f"R{index}D3",
             f"R{index}D4", f"DT{index}"],
        )
        if channel == "M2":
            offsets = (-4.6, 4.8, -6.3)
        elif channel == "M3":
            offsets = (-4.6, 4.8, 6.3)
        elif channel == "M4":
            offsets = (-4.6, -6.2, 6.3)
        else:
            offsets = (-4.6, 4.8, 6.3)
        for row_index, (refs, offset) in enumerate(zip(rows, offsets)):
            center_x = (L.MOTOR_SIDE[channel] * 1.6 if row_index == 0
                        else 1.8 if row_index == 1 else 0.0)
            pack_support_row(result, loaded, refs, cy + offset,
                             center_x=center_x)

        # The 1210 bus capacitor gets its own side pocket opposite the motor
        # pads. This keeps it close to the bridge without blocking phase wires.
        cap_x = -L.MOTOR_SIDE[channel] * 14.0
        result[f"C{index}D3"] = (*xy_layout((cap_x, cy - 3.7)), "B", 0)
    return result


def placed_shared_support(loaded):
    """Place the regulator and total-current support in reserved B-side bays."""
    result = {
        # F.Cu centre service window around, but not touching, JBAT. The heat
        # spreader therefore needs a matching electrically isolated relief.
        "D1": (*xy_layout((-15.0, 1.5)), "B", 0),
        "C2": (*xy_layout((-11.5, -1.5)), "F", 0),
        "C3": (*xy_layout((-11.5, 1.5)), "F", 0),
        "R1": (*xy_layout((-8.8, -1.5)), "F", 0),
        "R2": (*xy_layout((-8.8, 0.0)), "F", 0),
        "R3": (*xy_layout((-8.8, 1.5)), "F", 0),
        "C1": (*xy_layout((9.0, 0.0)), "F", 0),
        "C4": (*xy_layout((11.0, -1.5)), "F", 0),
        "C5": (*xy_layout((11.0, 1.5)), "F", 0),
    }
    pack_support_row(result, loaded,
                     ["RT1", "RS1", "RS2", "RS3", "RS4"],
                     32.5, span=12.5, gap=0.35, center_x=3.0)
    pack_support_row(result, loaded, ["RS5", "RS6", "CS1", "CS2"],
                     34.3, span=11.0, gap=0.35, center_x=3.0)
    return result


def main():
    global FP_LOADER
    components, pin_nets, net_names = parse_netlist()
    FP_LOADER = pcbnew.PCB_IO_KICAD_SEXPR()
    # KiCad 9's legacy SWIG binding invalidates its footprint-loader typemap
    # after BOARD.Remove() takes ownership of removed objects.  Load every
    # replacement footprint first, then mutate the source board.
    loaded_footprints = {
        ref: load_footprint(spec["footprint"])
        for ref, spec in components.items()
    }
    board = pcbnew.LoadBoard(str(SOURCE_BOARD))
    if board is None:
        raise RuntimeError(f"failed to load {SOURCE_BOARD}")

    # Preserve the outline and exact NPTH holes, not the construction
    # rectangles/text from the abstract floorplan preview.
    for layer in (pcbnew.F_SilkS, pcbnew.B_SilkS,
                  pcbnew.F_CrtYd, pcbnew.B_CrtYd,
                  pcbnew.Dwgs_User, pcbnew.Cmts_User):
        board.RemoveAllItemsOnLayer(layer)
    for fp in list(board.GetFootprints()):
        if fp.GetReference().startswith("H"):
            fp.Reference().SetVisible(False)
            fp.Value().SetVisible(False)
        else:
            board.Remove(fp)

    net_objects = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        net_objects[name] = net

    major = placed_major_components()
    major.update(placed_channel_support(loaded_footprints))
    major.update(placed_shared_support(loaded_footprints))
    staged = []
    stage_index = 0
    missing_pads = []
    for ref in sorted(components):
        spec = components[ref]
        fp = loaded_footprints[ref]
        if not hasattr(fp, "SetReference"):
            raise TypeError(f"loader returned {type(fp)!r} for {ref} {spec['footprint']}: {fp!r}")
        fp.SetReference(ref)
        fp.SetValue(spec["value"])
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

        if ref in major:
            x, y, side, rotation = major[ref]
        else:
            # Deliberate component staging area, 5.5 mm grid right of board.
            x = 40.0 + 5.5 * (stage_index % 12)
            y = -30.0 + 5.5 * (stage_index // 12)
            side, rotation = "F", 0
            stage_index += 1
            staged.append(ref)

        pos = pcbnew.VECTOR2I_MM(x, y)
        board.Add(fp)
        fp.SetPosition(pos)
        if side == "B":
            fp.Flip(pos, False)
        fp.SetOrientationDegrees(rotation)

        pad_numbers = {pad.GetNumber() for pad in fp.Pads()}
        expected = {pin for component_ref, pin in pin_nets if component_ref == ref}
        for pin in sorted(expected - pad_numbers):
            missing_pads.append(f"{ref}.{pin} ({spec['footprint']})")
        for pad in fp.Pads():
            name = pin_nets.get((ref, pad.GetNumber()))
            if name:
                pad.SetNet(net_objects[name])

    if missing_pads:
        raise RuntimeError("footprints missing schematic pads:\n  " + "\n  ".join(missing_pads))
    if staged:
        raise RuntimeError("all ESC footprints must be placed in-board; staged: "
                           + ", ".join(staged))

    add_silk_text(board, "VYPER-55A REV A", 0, 34.0, size=0.85)
    # Keep polarity off the exposed solder surface. Vertical labels fit the
    # narrow service corridor between the adjacent inverter cells.
    add_silk_text(board, "BAT+", -8.2, 0.0, size=0.55, rotation=90.0)
    add_silk_text(board, "GND", 8.2, 0.0, size=0.55, rotation=90.0)
    for index, channel in enumerate(L.CHANNELS, 1):
        side = L.MOTOR_SIDE[channel]
        x = side * 12.0
        for phase, y_offset in zip("ABC", L.MOTOR_PAD_STATIONS):
            add_silk_text(board, phase, x, L.CHANNEL_Y[channel] + y_offset,
                          size=0.58)
        add_silk_text(board, f"M{index}", side * 15.0,
                      L.CHANNEL_Y[channel] + 6.6, size=0.62)
    # The control face is intentionally too dense for decorative channel text.
    # The EVT warning remains in the board metadata and Dwgs.User layer.

    pcbnew.SaveBoard(str(OUT), board)
    print(f"wrote {OUT}")
    print(f"components: {len(components)}; true-net pads: {len(pin_nets)}")
    print(f"in-board placements: {len(major)}; staged components: {len(staged)}")
    print("NOT FOR FAB: all copper routing and validation remain open")


if __name__ == "__main__":
    main()
