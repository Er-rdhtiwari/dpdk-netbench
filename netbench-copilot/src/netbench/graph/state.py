from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class GraphState(BaseModel):
    intent: Literal["ask", "plan", "parse", "compare", "dataset", "eval", "explain"] | None = None
    query: str | None = None
    benchmark: str | None = None
    platform: str | None = None
    nl_goal: str | None = None

    retrieved_chunks: list[dict] = Field(default_factory=list)
    citations: list[dict] = Field(default_factory=list)

    run_plan: dict | None = None
    tuning_profile: dict | None = None
    cmd_sh: str | None = None

    metrics: dict | None = None
    delta: dict | None = None
    summary_md: str | None = None

    requires_approval: bool = False
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    extra: dict[str, Any] = Field(default_factory=dict)
