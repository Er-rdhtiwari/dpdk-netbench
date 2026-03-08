from __future__ import annotations

import json
import time
from pathlib import Path
import typer
from rich import print
import structlog
import yaml

from netbench.config import settings
from netbench.dataset.export import export_dataset
from netbench.eval.harness import run_eval
from netbench.kb.citations import build_citations, write_citations, citations_summary
from netbench.kb.ingest import build_index
from netbench.kb.retrieve import load_retriever
from netbench.mcp_server.server import MCPServer
from netbench.tools.langchain_tools import render_command_tool
from netbench.store.db import fetch_run, init_db, insert_run
from netbench.store.models import RunRecord
from netbench.tuning.advisor import build_plan_and_tuning

app = typer.Typer(help="NetBench Copilot CLI")


def setup_logging() -> None:
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
        processors=[structlog.processors.JSONRenderer()],
    )


def _run_id(prefix: str) -> str:
    return f"{prefix}-{int(time.time())}"


@app.command()
def index() -> None:
    """Build the KB index from PDFs."""
    setup_logging()
    stats = build_index(settings.kb_manifest, settings.kb_pdfs_dir, settings.index_dir)
    print(f"Indexed {stats.docs} docs into {stats.chunks} chunks. manifest={stats.manifest_hash}")


@app.command()
def ask(query: str = typer.Option(..., "--query")) -> None:
    """Ask a KB-grounded question."""
    setup_logging()
    retriever = load_retriever(settings.index_dir)
    chunks = retriever.retrieve(query, top_k=4)
    citations = build_citations(chunks)
    run_id = _run_id("ask")
    out_dir = settings.out_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    citations_path = out_dir / "citations.json"

    if not citations:
        print("NOT FOUND IN KB")
        write_citations(citations_path, [])
        return
    write_citations(citations_path, citations)
    answer = chunks[0].text.split("\n")[0].strip()
    print(answer)
    print(f"Sources: {citations_summary(citations)}")


@app.command()
def plan(
    benchmark: str = typer.Option(..., "--benchmark"),
    platform: str = typer.Option(..., "--platform"),
    nl: str = typer.Option(..., "--nl"),
) -> None:
    """Plan a benchmark run."""
    setup_logging()
    retriever = load_retriever(settings.index_dir)
    tuning_query = (
        f\"{benchmark} tuning HUGEPAGES IRQ_AFFINITY ISOLCPUS DISABLE_IRQBALANCE \"\n        \"DISABLE_THP KERNEL_CMDLINE BIOS VERIFY_CMD\"\n+    )
    chunks = retriever.retrieve(tuning_query, top_k=6)
    citations = build_citations(chunks)
    run_id = _run_id("plan")
    out_dir = settings.out_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    run_yaml_path = out_dir / "run.yaml"
    tuning_path = out_dir / "tuning_profile.yaml"
    plan_json_path = out_dir / "plan.json"
    citations_path = out_dir / "citations.json"
    write_citations(citations_path, citations)

    if not citations:
        print("NOT FOUND IN KB")
        return

    retrieved = [{"text": c.text} for c in chunks]
    run_plan, tuning_profile, errors = build_plan_and_tuning(benchmark, platform, nl, retrieved)
    if errors:
        print("NOT FOUND IN KB")
        return

    run_yaml_path.write_text(yaml.safe_dump(run_plan, sort_keys=False), encoding="utf-8")
    tuning_path.write_text(yaml.safe_dump(tuning_profile, sort_keys=False), encoding="utf-8")
    plan_json_path.write_text(
        json.dumps({"run": run_plan, "tuning": tuning_profile}, indent=2), encoding="utf-8"
    )

    server = MCPServer()
    validation = server.validate_plan(
        {"run_yaml": run_plan, "tuning_profile": tuning_profile, "env_snapshot": {}}
    )
    if not validation.get("valid", False):
        print("Plan validation failed:")
        for reason in validation.get("reasons", []):
            print(f"- {reason}")
        return

    if tuning_profile.get("requires_approval") and not settings.approval_token:
        print("Approval token required for BIOS/reboot steps. Set NETBENCH_APPROVAL_TOKEN.")
        record = RunRecord(
            run_id=run_id,
            benchmark=benchmark,
            platform=platform,
            nl_goal=nl,
            run_yaml=run_yaml_path.read_text(encoding="utf-8"),
            tuning_profile=tuning_path.read_text(encoding="utf-8"),
            citations_json=citations_path.read_text(encoding="utf-8"),
        )
        insert_run(settings.db_path, record)
        return

    cmd_resp = render_command_tool.invoke(
        {
            "benchmark": benchmark,
            "run_yaml": run_plan,
            "scenario_key": list(run_plan["scenarios"].keys())[0],
        }
    )
    cmd_path = out_dir / "cmd.sh"
    cmd_path.write_text(cmd_resp["cmd_sh"], encoding="utf-8")

    record = RunRecord(
        run_id=run_id,
        benchmark=benchmark,
        platform=platform,
        nl_goal=nl,
        run_yaml=run_yaml_path.read_text(encoding="utf-8"),
        tuning_profile=tuning_path.read_text(encoding="utf-8"),
        cmd_sh=cmd_path.read_text(encoding="utf-8"),
        citations_json=citations_path.read_text(encoding="utf-8"),
    )
    insert_run(settings.db_path, record)

    print(f"Wrote plan to {out_dir}")
    print(f"Sources: {citations_summary(citations)}")


@app.command()
def parse(
    benchmark: str = typer.Option(..., "--benchmark"),
    run_dir: Path = typer.Option(..., "--run-dir"),
    store: bool = typer.Option(False, "--store"),
) -> None:
    """Parse benchmark logs."""
    setup_logging()
    server = MCPServer()
    log_path = run_dir / "logs/stdout.txt"
    resp = server.parse_results({"benchmark": benchmark, "log_paths": [str(log_path)]})

    run_id = _run_id("run")
    out_dir = settings.out_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(resp["metrics"], indent=2), encoding="utf-8")

    if store:
        env_snapshot = ""
        env_dir = run_dir / "env"
        if env_dir.exists():
            for path in sorted(env_dir.glob("*.txt")):
                env_snapshot += f"## {path.name}\n{path.read_text(encoding='utf-8')}\n"
        log_text = log_path.read_text(encoding="utf-8")
        log_snippet = log_text[:2000]
        record = RunRecord(
            run_id=run_id,
            benchmark=benchmark,
            platform="unknown",
            metrics_json=json.dumps(resp["metrics"], indent=2),
            env_snapshot=env_snapshot,
            log_snippet=log_snippet,
        )
        insert_run(settings.db_path, record)

    print(f"metrics written to {metrics_path}")
    print(f"RUN_ID={run_id}")


