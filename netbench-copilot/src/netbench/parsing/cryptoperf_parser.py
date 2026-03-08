from __future__ import annotations

import re

from netbench.parsing.common import read_logs


def parse_cryptoperf_logs(log_paths: list[str]) -> tuple[dict, list[str]]:
    text = read_logs(log_paths)
    warnings: list[str] = []

    metrics: dict[str, float | str] = {}
    algo = re.search(r"Algorithm:\s*(.+)", text, re.IGNORECASE)
    if algo:
        metrics["algorithm"] = algo.group(1).strip()
    ops = re.search(r"Ops/s:\s*([0-9.]+)", text)
    if ops:
        metrics["ops_per_sec"] = float(ops.group(1))
    thr = re.search(r"Throughput \(Gbps\):\s*([0-9.]+)", text)
    if thr:
        metrics["throughput_gbps"] = float(thr.group(1))
    lat = re.search(r"Latency \(us\):\s*([0-9.]+)", text)
    if lat:
        metrics["latency_us"] = float(lat.group(1))

    if not metrics:
        warnings.append("No metrics found")
    return metrics, warnings
