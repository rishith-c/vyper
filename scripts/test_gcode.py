#!/usr/bin/env python3
"""Static safety/consistency checks for generated Neptune 4 G-code."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MASS = {
    "vyper_shell_body.gcode": 59.48,
    "vyper_shell_nose.gcode": 36.40,
    "vyper_arm_print.gcode": 27.49,
    "vyper_hub.gcode": 27.60,
    "vyper_electronics_cassette.gcode": 3.35,
    "vyper_tail_cap.gcode": 20.32,
}
QUANTITY = {"vyper_arm_print.gcode": 4}


def field(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    assert match, pattern
    return match.group(1)


def check_motion(text: str) -> tuple[float, float, float, float, float, float]:
    absolute = True
    position = {"X": 0.0, "Y": 0.0, "Z": 0.0}
    limits = {axis: [float("inf"), float("-inf")] for axis in position}
    extrusion_moves = 0
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if line == "G90":
            absolute = True
            continue
        if line == "G91":
            absolute = False
            continue
        if line.startswith("G92"):
            for axis, value in re.findall(r"([XYZ])(-?[0-9.]+)", line):
                position[axis] = float(value)
            continue
        if not re.match(r"G[0123](?:\s|$)", line):
            continue
        words = {axis: float(value) for axis, value in
                 re.findall(r"([XYZE])(-?[0-9.]+)", line)}
        if "E" in words:
            extrusion_moves += 1
        for axis in position:
            if axis in words:
                position[axis] = (words[axis] if absolute
                                  else position[axis] + words[axis])
                limits[axis][0] = min(limits[axis][0], position[axis])
                limits[axis][1] = max(limits[axis][1], position[axis])
    assert extrusion_moves > 100, extrusion_moves
    return tuple(value for axis in "XYZ" for value in limits[axis])


def main() -> None:
    total = 0.0
    for filename, expected_mass in EXPECTED_MASS.items():
        path = ROOT / "gcode" / filename
        text = path.read_text(errors="replace")
        assert len(text) > 10_000, path
        assert re.search(r"^M190 S80(?:\.0+)?$", text, re.MULTILINE), filename
        assert re.search(r"^M109 S240(?:\.0+)?$", text, re.MULTILINE), filename
        mass = float(field(text, r"^; total filament used \[g\] = ([0-9.]+)$"))
        assert abs(mass - expected_mass) < 0.01, (filename, mass, expected_mass)
        xmin, xmax, ymin, ymax, zmin, zmax = check_motion(text)
        assert 0 <= xmin <= xmax <= 225, (filename, xmin, xmax)
        assert 0 <= ymin <= ymax <= 225, (filename, ymin, ymax)
        assert 0 <= zmin <= zmax <= 265, (filename, zmin, zmax)
        total += mass * QUANTITY.get(filename, 1)
        print(f"{filename}: {mass:.2f} g, XYZ "
              f"{xmin:.1f}..{xmax:.1f} / {ymin:.1f}..{ymax:.1f} / {zmin:.1f}..{zmax:.1f}")
    assert abs(total - 257.11) < 0.01, total
    print(f"all six files pass; nine-print total {total:.2f} g")


if __name__ == "__main__":
    main()
