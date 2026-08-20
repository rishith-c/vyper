# VYPER AM32 target

The four ESC channels use the upstream GPL-3.0 AM32 firmware and the
`AT32F421K8U7-4`. `vyper_55a_f421_target.h` is a complete target block for
AM32's `Inc/targets.h`; the file remains GPL-3.0-or-later so it can be copied
into an AM32 checkout without relicensing AM32 code.

## Reproducible integration

1. Clone [AM32](https://github.com/am32-firmware/AM32) and record the commit.
2. Insert `vyper_55a_f421_target.h` before the hardware-group definitions in
   `Inc/targets.h`.
3. Run `make VYPER_55A_F421`. Flash one channel through its four SWD pads and
   the PB4-compatible AT32F421 bootloader before attempting passthrough.
4. Start with 80-count dead time, 24 kHz PWM, demag compensation and conservative
   current limits. Gate waveforms, dead time and switching overshoot must be
   measured before changing those values.

The current target uses only upstream-supported pin groups. PB5 is physically
connected to DRV8323 `nFAULT` for capture during bring-up, but stock AM32 does
not consume that signal. The DRV8323's UVLO, VDS OCP, gate-fault and thermal
shutdown remain hardware-enforced; PB5 firmware handling is a later upstreamable
feature, not a claimed present protection.

No prebuilt binary is committed because a binary without a recorded AM32
commit and bench qualification would be unsafe and irreproducible.
