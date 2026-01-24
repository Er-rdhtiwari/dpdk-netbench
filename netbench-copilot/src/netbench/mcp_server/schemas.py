"""Pydantic schemas for MCP tool requests and responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Tool A: render_command
class RenderCommandRequest(BaseModel):
    """Request schema for render_command tool."""

    benchmark: str = Field(description="Benchmark name (cryptoperf, testpmd, l3fwd, l2fwd)")
    run_yaml_content: str = Field(description="Content of run.yaml")
    scenario_key: str = Field(description="Scenario key to render from run.yaml")


class RenderCommandResponse(BaseModel):
    """Response schema for render_command tool."""

    success: bool = Field(description="Whether command rendering succeeded")
    cmd_sh_content: str = Field(description="Generated command script content")
    command_lines: List[str] = Field(description="Individual command lines")
    errors: Optional[List[str]] = Field(default=None, description="Errors encountered")


# Tool B: parse_results
class ParseResultsRequest(BaseModel):
    """Request schema for parse_results tool."""

    benchmark: str = Field(description="Benchmark name")
    log_paths: List[str] = Field(description="Paths to log files to parse")


class ParseResultsResponse(BaseModel):
    """Response schema for parse_results tool."""

    success: bool = Field(description="Whether parsing succeeded")
    metrics_json: str = Field(description="Normalized metrics JSON content")
    parse_warnings: List[str] = Field(default_factory=list, description="Parsing warnings")
    errors: Optional[List[str]] = Field(default=None, description="Errors encountered")


# Tool C: compare_runs
class CompareRunsRequest(BaseModel):
    """Request schema for compare_runs tool."""

    baseline_metrics_json: str = Field(description="Baseline metrics JSON content")
    candidate_metrics_json: str = Field(description="Candidate metrics JSON content")
    benchmark: str = Field(description="Benchmark name for context")


class CompareRunsResponse(BaseModel):
    """Response schema for compare_runs tool."""

    success: bool = Field(description="Whether comparison succeeded")
    delta_json: str = Field(description="Delta metrics JSON content")
    summary_md: str = Field(description="Summary markdown content")
    significant_changes: List[str] = Field(
        default_factory=list, description="List of significant changes"
    )
    errors: Optional[List[str]] = Field(default=None, description="Errors encountered")


# Tool D: validate_plan
class ValidatePlanRequest(BaseModel):
    """Request schema for validate_plan tool."""

    run_yaml_content: str = Field(description="Content of run.yaml")
    tuning_profile_yaml_content: str = Field(description="Content of tuning_profile.yaml")
    env_snapshot: Dict[str, Any] = Field(description="Environment snapshot data")


class ValidatePlanResponse(BaseModel):
    """Response schema for validate_plan tool."""

    valid: bool = Field(description="Whether plan is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggested_fixes: List[str] = Field(default_factory=list, description="Suggested fixes")


# Tool E: build_dataset
class BuildDatasetRequest(BaseModel):
    """Request schema for build_dataset tool."""

    db_path: str = Field(description="Path to SQLite database")
    output_dir: str = Field(description="Output directory for dataset files")
    train_split: float = Field(default=0.8, description="Training split ratio")
    val_split: float = Field(default=0.1, description="Validation split ratio")
    test_split: float = Field(default=0.1, description="Test split ratio")
    redact: bool = Field(default=True, description="Whether to redact sensitive data")


class BuildDatasetResponse(BaseModel):
    """Response schema for build_dataset tool."""

    success: bool = Field(description="Whether dataset building succeeded")
    train_path: str = Field(description="Path to training JSONL file")
    val_path: str = Field(description="Path to validation JSONL file")
    test_path: str = Field(description="Path to test JSONL file")
    eval_cases_path: str = Field(description="Path to eval cases JSON file")
    record_counts: Dict[str, int] = Field(description="Record counts per split")
    errors: Optional[List[str]] = Field(default=None, description="Errors encountered")


# Tool F: explain_metric
class ExplainMetricRequest(BaseModel):
    """Request schema for explain_metric tool."""

    metric_name: str = Field(description="Name of metric to explain")
    benchmark: Optional[str] = Field(default=None, description="Benchmark context")


class ExplainMetricResponse(BaseModel):
    """Response schema for explain_metric tool."""

    success: bool = Field(description="Whether explanation succeeded")
    explanation: str = Field(description="Metric explanation (or NOT FOUND IN KB)")
    citations_json: Optional[str] = Field(
        default=None, description="Citations JSON if found in KB"
    )
    errors: Optional[List[str]] = Field(default=None, description="Errors encountered")

# Made with Bob
