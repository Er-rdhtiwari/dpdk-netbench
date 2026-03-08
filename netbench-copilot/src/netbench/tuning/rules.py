from __future__ import annotations


def rule_checks(run_yaml: dict, tuning_profile: dict, env_snapshot: dict) -> list[str]:
    warnings: list[str] = []
    if "eal" in run_yaml and not run_yaml["eal"].get("core_list"):
        warnings.append("EAL core_list is empty")
    if tuning_profile.get("disable_thp") and "transparent_hugepage" in str(env_snapshot).lower():
        # This is a placeholder rule for demo purposes.
        warnings.append("Verify THP is disabled on the target system")
    return warnings
