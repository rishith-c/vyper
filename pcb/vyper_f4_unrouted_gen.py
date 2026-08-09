"""Build a true-footprint, true-net KiCad FC review board.

Run with KiCad's bundled Python 3.9. Major ICs, external interfaces and every
passive are placed at mechanically/electrically checked coordinates. The
ratsnest remains explicit because no copper is routed. This file is NOT a fab
release.
"""

import re
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
NETLIST = HERE / "vyper_f4.net"
SOURCE_BOARD = HERE / "vyper_f4.kicad_pcb"
OUT = HERE / "vyper_f4_unrouted.kicad_pcb"
FP_ROOT = Path("/Applications/KiCad.app/Contents/SharedSupport/footprints")

sys.path.insert(0, str(HERE))
import vyper_f4_layout as L  # noqa: E402


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
        components[field("ref")] = {
            "value": field("value"), "footprint": field("footprint")}

    pin_nets, net_names = {}, []
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


def smd_layers(side="F"):
    layers = pcbnew.LSET()
    for layer in ((pcbnew.B_Cu, pcbnew.B_Mask, pcbnew.B_Paste)
                  if side == "B" else
                  (pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_Paste)):
        layers.AddLayer(layer)
    return layers


def add_smd_pad(fp, number, x, y, sx, sy, side="F"):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(number))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
    pad.SetRoundRectRadiusRatio(0.2)
    pad.SetSize(pcbnew.VECTOR2I_MM(sx, sy))
    pad.SetFPRelativePosition(pcbnew.VECTOR2I_MM(x, y))
    pad.SetLayerSet(smd_layers(side))
    fp.Add(pad)


def custom_connector(ref):
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPIDAsString(f"VYPER:{ref}_SOLDER_PADS")
    if ref in ("J3", "J4", "J5", "J6"):
        group_name = {"J3": "J3_rx_uart1", "J4": "J4_gps_uart3",
                      "J5": "J5_aux_uart4", "J6": "J6_vtx_uart6"}[ref]
        group = L.PAD_GROUPS[group_name]
        centre_y = sum(p[1] for p in group) / len(group)
        # Pin order follows the layout list. KiCad local +Y points down.
        for number, (_x, y, _label) in enumerate(group, 1):
            add_smd_pad(fp, number, 0, -(y - centre_y), 1.6, 1.6)
    elif ref == "J7":
        for number, (x, y) in enumerate(
                ((-0.635, -0.635), (0.635, -0.635),
                 (-0.635, 0.635), (0.635, 0.635)), 1):
            add_smd_pad(fp, number, x, y, 0.8, 0.8)
    elif ref == "J8":
        add_smd_pad(fp, 1, -0.635, 0, 0.9, 1.3)
        add_smd_pad(fp, 2, 0.635, 0, 0.9, 1.3)
    else:
        raise KeyError(ref)
    return fp


def load_library_footprint(loader, identifier):
    library, name = identifier.split(":", 1)
    fp = loader.FootprintLoad(str(FP_ROOT / f"{library}.pretty"), name)
    if fp is None:
        raise FileNotFoundError(f"footprint not found: {identifier}")
    return fp


def layout_xy(point):
    return point[0], -point[1]


def placed_components():
    result = {}
    for key, spec in L.PARTS.items():
        ref = key.split("_", 1)[0]
        result[ref] = (*layout_xy(spec["pos"]), spec["side"], spec.get("rot", 0))
    for ref, group in (("J3", "J3_rx_uart1"), ("J4", "J4_gps_uart3"),
                       ("J5", "J5_aux_uart4"), ("J6", "J6_vtx_uart6")):
        pads = L.PAD_GROUPS[group]
        result[ref] = (pads[0][0], -sum(p[1] for p in pads) / len(pads), "F", 0)
    for ref, spec in L.PASSIVES.items():
        result[ref] = (*layout_xy(spec["pos"]), spec["side"], spec["rot"])
    return result


def main():
    components, pin_nets, net_names = parse_netlist()
    loader = pcbnew.PCB_IO_KICAD_SEXPR()
    loaded = {
        ref: (custom_connector(ref) if ref in {"J3", "J4", "J5", "J6", "J7", "J8"}
              else load_library_footprint(loader, spec["footprint"]))
        for ref, spec in components.items()
    }

    board = pcbnew.LoadBoard(str(SOURCE_BOARD))
    if board is None:
        raise RuntimeError(f"failed to load {SOURCE_BOARD}")
    board.SetCopperLayerCount(4)
    # Keep only the mechanical outline from the generated placement study.
    # Its global courtyard/silkscreen rectangles are construction aids, not
    # production artwork; the real library footprints provide their own.
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

    major = placed_components()
    staged, missing_pads, stage_index = [], [], 0
    for ref in sorted(components):
        spec, fp = components[ref], loaded[ref]
        fp.SetReference(ref)
        fp.SetValue(spec["value"])
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        if ref in major:
            x, y, side, rotation = major[ref]
        else:
            x = 32.0 + 8.0 * (stage_index % 8)
            y = -30.0 + 8.0 * (stage_index // 8)
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
        expected = {pin for component_ref, pin in pin_nets
                    if component_ref == ref}
        for pin in sorted(expected - pad_numbers):
            missing_pads.append(f"{ref}.{pin} ({spec['footprint']})")
        for pad in fp.Pads():
            name = pin_nets.get((ref, pad.GetNumber()))
            if name:
                pad.SetNet(net_objects[name])

    if missing_pads:
        raise RuntimeError("footprints missing netlist pads:\n  " +
                           "\n  ".join(missing_pads))

    pcbnew.SaveBoard(str(OUT), board)
    print(f"wrote {OUT}")
    print(f"components: {len(components)}; true-net pads: {len(pin_nets)}")
    print(f"in-board placements: {len(major)}; staged components: {len(staged)}")
    print("NOT FOR FAB: routing, review and hardware qualification remain open")


if __name__ == "__main__":
    main()
