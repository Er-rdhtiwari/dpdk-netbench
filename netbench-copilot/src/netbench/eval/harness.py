from __future__ import annotations

import json
from pathlib import Path

import yaml

from netbench.config import settings
from netbench.eval.metrics import rubric
from netbench.kb.citations import build_citations
from netbench.kb.retrieve import load_retriever
from netbench.mcp_server.server import MCPServer
from netbench.tuning.advisor import build_plan_and_tuning


def run_eval(cases_path: Path, out_dir: Path) -> dict:
    cases = yaml.safe_load(cases_path.read_text(encoding="utf-8")) or []
    results = []
    server = MCPServer()
    retriever = load_retriever(settings.index_dir)

    for case in cases:
        ctype = case.get("type")
        passed = False

        if ctype == "ask":
            query = case.get("query", "")
            chunks = retriever.retrieve(query, top_k=3)
            citations = build_citations(chunks)
            answer = "NOT FOUND IN KB" if not citations else chunks[0].text.lower()
            if case.get("expect") == "NOT_FOUND":
                passed = answer == "NOT FOUND IN KB"
            elif "expect_contains" in case:
                expected = case["expect_contains"][0].lower()
                passed = expected in answer

        if ctype == "plan":
            tuning_query = (
                f"{case.get('benchmark')} tuning HUGEPAGES IRQ_AFFINITY ISOLCPUS DISABLE_IRQBALANCE "
                "DISABLE_THP KERNEL_CMDLINE BIOS VERIFY_CMD"
            )
            retrieved = [{"text": c.text} for c in retriever.retrieve(tuning_query, top_k=6)]
            plan, tuning, errors = build_plan_and_tuning(
                case.get("benchmark"), case.get("platform"), case.get("nl"), retrieved
            )
            if errors or not plan or not tuning:
                passed = False
            else:
                validation = server.validate_plan(
                    {"run_yaml": plan, "tuning_profile": tuning, "env_snapshot": {}}
                )
                text = json.dumps(plan)
                expected = case.get("expect_contains", [""])[0]
                cmd_check = True
                kb_chunks = retriever.retrieve(case.get("benchmark", ""), top_k=3)
                kb_text = " ".join(c.text for c in kb_chunks).lower()
                cmd_resp = server.render_command(
                    {
                        "benchmark": plan.get("benchmark"),
                        "run_yaml": plan,
                        "scenario_key": list(plan.get("scenarios", {}).keys())[0],
                    }
                )
                cmd_sh = cmd_resp.get("cmd_sh", "").lower()
                expected_cmds = {
                    "cryptoperf": "dpdk-test-crypto-perf",
                    "testpmd": "testpmd",
                    "l3fwd": "l3fwd",
                    "l2fwd": "l2fwd",
                }
                bench = (plan.get("benchmark") or "").lower()
                required_cmd = expected_cmds.get(bench)
                if required_cmd and required_cmd in kb_text:
                    cmd_check = required_cmd in cmd_sh
                passed = expected in text and validation.get("valid", False) and cmd_check

        if ctype == "parse":
            resp = server.parse_results(
                {
                    "benchmark": case.get("benchmark"),
                    "log_paths": [str(Path(case.get("run_dir")) / "logs/stdout.txt")],
                }
            )
            metric = case.get("expect_metric")
            passed = metric in json.dumps(resp.get("metrics", {}))

        results.append({"id": case.get("id"), "passed": passed})

    summary = rubric([r["passed"] for r in results])
    report = {
        "total": summary.total,
        "passed": summary.passed,
        "score": summary.score,
        "results": results,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out_dir / "eval_report.md").write_text(
        f"# Eval Report\n\nScore: {summary.score:.2f}\n", encoding="utf-8"
    )
    return report
