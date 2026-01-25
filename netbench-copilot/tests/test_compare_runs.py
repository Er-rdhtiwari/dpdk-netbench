from __future__ import annotations

from netbench.mcp_server.tools import compare_runs_tool


def test_compare_delta() -> None:
    resp = compare_runs_tool("testpmd", {"rx_pps": 100.0}, {"rx_pps": 150.0})
    assert resp["delta"]["rx_pps"]["diff"] == 50.0
