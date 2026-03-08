from __future__ import annotations

from netbench.tuning.advisor import build_plan_and_tuning


def test_plan_requires_kb() -> None:
    run_plan, tuning_profile, errors = build_plan_and_tuning(
        "cryptoperf", "generic", "AES-GCM", retrieved=[]
    )
    assert errors == ["NOT FOUND IN KB"]
    assert run_plan is None
    assert tuning_profile is None
