from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError, Field

from netbench.tuning.rules import rule_checks


class RunScenario(BaseModel):
    name: str
    params: dict = Field(default_factory=dict)


class RunPlan(BaseModel):
    benchmark: str
    platform: str
    scenarios: dict[str, dict]
    eal: dict
    logging: dict
    env_snapshot_cmds: list[str]


class TuningProfile(BaseModel):
    hugepages: str
    irq_affinity: str
    isolcpus: str
    disable_irqbalance: str
    disable_thp: str
    kernel_cmdline: str
    bios: str
    verification_cmds: list[str]
    requires_approval: bool = False


def validate_plan(run_yaml: dict, tuning_profile: dict, env_snapshot: dict) -> tuple[bool, list[str], list[str]]:
    reasons: list[str] = []
    fixes: list[str] = []

    try:
        RunPlan.model_validate(run_yaml)
    except ValidationError as exc:
        reasons.append(str(exc))
    try:
        TuningProfile.model_validate(tuning_profile)
    except ValidationError as exc:
        reasons.append(str(exc))

    warnings = rule_checks(run_yaml, tuning_profile, env_snapshot)
    if warnings:
        fixes.extend(warnings)

    return len(reasons) == 0, reasons, fixes
