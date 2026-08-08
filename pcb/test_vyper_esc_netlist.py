"""Connectivity assertions for the authored VYPER-55A ESC netlist."""

import re
from pathlib import Path

NETLIST = Path(__file__).with_name("vyper_55a_esc.net")
text = NETLIST.read_text()


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
    if name_match:
        nets[name_match.group(1)] = set(re.findall(
            r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block))

fails = []


def check(name, condition, detail):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}: {detail}")
    if not condition:
        fails.append(name)


check("netlist parses", len(nets) >= 100, f"{len(nets)} named nets")

owners = {}
duplicates = []
for net_name, nodes in nets.items():
    for node in nodes:
        if node in owners and owners[node] != net_name:
            duplicates.append((node, owners[node], net_name))
        owners[node] = net_name
check("one net per component pin", not duplicates,
      "no duplicate assignments" if not duplicates else str(duplicates[:5]))

harness = {
    "PGND": ("J1", "1"),
    "VBAT_6S": ("J1", "2"),
    "ESC_CURRENT_TOTAL": ("J1", "3"),
    "ESC_TELEM": ("J1", "4"),
    "DSHOT_M1": ("J1", "5"),
    "DSHOT_M2": ("J1", "6"),
    "DSHOT_M3": ("J1", "7"),
    "DSHOT_M4": ("J1", "8"),
}
for net_name, node in harness.items():
    check(f"harness {net_name}", node in nets.get(net_name, set()), str(node))
check("battery pigtail positive", ("JBAT", "1") in nets.get("VBAT_6S", set()),
      "JBAT.1 -> VBAT_6S")
check("battery pigtail return", ("JBAT", "2") in nets.get("PGND", set()),
      "JBAT.2 -> PGND")

pwm_contract = {
    "AH": ("20", "34"), "AL": ("15", "35"),
    "BH": ("19", "36"), "BL": ("14", "37"),
    "CH": ("18", "38"), "CL": ("13", "39"),
}
for channel in range(1, 5):
    mcu, drv = f"U{channel}1", f"U{channel}2"
    check(f"M{channel} DShot PB4",
          nets.get(f"DSHOT_M{channel}", set()) ==
          {("J1", str(4 + channel)), (mcu, "27")},
          f"J1.{4 + channel} -> {mcu}.27")
    for signal, (mcu_pin, drv_pin) in pwm_contract.items():
        expected = {(mcu, mcu_pin), (drv, drv_pin)}
        actual = nets.get(f"M{channel}_PWM_{signal}", set())
        check(f"M{channel} PWM {signal}", actual == expected, str(sorted(actual)))

    for letter, mcu_pin, drv_phase_pin, odd, even in (
            ("A", "6", "7", 1, 2),
            ("B", "10", "14", 3, 4),
            ("C", "11", "17", 5, 6)):
        qh, ql = f"Q{channel}{odd}", f"Q{channel}{even}"
        phase = nets.get(f"M{channel}_PHASE_{letter}", set())
        required_phase = {
            (drv, drv_phase_pin), (f"JM{channel}", str("ABC".index(letter) + 1)),
            (f"R{channel}{letter}1", "1"),
            *((qh, str(pin)) for pin in (1, 2, 3)),
            (ql, "5"),
        }
        check(f"M{channel} phase {letter}", required_phase <= phase,
              f"{len(required_phase)} required nodes")
        bemf = nets.get(f"M{channel}_BEMF_{letter}", set())
        check(f"M{channel} BEMF {letter}", (mcu, mcu_pin) in bemf,
              f"{mcu}.{mcu_pin}")
        for side, q, drv_gate_pin in (("H", qh, {"A": "6", "B": "15", "C": "16"}[letter]),
                                      ("L", ql, {"A": "8", "B": "13", "C": "18"}[letter])):
            gate = nets.get(f"M{channel}_GATE_{letter}{side}", set())
            check(f"M{channel} gate {letter}{side}",
                  gate == {(drv, drv_gate_pin), (q, "4")}, str(sorted(gate)))

    power_return = nets.get(f"M{channel}_POWER_RETURN", set())
    required_return = {(drv, "9"), (f"RSH{channel}", "1")}
    for qnum in (2, 4, 6):
        required_return |= {(f"Q{channel}{qnum}", str(pin)) for pin in (1, 2, 3)}
    check(f"M{channel} common low-side shunt", required_return <= power_return,
          f"{len(required_return)} required nodes")
    current = nets.get(f"M{channel}_CURRENT_ADC", set())
    check(f"M{channel} current ADC", current == {
        (drv, "23"), (mcu, "8"), (f"RS{channel}", "1")}, str(sorted(current)))
    check(f"M{channel} voltage ADC", (mcu, "12") in
          nets.get(f"M{channel}_VOLTAGE_ADC", set()), f"{mcu}.12")
    check(f"M{channel} NTC ADC", (mcu, "9") in
          nets.get(f"M{channel}_NTC_ADC", set()), f"{mcu}.9")
    check(f"M{channel} fault monitor", (mcu, "28") in
          nets.get(f"M{channel}_NFAULT", set()), f"{mcu}.28")
    tx_nodes = {(mcu, "29"), (f"DT{channel}", "1")}
    check(f"M{channel} serial telemetry",
          any(nodes == tx_nodes for nodes in nets.values()),
          f"{mcu}.29 -> DT{channel}.1")

    # Each manufacturer land pattern has S1/S2/S3/G plus one continuous drain
    # land; package leads 5-8 are the same drain copper.
    for qnum in range(1, 7):
        qref = f"Q{channel}{qnum}"
        missing = [str(pin) for pin in range(1, 6) if (qref, str(pin)) not in owners]
        check(f"{qref} all pads connected", not missing, str(missing))
    missing_driver = {str(pin) for pin in range(1, 42)
                      if (drv, str(pin)) not in owners}
    check(f"{drv} active pads connected / NC pads explicit",
          missing_driver == {"21", "22", "27"},
          f"NC SOC/SOB/IDRIVE = {sorted(missing_driver)}")

check("buck feedback exact", nets.get("BUCK_FB", set()) ==
      {("R2", "2"), ("R3", "1"), ("U1", "3")},
      str(sorted(nets.get("BUCK_FB", set()))))
check("total current summer output", {
    ("J1", "3"), ("U2", "1"), ("RS6", "1"), ("CS1", "1")
} <= nets.get("ESC_CURRENT_TOTAL", set()),
      str(sorted(nets.get("ESC_CURRENT_TOTAL", set()))))
check("telemetry pullup and four isolators", {
    ("J1", "4"), ("RT1", "1"), *((f"DT{i}", "2") for i in range(1, 5))
} <= nets.get("ESC_TELEM", set()),
      str(sorted(nets.get("ESC_TELEM", set()))))
check("exact MCU selected", text.count("AT32F421K8U7-4") >= 4,
      "four AT32F421K8U7-4 components")
check("exact driver selected", text.count("DRV8323HRTAR") >= 4,
      "four DRV8323HRTAR components")
check("exact 60 V MOSFET selected", text.count("BSC012N06NS") >= 24,
      "24 BSC012N06NS components")
check("dedicated 60 V logic buck selected", "LMR16006XDDCR" in text,
      "LMR16006XDDCR present")

if fails:
    raise SystemExit(f"{len(fails)} FAILED: {', '.join(fails)}")
print("all authored ESC-netlist checks passed; PCB routing/bring-up still required")
