from __future__ import annotations

from pathlib import Path
from typing import Any

from netbench.benchmarks.cryptoperf import CryptoPerfAdapter
from netbench.benchmarks.l2fwd import L2FwdAdapter
from netbench.benchmarks.l3fwd import L3FwdAdapter
from netbench.benchmarks.testpmd import TestPmdAdapter
from netbench.dataset.export import export_dataset
from netbench.kb.citations import build_citations
from netbench.kb.retrieve import load_retriever
from netbench.tuning.validators import validate_plan


def get_adapter(benchmark: str):
    name = benchmark.lower()
    if name == "cryptoperf":
        return CryptoPerfAdapter()
    if name == "testpmd":
        return TestPmdAdapter()
    if name == "l3fwd":
        return L3FwdAdapter()
    if name == "l2fwd":
        return L2FwdAdapter()
    raise ValueError(f"Unknown benchmark: {benchmark}")


def render_command_tool(benchmark: str, run_yaml: dict, scenario_key: str) -> dict:
    adapter = get_adapter(benchmark)
    cmd_lines = adapter.render_command(run_yaml, scenario_key)
    cmd_sh = "#!/usr/bin/env bash\nset -euo pipefail\n\n" + "\n".join(cmd_lines) + "\n"
    return {"cmd_lines": cmd_lines, "cmd_sh": cmd_sh}


def parse_results_tool(benchmark: str, log_paths: list[str]) -> dict:
    adapter = get_adapter(benchmark)
    metrics, warnings = adapter.parse_results(log_paths)
    return {"metrics": metrics, "parse_warnings": warnings}


def compare_runs_tool(benchmark: str, baseline_metrics: dict, candidate_metrics: dict) -> dict:
    delta: dict[str, Any] = {}
    summary_lines = [f"# {benchmark} comparison", ""]
    for key, base_val in baseline_metrics.items():
        cand_val = candidate_metrics.get(key)
        if isinstance(base_val, (int, float)) and isinstance(cand_val, (int, float)):
            diff = cand_val - base_val
            pct = (diff / base_val * 100.0) if base_val else 0.0
            delta[key] = {"baseline": base_val, "candidate": cand_val, "diff": diff, "pct": pct}
            summary_lines.append(
                f"- {key}: {base_val} -> {cand_val} (diff {diff:.3f}, {pct:.2f}%)"
            )
        else:
            delta[key] = {"baseline": base_val, "candidate": cand_val}
    summary_md = "\n".join(summary_lines) + "\n"
    return {"delta": delta, "summary_md": summary_md}


def validate_plan_tool(run_yaml: dict, tuning_profile: dict, env_snapshot: dict) -> dict:
    valid, reasons, fixes = validate_plan(run_yaml, tuning_profile, env_snapshot)
    return {"valid": valid, "reasons": reasons, "suggested_fixes": fixes}


def build_dataset_tool(db_path: str, out_dir: str) -> dict:
    result = export_dataset(Path(db_path), Path(out_dir))
    return {
        "sft_train": str(result["sft_train"]),
        "sft_val": str(result["sft_val"]),
        "eval_cases": str(result["eval_cases"]),
    }


def explain_metric_tool(metric_name: str, index_dir: Path) -> dict:
    retriever = load_retriever(index_dir)
    chunks = retriever.retrieve(f"METRIC {metric_name}", top_k=3)
    citations = build_citations(chunks)
    if not citations:
        return {"answer": "NOT FOUND IN KB", "citations": []}
    # deterministic answer: first chunk text line containing the metric name
    answer = "NOT FOUND IN KB"
    for chunk in chunks:
        if metric_name.lower() in chunk.text.lower():
            answer = chunk.text.strip().split("\n")[0]
            break
    return {
        "answer": answer,
        "citations": [c.__dict__ for c in citations],
    }
