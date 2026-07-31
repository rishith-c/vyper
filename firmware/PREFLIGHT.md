# VYPER — bench and pre-flight procedure

**Props off for every step except the last.**

## Bench (first power-up)

1. **Smoke test on a current-limited supply if you have one.** A miswired
   4-in-1 draws hundreds of amps and destroys itself in under a second.
2. Flash Betaflight, then paste `betaflight_vyper.txt` in the CLI, `save`.
3. **Motors tab** — verify direction and order. Fix rotation in BLHeli/AM32,
   not by swapping wires.
4. **Receiver tab** — all channels move the right way, endpoints 1000–2000.
5. **Failsafe** — power the radio off with motors spinning (props off). Motors
   must stop within 4 s. If they don't, stop and fix it.
6. **Accelerometer calibration** on a level surface.
7. **VTX** — 25 mW indoors, and never power it without an antenna.

## The one that is specific to this airframe

8. **Thermal check.** Spool to 50 % for 30 s **with the canopy closed**, then
   immediately feel the ESC. This is a sealed 300 mm tube; the cooling path
   runs nose inlet → cavity → tail. If the ESC is too hot to hold, open the
   inlet before you fly. A closed fuselage is the real risk here, not thrust.

## First flight

9. Props on last. Check each direction against the Betaflight diagram.
10. Hover 1 m for 30 s. Land. **Feel every motor.** Anything hot means a
    prop/tune/bearing problem — do not fly it fast.
11. Only then open it up.
