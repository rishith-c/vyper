"""Keep the AM32 target block synchronized with the authored ESC netlist."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
target = Path(__file__).with_name("vyper_55a_f421_target.h").read_text()
netlist = (ROOT / "pcb" / "vyper_55a_esc.net").read_text()

required_defines = {
    "HARDWARE_GROUP_AT_B": None,
    "HARDWARE_GROUP_AT_045": None,
    "MILLIVOLT_PER_AMP": "5",
    "CURRENT_ADC_PIN": "GPIO_PINS_2",
    "CURRENT_ADC_CHANNEL": "ADC_CHANNEL_2",
    "VOLTAGE_ADC_PIN": "GPIO_PINS_6",
    "VOLTAGE_ADC_CHANNEL": "ADC_CHANNEL_6",
    "NTC_ADC_PIN": "GPIO_PINS_3",
    "NTC_ADC_CHANNEL": "ADC_CHANNEL_3",
}

for name, value in required_defines.items():
    match = re.search(rf"^#define\s+{name}(?:\s+(\S+))?", target, re.MULTILINE)
    assert match, f"missing {name}"
    if value is not None:
        assert match.group(1) == value, f"{name}: {match.group(1)} != {value}"

for channel in range(1, 5):
    mcu = f'U{channel}1'
    expected = {
        27: f'DSHOT_M{channel}', 20: f'M{channel}_PWM_AH',
        15: f'M{channel}_PWM_AL', 19: f'M{channel}_PWM_BH',
        14: f'M{channel}_PWM_BL', 18: f'M{channel}_PWM_CH',
        13: f'M{channel}_PWM_CL', 6: f'M{channel}_BEMF_A',
        10: f'M{channel}_BEMF_B', 11: f'M{channel}_BEMF_C',
        8: f'M{channel}_CURRENT_ADC', 12: f'M{channel}_VOLTAGE_ADC',
        9: f'M{channel}_NTC_ADC',
    }
    for pin, net in expected.items():
        net_block = re.search(
            rf'\(net\s+\(code\s+\d+\)\s+\(name "{re.escape(net)}"\)(.*?)(?=\n\s*\(net|\n\s*\)\)\))',
            netlist, re.DOTALL)
        assert net_block and re.search(
            rf'\(ref "{mcu}"\)\s+\(pin "{pin}"\)', net_block.group(1)), \
            f"{mcu}.{pin} is not on {net}"

print("AM32 target and all four PCB pin maps agree")
