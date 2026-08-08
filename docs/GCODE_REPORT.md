# G-code report — Neptune 4 / PETG

Generated 8 August 2026 with OrcaSlicer 2.4.2 using the installed Elegoo
Neptune 4 / 0.4 mm machine profile, the repository's 0.20 mm five-wall process
profile and the Elegoo Generic PETG values (1.27 g/cm³, 240 °C first layer,
250 °C thereafter, 80 °C bed).

| File | Quantity | PETG each | Time each |
|---|---:|---:|---:|
| `gcode/vyper_shell_body.gcode` | 1 | 76.57 g | 3:51:48 |
| `gcode/vyper_shell_nose.gcode` | 1 | 36.92 g | 1:57:12 |
| `gcode/vyper_arm_print.gcode` | 4 | 24.39 g | 2:29:33 |
| `gcode/vyper_hub.gcode` | 1 | 27.31 g | 2:06:51 |
| `gcode/vyper_tail_cap.gcode` | 1 | 20.77 g | 1:09:21 |
| **Total** | 8 prints | **259.13 g** | **19:03:24** |

All five unique files pass the G-code skill's static checks for non-empty
content, movement, extrusion, temperature commands and Neptune 4 XYZ bounds.
Two reviewed warnings remain:

- relative positioning occurs in the vendor end G-code, so bounds checks pause
  only while `G91` is active and resume after `G90`;
- `SET_VELOCITY_LIMIT` is reported unknown by the generic validator but is a
  normal Klipper command for the Neptune 4 profile.

This validation does not simulate extrusion physics or authorize a print.
Review the first-layer placement in OrcaSlicer and print the tolerance coupon
before any structural part.

CAD Viewer handoff was attempted as required, but the installed CAD Viewer
package lacks its documented `agent:start` script. No review URL is claimed;
static G-code validation completed successfully.
