from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RenderCommandRequest(BaseModel):
    benchmark: str
    run_yaml: dict
    scenario_key: str


class RenderCommandResponse(BaseModel):
    cmd_lines: list[str]
    cmd_sh: str


class ParseResultsRequest(BaseModel):
    benchmark: str
    log_paths: list[str]


class ParseResultsResponse(BaseModel):
    metrics: dict
    parse_warnings: list[str] = Field(default_factory=list)


class CompareRunsRequest(BaseModel):
    benchmark: str
    baseline_metrics: dict
    candidate_metrics: dict


class CompareRunsResponse(BaseModel):
    delta: dict
    summary_md: str


class ValidatePlanRequest(BaseModel):
    run_yaml: dict
    tuning_profile: dict
    env_snapshot: dict


class ValidatePlanResponse(BaseModel):
    valid: bool
    reasons: list[str] = Field(default_factory=list)
    suggested_fixes: list[str] = Field(default_factory=list)


class BuildDatasetRequest(BaseModel):
    db_path: str
    out_dir: str


class BuildDatasetResponse(BaseModel):
    sft_train: str
    sft_val: str
    eval_cases: str


class ExplainMetricRequest(BaseModel):
    metric_name: str


class ExplainMetricResponse(BaseModel):
    answer: str
    citations: list[dict] = Field(default_factory=list)
