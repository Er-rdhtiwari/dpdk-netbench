from __future__ import annotations

from netbench.mcp_server.server import MCPServer


def test_render_command() -> None:
    server = MCPServer()
    resp = server.render_command(
        {
            "benchmark": "cryptoperf",
            "run_yaml": {
                "benchmark": "cryptoperf",
                "scenarios": {"scenario_001": {"algorithm": "aes-gcm"}},
                "eal": {"core_list": "0-3", "socket_mem": "1024", "file_prefix": "nb"},
            },
            "scenario_key": "scenario_001",
        }
    )
    assert "dpdk-test-crypto-perf" in resp["cmd_sh"]


def test_compare_runs() -> None:
    server = MCPServer()
    resp = server.compare_runs(
        {
            "benchmark": "testpmd",
            "baseline_metrics": {"rx_pps": 100.0},
            "candidate_metrics": {"rx_pps": 110.0},
        }
    )
    assert "rx_pps" in resp["delta"]
