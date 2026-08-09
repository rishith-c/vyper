# VYPER-55A 4-in-1 ESC — EVT architecture

Status: **architecture and floorplan under test; not routed, not fire-safe,
not approved for a LiPo or flight.** The name records a 55 A, 2 s design
target—not an achieved rating.

## Locked architecture

Each of the four electrically independent channels uses:

- `AT32F421K8U7-4`, QFN32 4×4 mm, one MCU per motor. AM32 directly supports
  the AT32F421 and provides DShot, bidirectional DShot, telemetry, variable PWM
  and stuck-rotor protection.
- `DRV8323HRTAR`, 6×6 mm WQFN, a 6–60 V three-phase smart gate driver with a
  65 V absolute maximum, three current-sense amplifiers, adjustable gate
  current, VDS over-current protection, gate-fault detection, UVLO and thermal
  shutdown.
- Six `BSC012N06NS` 60 V, 1.2 mΩ OptiMOS 5 devices: one high-side and one
  low-side SuperSO8 per phase. The hot-junction design screening value is
  deliberately doubled to 2.4 mΩ.
- Three RC-filtered phase dividers into AT32 pins PA0/PA4/PA5. AM32's F421
  target multiplexes the MCU's internal comparator among these pins for
  back-EMF zero crossing; no imaginary external comparator is omitted.
- One NTC beside the hottest half bridge and the driver's `nFAULT` tied to the
  MCU. Hardware fault action must shut all six inputs low; firmware telemetry
  is secondary.
- One `WSLF2512R0005FEA` 0.5 mΩ, 10 W shunt in each channel's common low-side
  return. The DRV8323's 10 V/V CSA therefore reports 5 mV/A to PA2. A
  `TLV9061IDBVR` equal-resistor averager with gain 4 reports the sum of all
  four channels to the FC at the same 5 mV/A scale.

A dedicated `LMR16006XDDCR` 60 V / 600 mA buck supplies 3.3 V logic. Four
AT32F421 devices draw at most 82.8 mA total at the datasheet's 105 °C,
120 MHz maximum-current point, retaining more than 7× regulator current
margin before the small analog load. The rail still requires startup, ripple
and closed-body thermal validation.

## Board and current path

- 30×72 mm, R3 corners, 24×64 mm M2 pattern, six layers. The board mounts
  longitudinally and vertically in the removable cassette.
- 3 oz outer copper; 2 oz inner copper design request. Fabricator capability,
  finished thickness and current-density review remain release gates.
- F.Cu outward face: all 24 MOSFETs in four stacked inverter cells. Each
  high/low pair shares an X station and uses a same-face switch loop. Gate
  drivers and controllers sit directly behind the cells on B.Cu.
- Inner planes: `VBAT`, `PGND`, `3V3`, and a quiet logic-ground reference.
  Logic and power grounds meet once at the driver-recommended point; they are
  not connected by a long skinny trace.
- Each phase output is a plated long-edge pad; channels alternate left/right
  to avoid crossed phase leads. Central 12-AWG pigtail pads halve the worst
  distribution distance along the board.
- Two 28×27.5×1 mm aluminium spreaders sit outside the MOSFET face over a
  0.5 mm dielectric thermal interface rated at least 1 kV. A 6 mm centre gap
  leaves the battery and buck-regulator service bay accessible. The plates are never allowed
  to contact component leads or copper directly.
- An external **470–1000 µF, 50 V, low-ESR** capacitor is soldered directly to
  the battery pigtail with the shortest possible leads. A remote capacitor at
  the XT60 does not control the board's commutation loop.

The floorplan is encoded in `vyper_esc_layout.py`; `test_vyper_esc.py` checks
the longitudinal outline, holes, 52 modeled major/support courtyards,
same-cooling-face half bridges, gate-loop distance and voltage margins.

`vyper_esc_schematic.py` authors the full 159-net electrical design and emits
`vyper_55a_esc.net`. `test_vyper_esc_netlist.py` verifies the exact AM32 pin
contract, all 24 manufacturer TDSON land patterns, all four 41-pad drivers,
three phases and six gates per channel, shunts, ADCs, telemetry isolation,
regulator feedback and the eight-pin FC harness. SKiDL ERC currently reports
zero errors and zero warnings; this is schematic evidence, not routed-PCB
evidence.

## Current and thermal limits

The selected motor's manufacturer bench point is 45 A. VYPER therefore uses
a **30 A continuous design target in the enclosed body and a 55 A / 2 s burst
target**. For six-step commutation, two hot MOSFETs conduct at once:

`Pcond ≈ 2 × I² × 2.4 mΩ`

- 30 A: 4.3 W/channel before switching, copper and connector loss.
- 55 A: 14.5 W/channel before switching, copper and connector loss.

That arithmetic is why “55 A” cannot be declared continuous from a datasheet.
An instrumented motor dyno and a closed-fuselage thermal test set the real
rating.

## AI PCB tools — useful boundary

- [Quilter](https://www.quilter.ai/product) accepts a schematic and board
  constraints, then generates placement/routing candidates with DRC and
  physics checks. It is the best candidate after the critical half bridges,
  shunts, bulk decoupling and connectors are pre-placed.
- [DeepPCB](https://deeppcb.ai/) supports KiCad, up to eight layers and
  multi-plane routing. It can be used as a second independent routing attempt.
- [Flux](https://www.flux.ai/COPILOT) is strongest for schematic-aware part
  research and editing; Flux's own documentation says its PCB-layout/trace
  understanding is currently limited.

None of these tools supplies missing requirements, chooses safe over-current
thresholds, validates a MOSFET SOA, or turns a DRC-clean board into a tested
ESC. A human power-layout review and the gates below remain mandatory.

## Mandatory gates before LiPo power

1. Complete schematic, pin map and AM32 custom target; pass KiCad ERC with zero
   unexplained errors.
2. Route the critical power stage by hand from the TI DRV832x layout guide;
   then use AI only for candidate completion. Pass fab-profile DRC with zero
   violations and zero unconnected pads.
3. Review MOSFET SOA, gate charge, dead time, shunt power, regulator startup,
   ceramic DC-bias derating and every component's voltage rating.
4. Bare-board isolation and hipot checks; then power logic from a current-
   limited bench supply. No LiPo and no motor.
5. Scope all six gates at 12 V with differential probes. Verify dead time,
   no shoot-through, `nFAULT`, UVLO and stuck-rotor shutdown.
6. Spin one motor without a prop at 12 V; then dyno behind a shield at 3S, 4S
   and 6S. Record bus transient, current, RPM and thermal images.
7. Accept only if the 6S switch-node overshoot stays below 50 V, no component
   exceeds its derated limit, and 30 A steady / 55 A for 2 s pass in the closed
   fuselage. Any failure removes the rating; it does not get explained away.

Primary references: [TI DRV8323 product and datasheet](https://www.ti.com/product/DRV8323),
[TI DRV832x layout guide](https://www.ti.com/lit/an/slva951/slva951.pdf),
[Infineon BSC012N06NS](https://www.infineon.com/cms/en/product/power/mosfet/n-channel/bsc012n06ns/),
[Artery AT32F421](https://www.arterychip.com/en/product/AT32F421.jsp), and
[AM32](https://github.com/am32-firmware/AM32).
