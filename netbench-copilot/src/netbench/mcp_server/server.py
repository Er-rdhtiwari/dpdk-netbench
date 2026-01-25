from __future__ import annotations

from netbench.config import settings
from netbench.mcp_server.schemas import (
    BuildDatasetRequest,
    BuildDatasetResponse,
    CompareRunsRequest,
    CompareRunsResponse,
    ExplainMetricRequest,
    ExplainMetricResponse,
    ParseResultsRequest,
    ParseResultsResponse,
    RenderCommandRequest,
    RenderCommandResponse,
    ValidatePlanRequest,
    ValidatePlanResponse,
)
from netbench.mcp_server.tools import (
    build_dataset_tool,
    compare_runs_tool,
    explain_metric_tool,
    parse_results_tool,
    render_command_tool,
    validate_plan_tool,
)


class MCPServer:
    def render_command(self, request: dict) -> dict:
        parsed = RenderCommandRequest.model_validate(request)
        response = render_command_tool(parsed.benchmark, parsed.run_yaml, parsed.scenario_key)
        return RenderCommandResponse.model_validate(response).model_dump()

    def parse_results(self, request: dict) -> dict:
        parsed = ParseResultsRequest.model_validate(request)
        response = parse_results_tool(parsed.benchmark, parsed.log_paths)
        return ParseResultsResponse.model_validate(response).model_dump()

    def compare_runs(self, request: dict) -> dict:
        parsed = CompareRunsRequest.model_validate(request)
        response = compare_runs_tool(
            parsed.benchmark, parsed.baseline_metrics, parsed.candidate_metrics
        )
        return CompareRunsResponse.model_validate(response).model_dump()

    def validate_plan(self, request: dict) -> dict:
        parsed = ValidatePlanRequest.model_validate(request)
        response = validate_plan_tool(parsed.run_yaml, parsed.tuning_profile, parsed.env_snapshot)
        return ValidatePlanResponse.model_validate(response).model_dump()

    def build_dataset(self, request: dict) -> dict:
        parsed = BuildDatasetRequest.model_validate(request)
        response = build_dataset_tool(parsed.db_path, parsed.out_dir)
        return BuildDatasetResponse.model_validate(response).model_dump()

    def explain_metric(self, request: dict) -> dict:
        parsed = ExplainMetricRequest.model_validate(request)
        response = explain_metric_tool(parsed.metric_name, settings.index_dir)
        return ExplainMetricResponse.model_validate(response).model_dump()
