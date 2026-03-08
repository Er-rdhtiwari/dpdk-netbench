from __future__ import annotations

from pathlib import Path

from netbench.parsing.cryptoperf_parser import parse_cryptoperf_logs


def test_parse_cryptoperf() -> None:
    log_path = Path("data/sample_runs/cryptoperf_run_001/logs/stdout.txt")
    metrics, warnings = parse_cryptoperf_logs([str(log_path)])
    assert warnings == []
    assert metrics["throughput_gbps"] == 12.50
