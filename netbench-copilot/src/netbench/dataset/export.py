from __future__ import annotations

import hashlib
import json
from pathlib import Path

from netbench.dataset.redact import redact
from netbench.dataset.templates import COMPARE_TEMPLATE, PARSE_TEMPLATE, PLAN_TEMPLATE, SYSTEM_PROMPT
from netbench.store.db import list_runs


def _bucket(run_id: str) -> str:
    h = hashlib.sha256(run_id.encode("utf-8")).hexdigest()
    val = int(h[:2], 16) / 255.0
    if val < 0.8:
        return "train"
    if val < 0.9:
        return "val"
    return "test"


def export_dataset(db_path: Path, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    records = list_runs(db_path)
    run_records_path = out_dir / "run_records.jsonl"

    sft_train = out_dir / "sft_train.jsonl"
    sft_val = out_dir / "sft_val.jsonl"
    sft_test = out_dir / "sft_test.jsonl"

    with run_records_path.open("w", encoding="utf-8") as run_f, \
        sft_train.open("w", encoding="utf-8") as train_f, \
        sft_val.open("w", encoding="utf-8") as val_f, \
        sft_test.open("w", encoding="utf-8") as test_f:
        for record in records:
            payload = record.model_dump()
            if payload.get("env_snapshot"):
                payload["env_snapshot"] = redact(payload["env_snapshot"])
            if payload.get("nl_goal"):
                payload["nl_goal"] = redact(payload["nl_goal"])
            if payload.get("log_snippet"):
                payload["log_snippet"] = redact(payload["log_snippet"])
            run_f.write(json.dumps(payload) + "\n")

            bucket = _bucket(record.run_id)
            target = train_f if bucket == "train" else val_f if bucket == "val" else test_f

            if record.run_yaml and record.tuning_profile and record.nl_goal:
                env_summary = (record.env_snapshot or "")[:200]
                user_msg = PLAN_TEMPLATE.format(
                    nl_goal=redact(record.nl_goal), env_summary=redact(env_summary)
                )
                assistant_msg = f"run.yaml\n{record.run_yaml}\n\n\n" \
                    f"tuning_profile.yaml\n{record.tuning_profile}\n"
                example = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": assistant_msg},
                    ]
                }
                target.write(json.dumps(example) + "\n")

            if record.metrics_json and record.log_snippet:
                snippet = redact(record.log_snippet or "<log snippet unavailable>")
                user_msg = PARSE_TEMPLATE.format(log_snippet=snippet)
                example = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": record.metrics_json},
                    ]
                }
                target.write(json.dumps(example) + "\n")

            if record.summary_md and record.metrics_json:
                try:
                    metrics_payload = json.loads(record.metrics_json)
                except json.JSONDecodeError:
                    metrics_payload = {}
                baseline = metrics_payload.get("baseline", record.metrics_json)
                candidate = metrics_payload.get("candidate", record.metrics_json)
                user_msg = COMPARE_TEMPLATE.format(
                    baseline=json.dumps(baseline), candidate=json.dumps(candidate)
                )
                example = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": record.summary_md},
                    ]
                }
                target.write(json.dumps(example) + "\n")

    eval_cases_path = out_dir / "eval_cases.json"
    golden = Path("data/golden_prompts/eval_cases.yaml")
    if golden.exists():
        import yaml

        eval_cases = yaml.safe_load(golden.read_text(encoding="utf-8")) or []
    else:
        eval_cases = []
    eval_cases_path.write_text(json.dumps({"cases": eval_cases}, indent=2), encoding="utf-8")

    return {
        "run_records": run_records_path,
        "sft_train": sft_train,
        "sft_val": sft_val,
        "sft_test": sft_test,
        "eval_cases": eval_cases_path,
    }
