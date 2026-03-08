from __future__ import annotations

import re
from typing import Iterable

from netbench.tuning.envprobe import env_snapshot_commands


def _iter_lines(retrieved: Iterable[dict]) -> Iterable[str]:
    for chunk in retrieved:
        text = chunk.get("text") if isinstance(chunk, dict) else getattr(chunk, "text", "")
        for line in (text or "").splitlines():
            line = line.strip()
            if line:
                yield line


def _extract_prefixed(prefix: str, retrieved: Iterable[dict]) -> str | None:
    prefix_upper = prefix.upper()
    for line in _iter_lines(retrieved):
        if line.upper().startswith(prefix_upper):
            parts = line.split(":", 1)
            if len(parts) == 2:
                return parts[1].strip()
    return None


def _extract_all(prefix: str, retrieved: Iterable[dict]) -> list[str]:
    items: list[str] = []
    prefix_upper = prefix.upper()
    for line in _iter_lines(retrieved):
        if line.upper().startswith(prefix_upper):
            parts = line.split(":", 1)
            if len(parts) == 2:
                items.append(parts[1].strip())
    return items


def _infer_scenarios(benchmark: str, nl_goal: str) -> dict[str, dict]:
    nl = nl_goal.lower()
    scenarios: dict[str, dict] = {}
    if benchmark == "cryptoperf":
        algo = "aes-gcm" if "aes" in nl else "null"
        cores = re.findall(r"(\d+)\s*cores?", nl)
        scenario = {
            "algorithm": algo,
            "burst_size": 32,
            "total_ops": 1000000,
            "core_count": int(cores[0]) if cores else 4,
        }
        scenarios["scenario_001"] = scenario
    elif benchmark == "testpmd":
        frame_sizes = re.findall(r"(\d{2,4})b", nl)
        sizes = [int(s) for s in frame_sizes] or [64]
        for idx, size in enumerate(sizes, start=1):
            scenarios[f"scenario_{idx:03d}"] = {
                "frame_size": size,
                "forward_mode": "io",
            }
    else:
        scenarios["scenario_001"] = {"port_mask": "0x3"}
    return scenarios


def _llm_refine_scenarios(benchmark: str, nl_goal: str, scenarios: dict[str, dict]) -> dict[str, dict]:
    # Deterministic placeholder: real LLM integration can replace this.
    return scenarios


def build_run_plan(benchmark: str, platform: str, nl_goal: str) -> dict:
    scenarios = _infer_scenarios(benchmark, nl_goal)
    scenarios = _llm_refine_scenarios(benchmark, nl_goal, scenarios)
    return {
        "benchmark": benchmark,
        "platform": platform,
        "nl_goal": nl_goal,
        "scenarios": scenarios,
        "eal": {
            "core_list": "0-3",
            "socket_mem": "1024",
            "file_prefix": "nb",
            "allowlist": ["0000:00:00.0"],
        },
        "logging": {"stdout": "logs/stdout.txt"},
        "env_snapshot_cmds": env_snapshot_commands(),
    }


def build_tuning_profile(retrieved: list[dict]) -> tuple[dict | None, list[str]]:
    errors: list[str] = []

    hugepages = _extract_prefixed("HUGEPAGES", retrieved)
    irq_affinity = _extract_prefixed("IRQ_AFFINITY", retrieved)
    isolcpus = _extract_prefixed("ISOLCPUS", retrieved)
    disable_irqbalance = _extract_prefixed("DISABLE_IRQBALANCE", retrieved)
    disable_thp = _extract_prefixed("DISABLE_THP", retrieved)
    kernel_cmdline = _extract_prefixed("KERNEL_CMDLINE", retrieved)
    bios = _extract_prefixed("BIOS", retrieved)
    verification_cmds = _extract_all("VERIFY_CMD", retrieved)

    required = [
        ("HUGEPAGES", hugepages),
        ("IRQ_AFFINITY", irq_affinity),
        ("ISOLCPUS", isolcpus),
        ("DISABLE_IRQBALANCE", disable_irqbalance),
        ("DISABLE_THP", disable_thp),
        ("KERNEL_CMDLINE", kernel_cmdline),
        ("BIOS", bios),
    ]
    missing = [name for name, value in required if not value]
    if missing:
        errors.append("NOT FOUND IN KB")
        return None, errors

    tuning_profile = {
        "hugepages": hugepages,
        "irq_affinity": irq_affinity,
        "isolcpus": isolcpus,
        "disable_irqbalance": disable_irqbalance,
        "disable_thp": disable_thp,
        "kernel_cmdline": kernel_cmdline,
        "bios": bios,
        "verification_cmds": verification_cmds,
        "requires_approval": "requires reboot" in bios.lower(),
    }
    return tuning_profile, errors


def build_plan_and_tuning(
    benchmark: str,
    platform: str,
    nl_goal: str,
    retrieved: list[dict],
) -> tuple[dict | None, dict | None, list[str]]:
    run_plan = build_run_plan(benchmark, platform, nl_goal)
    tuning_profile, errors = build_tuning_profile(retrieved)
    if errors:
        return None, None, errors
    return run_plan, tuning_profile, errors
