# VYPER — bench and pre-flight procedure

**Props off for every step except the last.**

## Bench (first power-up)

1. **First power is mandatory on a current-limited bench supply through a
   smoke stopper, no LiPo.** A miswired 4-in-1 can fail in under a second.
2. Flash Betaflight, then paste `betaflight_vyper.txt` in the CLI, `save`.
3. **Motors tab** — verify direction and order. Fix rotation in BLHeli/AM32,
   not by swapping wires.
4. **Receiver tab** — all channels move the right way, endpoints 1000–2000.
5. **Failsafe** — power the radio off with motors spinning (props off). Motors
   must stop on the configured timeout. If they do not, stop and fix it.
6. **Accelerometer calibration** on a level surface.
7. **VTX** — 25 mW indoors, and never power it without an antenna.

## The one that is specific to this airframe

8. **Instrumented thermal check.** Follow `docs/VALIDATION_GATES.md`; do not
   substitute a hand touch for temperature/current logging. The Ø57×360 mm
   body encloses the ESC, so test it in the closed fuselage. Stop at the listed
   MOSFET, PCB, connector and battery limits.

## First flight

9. Props on last. Check each direction against the Betaflight diagram.
10. Hover at low altitude in a controlled test area. Land and log every motor
    and ESC-channel temperature. Investigate any asymmetry before continuing.
11. Expand speed only through the G5 increments in `docs/VALIDATION_GATES.md`.
