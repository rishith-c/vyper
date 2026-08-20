"""Run KiCad DRC on the unrouted ESC and reject placement/copper errors.

Unconnected items are expected until routing starts. Presentation/library
warnings are also allowed on this generated review board. Copper shorts,
clearance failures, courtyard overlaps, edge violations, and footprint errors
are not allowed to hide inside that known routing backlog.
"""

import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOARD = HERE / "vyper_55a_esc_unrouted.kicad_pcb"
DEFAULT_MAC_CLI = Path("/Applications/KiCad.app/Contents/MacOS/kicad-cli")

cli = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli")
if not cli and DEFAULT_MAC_CLI.exists():
    cli = str(DEFAULT_MAC_CLI)
if not cli:
    raise SystemExit("kicad-cli not found; set KICAD_CLI to its absolute path")

with tempfile.NamedTemporaryFile(suffix=".rpt") as report:
    result = subprocess.run(
        [cli, "pcb", "drc", "--output", report.name, str(BOARD)],
        check=False,
        capture_output=True,
        text=True,
    )
    text = Path(report.name).read_text()

categories = Counter(re.findall(r"^\[([^]]+)\]:", text, re.MULTILINE))
allowed = {"unconnected_items", "silk_over_copper", "silk_overlap",
           "lib_footprint_issues"}
forbidden = categories.keys() - allowed
assert not forbidden, f"forbidden DRC categories: {sorted(forbidden)}"
assert categories["unconnected_items"] == 499, categories
assert "** Found 0 Footprint errors **" in text

print("KiCad DRC has no shorts, clearance, courtyard, edge, or footprint errors")
print("499 unconnected items remain by design; routing is NOT complete")
print("allowed review-board warnings:",
      dict(sorted((k, v) for k, v in categories.items()
                  if k != "unconnected_items")))
