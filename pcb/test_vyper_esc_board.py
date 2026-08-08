"""Verify netlist-to-footprint transfer on the unrouted KiCad review board.

Run with KiCad's bundled Python 3.9, not system Python.
"""

import re
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
board = pcbnew.LoadBoard(str(HERE / "vyper_55a_esc_unrouted.kicad_pcb"))
netlist = (HERE / "vyper_55a_esc.net").read_text()


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


expected_refs = set(re.findall(r'\(comp\s+\(ref "([^"]+)"\)', netlist))
expected_nodes = {}
for block in child_blocks(netlist, "(nets", "(net"):
    name_match = re.search(r'\(name "([^"]+)"\)', block)
    if not name_match:
        continue
    for ref, pin in re.findall(
            r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
        expected_nodes[(ref, pin)] = name_match.group(1)

footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
board_refs = set(footprints) - {f"H{i}" for i in range(1, 5)}
assert board_refs == expected_refs, (
    f"ref mismatch missing={sorted(expected_refs - board_refs)} "
    f"extra={sorted(board_refs - expected_refs)}")

errors = []
for (ref, pin), net_name in expected_nodes.items():
    pads = [pad for pad in footprints[ref].Pads() if pad.GetNumber() == pin]
    if not pads:
        errors.append(f"{ref}.{pin}: no physical pad")
    elif any(pad.GetNetname() != net_name for pad in pads):
        errors.append(f"{ref}.{pin}: expected {net_name}, got "
                      f"{sorted({pad.GetNetname() for pad in pads})}")
assert not errors, "\n".join(errors[:20])

for channel in range(1, 5):
    for qnum in range(1, 7):
        numbers = {p.GetNumber() for p in footprints[f"Q{channel}{qnum}"].Pads()
                   if p.GetNumber()}
        assert numbers == {"1", "2", "3", "4", "5"}, numbers
    driver_numbers = {p.GetNumber() for p in footprints[f"U{channel}2"].Pads()}
    assert driver_numbers == {str(i) for i in range(1, 42)}, driver_numbers

assert board.GetCopperLayerCount() == 6
assert len(board.GetTracks()) == 0
assert len(board.Zones()) == 0
assert len(expected_refs) == 195
assert len(expected_nodes) == 715
assert len(board.GetNetInfo().NetsByName()) == 160  # 159 named plus net 0.

print("all 195 references and 715 authored netlist nodes reach real PCB pads")
print("six layers; zero tracks/zones by design -- unrouted review board, NOT FOR FAB")
