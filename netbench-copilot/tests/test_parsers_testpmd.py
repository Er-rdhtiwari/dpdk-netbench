from __future__ import annotations

from pathlib import Path

from netbench.parsing.testpmd_parser import parse_testpmd_logs


def test_parse_testpmd() -> None:
    log_path = Path("data/sample_runs/testpmd_run_001/logs/stdout.txt")
    metrics, warnings = parse_testpmd_logs([str(log_path)])
    assert warnings == []
    assert metrics["rx_pps"] == 12345678.0
