# Legacy — earlier design iterations

This project went through several airframe layouts before the current one.
They are kept because the reasoning is in the commit history and some of it is
reusable, but **none of it is part of Peregreen-X**.

- `cad_build123d/` — a build123d parametric airframe (flat-plate racer, then a
  faired fuselage with pylons, then swept wing panels, then crossed blades).
  Its own 41-check verification suite lives in that history.
- `tolerance_coupon.stl` (in `../stl/`) is still worth printing: M3/M2 hole
  ladders, wall ladder, bridge tests and an overhang fan for calibrating your
  printer before committing to a long part.

The current design is the CadQuery model at the repo root.
