# G-code report — Neptune 4 / PETG

Generated 8 August 2026 with OrcaSlicer 2.4.2 using the installed Elegoo
Neptune 4 / 0.4 mm machine profile, the repository's 0.20 mm five-wall process
profile and the Elegoo Generic PETG values (1.27 g/cm³, 240 °C first layer,
250 °C thereafter, 80 °C bed).

| File | Quantity | PETG each | Time each |
|---|---:|---:|---:|
| `gcode/vyper_shell_body.gcode` | 1 | 59.48 g | 2:47:29 |
| `gcode/vyper_shell_nose.gcode` | 1 | 36.40 g | 2:00:01 |
| `gcode/vyper_arm_print.gcode` | 4 | 27.49 g | 1:48:13 |
| `gcode/vyper_hub.gcode` | 1 | 27.60 g | 1:20:56 |
| `gcode/vyper_electronics_cassette.gcode` | 1 | 3.35 g | 0:12:59 |
| `gcode/vyper_tail_cap.gcode` | 1 | 20.32 g | 1:05:12 |
| **Total** | 9 prints | **257.11 g** | **14:39:29** |

The 25° arm print orientation requires build-plate-only support; the other
five parts remain support-free. Orca's feature tags assign approximately
2.07 g per arm (8.28 g total) to support and support-interface extrusion; that
allowance is removed only when comparing slicer mass with the support-free
solid-volume sanity estimate. It remains included in the 257.11 g build mass
and 715 g aircraft estimate. All six unique files pass static checks for non-empty
content, movement, extrusion, temperature commands and Neptune 4 XYZ bounds.
Two reviewed warnings remain:

- relative positioning occurs in the vendor end G-code, so bounds checks pause
  only while `G91` is active and resume after `G90`;
- `SET_VELOCITY_LIMIT` is reported unknown by the generic validator but is a
  normal Klipper command for the Neptune 4 profile.

All files now explicitly start at an 80 °C bed and 240 °C nozzle; the previous
Cool Plate fallback of 35 °C was rejected. This validation does not simulate extrusion physics or authorize a print.
Review the first-layer placement in OrcaSlicer and print the tolerance coupon
before any structural part.

CAD Viewer handoff was attempted as required, but the installed CAD Viewer
package lacks its documented `agent:start` script. No review URL is claimed;
static G-code validation completed successfully.
