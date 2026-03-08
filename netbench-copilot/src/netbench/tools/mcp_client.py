from __future__ import annotations

from netbench.mcp_server.server import MCPServer


class MCPClient:
    def __init__(self) -> None:
        self.server = MCPServer()

    def render_command(self, request: dict) -> dict:
        return self.server.render_command(request)

    def parse_results(self, request: dict) -> dict:
        return self.server.parse_results(request)

    def compare_runs(self, request: dict) -> dict:
        return self.server.compare_runs(request)

    def validate_plan(self, request: dict) -> dict:
        return self.server.validate_plan(request)

    def build_dataset(self, request: dict) -> dict:
        return self.server.build_dataset(request)

    def explain_metric(self, request: dict) -> dict:
        return self.server.explain_metric(request)
