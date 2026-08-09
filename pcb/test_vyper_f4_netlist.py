"""Connectivity assertions for the authored VYPER-F4 KiCad netlist."""

import re
from pathlib import Path

NETLIST = Path(__file__).with_name("vyper_f4.net")
text = NETLIST.read_text()
firmware = (NETLIST.parent.parent / "firmware" / "vyper_f405" /
            "config.h").read_text()


def child_blocks(source, parent_token, child_token):
    start = source.index(parent_token)
    blocks = []
    depth = 0
    child_start = None
    i = start
    while i < len(source):
        if source[i] == "(":
            if depth == 1 and source.startswith(child_token, i):
                child_start = i
            depth += 1
        elif source[i] == ")":
            depth -= 1
            if child_start is not None and depth == 1:
                blocks.append(source[child_start:i + 1])
                child_start = None
            if depth == 0:
                break
        i += 1
    return blocks


net_blocks = child_blocks(text, "(nets", "(net")
nets = {}
for block in net_blocks:
    name_match = re.search(r'\(name "([^"]+)"\)', block)
    if not name_match:
        continue
    nodes = set(re.findall(
        r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block))
    nets[name_match.group(1)] = nodes

fails = []


def check(name, condition, detail):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}: {detail}")
    if not condition:
        fails.append(name)


check("netlist parses", len(nets) >= 55, f"{len(nets)} named nets")

# No pad may silently belong to two electrical nets.
owners = {}
duplicates = []
for net_name, nodes in nets.items():
    for node in nodes:
        if node in owners and owners[node] != net_name:
            duplicates.append((node, owners[node], net_name))
        owners[node] = net_name
check("one net per component pin", not duplicates,
      "no duplicate assignments" if not duplicates else str(duplicates[:3]))

expected_exact = {
    "BUCK_FB": {("R4", "2"), ("R5", "1"), ("U3", "5")},
    "SPI1_SCK": {("U1", "55"), ("U2", "13")},
    "SPI1_MISO": {("U1", "56"), ("U2", "1")},
    "SPI1_MOSI": {("U1", "57"), ("U2", "14")},
    "GYRO_CS": {("U1", "59"), ("U2", "12")},
    "GYRO_INT1": {("U1", "58"), ("U2", "4")},
    "MOTOR_1": {("J2", "5"), ("U1", "27")},
    "MOTOR_2": {("J2", "6"), ("U1", "26")},
    "MOTOR_3": {("J2", "7"), ("U1", "17")},
    "MOTOR_4": {("J2", "8"), ("U1", "16")},
    "ESC_TELEM": {("J2", "4"), ("U1", "54")},
    "USB_5V": {("D3", "2"), ("D7", "2"), ("J1", "2"), ("C28", "1")},
    "USB_DM_RAW": {("J1", "3"), ("D5", "2"), ("R14", "1")},
    "USB_DP_RAW": {("J1", "4"), ("D6", "2"), ("R15", "1")},
    "SWDIO": {("J7", "2"), ("U1", "46")},
    "SWCLK": {("J7", "3"), ("U1", "49")},
    "BEEPER": {("J8", "2"), ("U1", "2")},
    "LED_RGB_MCU": {("R20", "1"), ("U1", "41"), ("U8", "2")},
    "LED_RGB_LEVEL": {("R19", "1"), ("U8", "4")},
    "LED_RGB_DIN": {("D4", "3"), ("R19", "2")},
}
for name, expected in expected_exact.items():
    actual = nets.get(name, set())
    check(name, actual == expected, f"{sorted(actual)}")

for ref, prefix in (("J3", "RX_UART1"), ("J4", "GPS_UART3"),
                    ("J6", "VTX_UART6")):
    for pin, net_name in ((1, "GND"), (2, "V5_BUCK"),
                          (3, f"{prefix}_TX"), (4, f"{prefix}_RX")):
        check(f"{ref}.{pin} {net_name}",
              (ref, str(pin)) in nets.get(net_name, set()),
              "physical edge-pad contract")

for pin, net_name in ((1, "GND"), (2, "V5_BUCK"),
                      (3, "I2C1_SDA"), (4, "I2C1_SCL")):
    check(f"J5.{pin} {net_name}",
          ("J5", str(pin)) in nets.get(net_name, set()),
          "external magnetometer/I2C edge-pad contract")

required_members = {
    "VBAT_6S": {("J2", "2"), ("U3", "2"), ("R2", "1")},
    "V3V3_GYRO": {("U2", "5"), ("U2", "8"), ("U5", "5")},
    "V3V3": {("U1", "1"), ("U1", "19"), ("U4", "5"), ("U6", "8")},
    "USB_DM": {("U1", "44")},
    "USB_DP": {("U1", "45")},
    "ADC_VBAT": {("U1", "25")},
    "ADC_CURRENT": {("U1", "11")},
}
for name, required in required_members.items():
    actual = nets.get(name, set())
    check(f"{name} required members", required <= actual,
          f"required {sorted(required)}")

check("no schematic-only power flags in PCB netlist", "#FLG" not in text,
      "power-source intent is represented by named external rails")
check("60 V buck selected", "TPS54360DDA" in text,
      "TPS54360DDA present")
check("exact gyro value selected", "ICM-42688-P" in text,
      "ICM-42688-P value overrides the pin-compatible library symbol")
check("RGB uses a 5 V AHCT level shifter",
      "SN74AHCT1G125DBVR" in text and "SK6812MINI-E" in text,
      "PA8 is translated to a 5 V addressable status LED")

resource_contract = {
    "SPI1_SCK_PIN": "PB3", "SPI1_SDI_PIN": "PB4",
    "SPI1_SDO_PIN": "PB5", "GYRO_1_EXTI_PIN": "PB6",
    "GYRO_1_CS_PIN": "PB7", "I2C1_SCL_PIN": "PB8",
    "I2C1_SDA_PIN": "PB9", "GYRO_1_ALIGN": "CW90_DEG",
}
for macro, expected in resource_contract.items():
    match = re.search(rf"^#define\s+{macro}\s+(\S+)", firmware, re.MULTILINE)
    actual = match.group(1) if match else "<missing>"
    check(f"firmware {macro}", actual == expected,
          f"{actual} (expected {expected})")

if fails:
    raise SystemExit(f"{len(fails)} FAILED: {', '.join(fails)}")
print("all authored-netlist checks passed; PCB routing/bring-up still required")
