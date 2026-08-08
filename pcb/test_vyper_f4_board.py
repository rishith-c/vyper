"""Verify FC netlist-to-footprint transfer on the unrouted KiCad board."""

import math
import re
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vyper_f4_layout as L  # noqa: E402

board = pcbnew.LoadBoard(str(HERE / "vyper_f4_unrouted.kicad_pcb"))
netlist = (HERE / "vyper_f4.net").read_text()


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
    match = re.search(r'\(name "([^"]+)"\)', block)
    if not match:
        continue
    for ref, pin in re.findall(
            r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
        expected_nodes[(ref, pin)] = match.group(1)

footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
board_refs = set(footprints) - {f"H{i}" for i in range(1, 5)}
assert board_refs == expected_refs

errors = []
for (ref, pin), net_name in expected_nodes.items():
    pads = [pad for pad in footprints[ref].Pads() if pad.GetNumber() == pin]
    if not pads:
        errors.append(f"{ref}.{pin}: no physical pad")
    elif any(pad.GetNetname() != net_name for pad in pads):
        errors.append(f"{ref}.{pin}: expected {net_name}")
assert not errors, "\n".join(errors[:20])

for ref, count in (("J3", 4), ("J4", 4), ("J5", 4), ("J6", 4),
                   ("J7", 4), ("J8", 2)):
    assert {p.GetNumber() for p in footprints[ref].Pads()} == {
        str(i) for i in range(1, count + 1)}

for ref, group in (("J3", "J3_rx_uart1"), ("J4", "J4_gps_uart3"),
                   ("J5", "J5_aux_uart4"), ("J6", "J6_vtx_uart6")):
    pads = {p.GetNumber(): p for p in footprints[ref].Pads()}
    for number, (x, y, _label) in enumerate(L.PAD_GROUPS[group], 1):
        actual = pads[str(number)].GetPosition()
        assert abs(pcbnew.ToMM(actual.x) - x) < 1e-6
        assert abs(pcbnew.ToMM(actual.y) + y) < 1e-6

assert len(L.PASSIVES) == 57
for ref, spec in L.PASSIVES.items():
    actual = footprints[ref].GetPosition()
    assert abs(pcbnew.ToMM(actual.x) - spec["pos"][0]) < 1e-6
    assert abs(pcbnew.ToMM(actual.y) + spec["pos"][1]) < 1e-6


def distance(a, b):
    return math.dist(a, b)


def part_pos(key):
    return L.PARTS[key]["pos"]


# Proximity gates preserve the intent of the manually packed passive groups.
assert distance(L.PASSIVES["D1"]["pos"], part_pos("U3_buck_TPS54360")) <= 9.0
assert distance(part_pos("L1_buck_inductor"), part_pos("U3_buck_TPS54360")) <= 9.0
assert max(distance(L.PASSIVES[r]["pos"], part_pos("L1_buck_inductor"))
           for r in ("C5", "C7")) <= 8.0
assert min(distance(L.PASSIVES[r]["pos"], part_pos("U3_buck_TPS54360"))
           for r in ("C4", "C6")) <= 6.0
assert max(distance(L.PASSIVES[r]["pos"], part_pos("U2_gyro_ICM42688P"))
           for r in ("C24", "C25")) <= 4.0
assert max(distance(L.PASSIVES[r]["pos"], part_pos("U1_mcu_STM32F405RGT6"))
           for r in ("C12", "C13", "C14", "C15", "C16", "C17",
                     "C18", "C19", "C20")) <= 10.0
assert max(distance(L.PASSIVES[r]["pos"], part_pos("Y1_xtal_8MHz"))
           for r in ("C21", "C22", "R7")) <= 4.2
assert max(distance(L.PASSIVES[r]["pos"], part_pos("U5_gyro_ldo_AP2112K"))
           for r in ("C10", "C11")) <= 4.0
assert max(distance(L.PASSIVES[r]["pos"], part_pos("U6_flash_W25Q128"))
           for r in ("C26", "R10", "R11")) <= 6.5
assert max(distance(L.PASSIVES[r]["pos"], part_pos("U7_baro_BMP280"))
           for r in ("C27", "R12", "R13")) <= 3.0
assert max(distance(L.PASSIVES[r]["pos"], part_pos("U1_mcu_STM32F405RGT6"))
           for r in ("C29", "C30")) <= 9.0

assert board.GetCopperLayerCount() == 4
assert len(board.GetTracks()) == 0
assert len(board.Zones()) == 0
assert len(expected_refs) == 74
assert len(expected_nodes) == 242
assert len(board.GetNetInfo().NetsByName()) == 60

print("all 74 FC references and 242 netlist nodes reach real PCB pads")
print("all 57 passives are in-outline and preserve functional proximity gates")
print("four layers; zero tracks/zones by design -- unrouted review board, NOT FOR FAB")