@app.command()
def compare(
    baseline: str = typer.Option(..., "--baseline"),
    candidate: str = typer.Option(..., "--candidate"),
) -> None:
    """Compare two stored runs."""
    setup_logging()
    init_db(settings.db_path)
    base = fetch_run(settings.db_path, baseline)
    cand = fetch_run(settings.db_path, candidate)
    if not base or not cand:
        raise SystemExit("Run IDs not found in DB")

    server = MCPServer()
    resp = server.compare_runs(
        {
            "benchmark": base.benchmark,
            "baseline_metrics": json.loads(base.metrics_json or "{}"),
            "candidate_metrics": json.loads(cand.metrics_json or "{}"),
        }
    )

    run_id = _run_id("compare")
    out_dir = settings.out_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "delta.json").write_text(json.dumps(resp["delta"], indent=2), encoding="utf-8")
    (out_dir / "summary.md").write_text(resp["summary_md"], encoding="utf-8")

    compare_metrics = {
        "baseline": json.loads(base.metrics_json or "{}"),
        "candidate": json.loads(cand.metrics_json or "{}"),
        "delta": resp["delta"],
    }
    record = RunRecord(
        run_id=run_id,
        benchmark=base.benchmark,
        platform=base.platform,
        metrics_json=json.dumps(compare_metrics, indent=2),
        summary_md=resp["summary_md"],
    )
    insert_run(settings.db_path, record)

    print(f"Comparison written to {out_dir}")


dataset_app = typer.Typer()
app.add_typer(dataset_app, name="dataset")


dataset_app.command("export")
def dataset_export(out: Path = typer.Option(..., "--out")) -> None:
    setup_logging()
    server = MCPServer()
    resp = server.build_dataset({"db_path": str(settings.db_path), "out_dir": str(out)})
    print(json.dumps(resp, indent=2))


eval_app = typer.Typer()
app.add_typer(eval_app, name="eval")


eval_app.command("run")
def eval_run(cases: Path = typer.Option(..., "--cases")) -> None:
    setup_logging()
    report = run_eval(cases, settings.out_dir)
    print(json.dumps(report, indent=2))


finetune_app = typer.Typer()
app.add_typer(finetune_app, name="finetune")


@finetune_app.command("lora")
def finetune_lora(
    dataset: Path = typer.Option(..., "--dataset"),
    val: Path = typer.Option(..., "--val"),
) -> None:
    setup_logging()
    from netbench.finetune.train_lora import run_lora

    run_lora(dataset, val, settings.model_id, settings.out_dir)


if __name__ == "__main__":
    app()
