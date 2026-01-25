from __future__ import annotations

import re

from netbench.parsing.common import read_logs


def parse_l3fwd_logs(log_paths: list[str]) -> tuple[dict, list[str]]:
    text = read_logs(log_paths)
    warnings: list[str] = []

    metrics: dict[str, float | str] = {}
    rx = re.search(r"Packets RX:\s*([0-9.]+)", text, re.IGNORECASE)
    tx = re.search(r"Packets TX:\s*([0-9.]+)", text, re.IGNORECASE)
    thr = re.search(r"Throughput \(Mpps\):\s*([0-9.]+)", text)
    lat = re.search(r"Latency \(us\):\s*([0-9.]+)", text)

    if rx:
        metrics["packets_rx"] = float(rx.group(1))
    if tx:
        metrics["packets_tx"] = float(tx.group(1))
    if thr:
        metrics["throughput_mpps"] = float(thr.group(1))
    if lat:
        metrics["latency_us"] = float(lat.group(1))

    if not metrics:
        warnings.append("No metrics found")
    return metrics, warnings
