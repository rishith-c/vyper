/*
 * VYPER_55A_F421 target block for AM32.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 * Paste this complete block into AM32 Inc/targets.h.  It intentionally uses
 * AM32's existing AT32F421 hardware groups; no private firmware is required.
 */

#ifdef VYPER_55A_F421
#define FIRMWARE_NAME "VYPER 55A   "
#define FILE_NAME "VYPER_55A_F421"
#define DEAD_TIME 80

/* PCB: PB4 DShot, PA10/9/8 high PWM, PB1/PB0/PA7 low PWM. */
#define HARDWARE_GROUP_AT_B

/* PCB: phase A/B/C back-EMF dividers on PA0/PA4/PA5. */
#define HARDWARE_GROUP_AT_045

/* PB6 KISS serial telemetry, diode-isolated onto the shared TLM line. */
#define USE_SERIAL_TELEMETRY

/* DRV8323 gain 10 V/V x 0.5 mOhm shunt = 5 mV/A. */
#define MILLIVOLT_PER_AMP 5
#define CURRENT_ADC_PIN GPIO_PINS_2
#define CURRENT_ADC_CHANNEL ADC_CHANNEL_2

/* 100k/10k divider: firmware calibration must use a measured board value. */
#define VOLTAGE_ADC_PIN GPIO_PINS_6
#define VOLTAGE_ADC_CHANNEL ADC_CHANNEL_6

#define USE_NTC
#define NTC_ADC_PIN GPIO_PINS_3
#define NTC_ADC_CHANNEL ADC_CHANNEL_3
#endif
