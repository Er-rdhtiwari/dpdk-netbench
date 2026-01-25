from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RunRecord(BaseModel):
    run_id: str
    benchmark: str
    platform: str
    nl_goal: str | None = None
    run_yaml: str | None = None
    tuning_profile: str | None = None
    cmd_sh: str | None = None
    metrics_json: str | None = None
    summary_md: str | None = None
    citations_json: str | None = None
    env_snapshot: str | None = None
    log_snippet: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
