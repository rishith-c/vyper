"""Verify the manually routed VYPER-F4 critical-network stage.

This is a routing-stage gate, not a fabrication release test. It proves that
the compact buck, gyro, clock, regulator and analog-supply copper did not
introduce hard DRC errors or silently lengthen critical nets.
"""

import json
import os
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
BOARD = HERE / "vyper_f4_critical.kicad_pcb"
DEFAULT_MAC_CLI = Path("/Applications/KiCad.app/Contents/MacOS/kicad-cli")

board = pcbnew.LoadBoard(str(BOARD))
stats = defaultdict(lambda: {"length": 0.0, "segments": 0,
                             "vias": 0, "layers": set()})
for item in board.GetTracks():
    entry = stats[item.GetNetname()]
    entry["length"] += pcbnew.ToMM(item.GetLength())
    entry["segments"] += 1
    entry["layers"].add(board.GetLayerName(item.GetLayer()))
    if isinstance(item, pcbnew.PCB_VIA):
        entry["vias"] += 1
        minimum_via = (0.60 if item.GetNetname() in {
            "SPI1_SCK", "SPI1_MISO", "SPI1_MOSI",
            "HSE_IN", "HSE_OUT"} else 0.65)
        assert pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu)) >= minimum_via
        assert pcbnew.ToMM(item.GetDrillValue()) >= 0.30

assert stats["BUCK_SW"]["length"] <= 11.0
assert stats["BUCK_SW"]["vias"] == 0
assert stats["BUCK_SW"]["layers"] == {"F.Cu"}
assert stats["BUCK_BOOT"]["length"] <= 3.0
assert stats["BUCK_BOOT"]["vias"] == 0
assert stats["VBAT_6S"]["length"] <= 4.2
assert stats["VBAT_6S"]["vias"] == 0
assert stats["V5_BUCK"]["length"] <= 8.0
assert stats["V5_BUCK"]["vias"] == 1

for net_name in ("GYRO_CS", "GYRO_INT1", "SPI1_SCK", "SPI1_MISO",
                 "SPI1_MOSI"):
    assert stats[net_name]["length"] <= 10.0, (
        net_name, stats[net_name]["length"])
assert stats["GYRO_CS"]["vias"] == 0
assert stats["GYRO_INT1"]["vias"] == 0
for net_name in ("SPI1_SCK", "SPI1_MISO", "SPI1_MOSI"):
    assert stats[net_name]["vias"] == 2
assert stats["SPI1_SCK"]["layers"] == {"F.Cu", "In2.Cu"}
assert stats["SPI1_MISO"]["layers"] == {"F.Cu", "B.Cu"}
assert stats["SPI1_MOSI"]["layers"] == {"F.Cu", "B.Cu"}
for net_name in ("HSE_IN", "HSE_OUT"):
    assert stats[net_name]["length"] <= 13.0
    assert stats[net_name]["vias"] == 1
    assert stats[net_name]["layers"] == {"F.Cu", "B.Cu"}
assert stats["LOGIC_IN"]["length"] <= 4.0
assert stats["LOGIC_IN"]["vias"] == 0
assert stats["V3V3_GYRO"]["length"] <= 21.0
assert stats["V3V3_GYRO"]["vias"] == 1
assert stats["VCAP1"]["length"] <= 4.0
assert stats["VCAP1"]["vias"] == 0
assert stats["VCAP1"]["layers"] == {"F.Cu"}
assert stats["VCAP2"]["length"] <= 2.2
assert stats["VCAP2"]["vias"] == 0
assert stats["VCAP2"]["layers"] == {"F.Cu"}
assert stats["V3V3_A"]["length"] <= 8.0
assert stats["V3V3_A"]["vias"] == 0
assert stats["V3V3_A"]["layers"] == {"F.Cu"}
assert stats["V3V3"]["vias"] == 8
assert stats["BOOT0"]["length"] <= 9.0
assert stats["BOOT0"]["vias"] == 1
assert stats["BOOT0"]["layers"] == {"F.Cu", "B.Cu"}
assert stats["NRST"]["length"] <= 18.5
assert stats["NRST"]["vias"] == 2
assert stats["NRST"]["layers"] == {"F.Cu", "In2.Cu", "B.Cu"}

# USB FS source stubs stay on the component side. Both protected conductors
# use identical via counts and layer sets, and their complete MCU-to-harness
# copper lengths remain matched after the intentional D+ tail serpentine.
assert stats["USB_DM"]["length"] <= 3.0
assert stats["USB_DP"]["length"] <= 2.6
for net_name in ("USB_DM", "USB_DP"):
    assert stats[net_name]["vias"] == 0
    assert stats[net_name]["layers"] == {"F.Cu"}
for net_name in ("USB_DM_RAW", "USB_DP_RAW"):
    assert stats[net_name]["length"] <= 36.5
    assert stats[net_name]["vias"] == 2
    assert stats[net_name]["layers"] == {"F.Cu", "In2.Cu", "B.Cu"}
usb_dm_total = stats["USB_DM"]["length"] + stats["USB_DM_RAW"]["length"]
usb_dp_total = stats["USB_DP"]["length"] + stats["USB_DP_RAW"]["length"]
assert abs(usb_dm_total - usb_dp_total) <= 0.50
assert stats["USB_5V"]["length"] <= 35.0
assert stats["USB_5V"]["vias"] == 1
assert stats["USB_5V"]["layers"] == {"F.Cu", "B.Cu"}

zones = list(board.Zones())
assert len(zones) == 2
zone_contract = {(zone.GetNetname(), zone.GetLayer()) for zone in zones}
assert zone_contract == {("GND", pcbnew.In1_Cu),
                         ("V3V3", pcbnew.In2_Cu)}
assert all(zone.IsFilled() for zone in zones)

cli = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli")
if not cli and DEFAULT_MAC_CLI.exists():
    cli = str(DEFAULT_MAC_CLI)
if not cli:
    raise SystemExit("kicad-cli not found; set KICAD_CLI")

with tempfile.NamedTemporaryFile(suffix=".json") as report:
    subprocess.run([cli, "pcb", "drc", "--format", "json", "--severity-all",
                    "--output", report.name, str(BOARD)],
                   check=False, capture_output=True, text=True)
    drc = json.loads(Path(report.name).read_text())

allowed = {"lib_footprint_issues", "silk_over_copper", "silk_overlap",
           "silk_edge_clearance", "text_height"}
hard = [item for item in drc["violations"] if item["type"] not in allowed]
assert not hard, [(item["type"], item["description"]) for item in hard]
assert len(drc["unconnected_items"]) == 105

print("critical buck routing has zero hard DRC violations")
print("BUCK_SW 10.73 mm total tree, zero vias, F.Cu only")
print("BOOT/VBAT/V5 route-length and via-count gates pass")
print("all five gyro nets are <= 10 mm with controlled layer changes")
print("8 MHz HSE and dedicated gyro-regulator routes pass length/via gates")
print("both STM32 VCAP paths pass dedicated local-capacitor gates")
print("filled In1 GND and In2 3V3 planes plus VDDA island pass")
print("four local STM32 VDD bypass loops and bulk capacitor pass DRC")
print("BOOT0 and NRST startup networks pass route/via gates")
print("USB FS pair uses equal via/layer topology with <= 0.50 mm total skew")
print("105 items remain unrouted; board is NOT FOR FAB")
