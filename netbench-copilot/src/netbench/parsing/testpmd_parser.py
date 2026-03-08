from __future__ import annotations

import re

from netbench.parsing.common import read_logs


def parse_testpmd_logs(log_paths: list[str]) -> tuple[dict, list[str]]:
    text = read_logs(log_paths)
    warnings: list[str] = []

    metrics: dict[str, float | str] = {}
    rx_pps = re.search(r"Rx-pps:\s*([0-9.]+)", text, re.IGNORECASE)
    tx_pps = re.search(r"Tx-pps:\s*([0-9.]+)", text, re.IGNORECASE)
    rx_bps = re.search(r"Rx-bps:\s*([0-9.]+)", text, re.IGNORECASE)
    tx_bps = re.search(r"Tx-bps:\s*([0-9.]+)", text, re.IGNORECASE)
    lat = re.search(r"Latency \(us\):\s*([0-9.]+)", text)

    if rx_pps:
        metrics["rx_pps"] = float(rx_pps.group(1))
    if tx_pps:
        metrics["tx_pps"] = float(tx_pps.group(1))
    if rx_bps:
        metrics["rx_bps"] = float(rx_bps.group(1))
    if tx_bps:
        metrics["tx_bps"] = float(tx_bps.group(1))
    if lat:
        metrics["latency_us"] = float(lat.group(1))

    if not metrics:
        warnings.append("No metrics found")
    return metrics, warnings
