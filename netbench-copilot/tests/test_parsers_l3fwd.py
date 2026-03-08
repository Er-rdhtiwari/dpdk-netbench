from __future__ import annotations

from pathlib import Path

from netbench.parsing.l3fwd_parser import parse_l3fwd_logs


def test_parse_l3fwd() -> None:
    log_path = Path("data/sample_runs/l3fwd_run_001/logs/stdout.txt")
    metrics, warnings = parse_l3fwd_logs([str(log_path)])
    assert warnings == []
    assert metrics["throughput_mpps"] == 8.8
