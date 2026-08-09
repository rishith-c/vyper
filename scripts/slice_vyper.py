#!/usr/bin/env python3
"""Regenerate every Neptune 4 G-code file from the checked-in VYPER STLs.

Orca's command-line loader does not resolve profile inheritance, so this
script flattens the installed Elegoo profiles before invoking OrcaSlicer.
It also prevents the GUI's Cool Plate default from silently replacing the
repository's 80 C PETG bed setting.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORCA = Path("/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer")
PROFILE_ROOT = (
    Path.home() / "Library/Application Support/OrcaSlicer/system/Elegoo"
)

PARTS = (
    ("vyper_shell_body", 0, False),
    ("vyper_shell_nose", 0, False),
    ("vyper_arm_print", 0, True),
    ("vyper_hub", 0, False),
    ("vyper_electronics_cassette", 90, False),
    ("vyper_tail_cap", 0, False),
)


def profile_index() -> dict[tuple[str, str], Path]:
    result = {}
    for path in PROFILE_ROOT.rglob("*.json"):
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and data.get("type") and data.get("name"):
            result[(data["type"], data["name"])] = path
    return result


def flatten(path: Path, index: dict[tuple[str, str], Path]) -> dict:
    data = json.loads(path.read_text())
    merged = {}
    parent = data.get("inherits")
    if parent:
        parent_path = index.get((data["type"], parent))
        if parent_path is None:
            raise RuntimeError(f"cannot resolve {data['type']} profile {parent!r}")
        merged.update(flatten(parent_path, index))
    merged.update(data)
    merged.pop("inherits", None)
    return merged


def write_profile(path: Path, data: dict) -> None:
    data = dict(data)
    data.update({"from": "system", "instantiation": "true"})
    data.pop("inherits", None)
    path.write_text(json.dumps(data, indent=2))


def value(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"generated G-code lacks {pattern!r}")
    return match.group(1)


def main() -> None:
    if not ORCA.exists():
        raise SystemExit(f"OrcaSlicer 2.4.x not found at {ORCA}")

    index = profile_index()
    machine = flatten(
        PROFILE_ROOT / "machine/Elegoo Neptune 4 (0.4 nozzle).json", index
    )
    process = flatten(
        PROFILE_ROOT
        / "process/0.20mm Standard @Elegoo Neptune4 (0.4 nozzle).json",
        index,
    )
    process.update(
        json.loads((ROOT / "print_profiles/vyper_020_petg_process.json").read_text())
    )
    filament = flatten(
        PROFILE_ROOT / "filament/Generic PETG @Elegoo.json", index
    )
    filament.update(
        json.loads((ROOT / "print_profiles/vyper_generic_petg.json").read_text())
    )

    with tempfile.TemporaryDirectory(prefix="vyper-orca-") as temp_name:
        temp = Path(temp_name)
        write_profile(temp / "machine.json", machine)
        write_profile(temp / "process.json", process)
        write_profile(temp / "filament.json", filament)

        for stem, rotate_x, needs_support in PARTS:
            source = ROOT / "stl" / f"{stem}.stl"
            if not source.exists():
                raise FileNotFoundError(source)
            output_dir = temp / stem
            output_dir.mkdir()
            command = [
                str(ORCA),
                "--logfile", str(output_dir / "orca.log"),
                "--debug", "4",
                "--slice", "0",
                "--no-check",
                "--ensure-on-bed",
                "--outputdir", str(output_dir),
                "--load-settings",
                f"{temp / 'machine.json'};{temp / 'process.json'}",
                "--load-filaments", str(temp / "filament.json"),
            ]
            if rotate_x:
                command += ["--rotate-x", str(rotate_x)]
            if needs_support:
                command += ["--enable-support", "--support-on-build-plate-only"]
            command.append(str(source))
            try:
                subprocess.run(command, check=True, cwd=ROOT)
            except subprocess.CalledProcessError:
                log = output_dir / "orca.log"
                if log.exists():
                    print(log.read_text(errors="replace")[-8000:])
                raise

            generated = output_dir / "plate_1.gcode"
            text = generated.read_text(errors="replace")
            bed = value(r"^M190 S([0-9.]+)$", text)
            nozzle = value(r"^M109 S([0-9.]+)$", text)
            mass = value(r"^; total filament used \[g\] = ([0-9.]+)$", text)
            duration = value(
                r"^; estimated printing time \(normal mode\) = (.+)$", text
            )
            if float(bed) != 80.0 or float(nozzle) != 240.0:
                raise RuntimeError(
                    f"{stem}: expected PETG start 80/240 C, got {bed}/{nozzle}"
                )
            destination = ROOT / "gcode" / f"{stem}.gcode"
            shutil.copy2(generated, destination)
            print(f"{stem}: {mass} g, {duration}, start {bed}/{nozzle} C")


if __name__ == "__main__":
    main()
