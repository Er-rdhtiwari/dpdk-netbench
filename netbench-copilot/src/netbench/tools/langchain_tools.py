from __future__ import annotations

from langchain_core.tools import tool

from netbench.tools.mcp_client import MCPClient


@tool
def render_command_tool(benchmark: str, run_yaml: dict, scenario_key: str) -> dict:
    """Deterministic MCP-backed command renderer."""
    return MCPClient().render_command(
        {"benchmark": benchmark, "run_yaml": run_yaml, "scenario_key": scenario_key}
    )
