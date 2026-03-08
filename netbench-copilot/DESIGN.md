# Design

## LangGraph State Machine

```
[classify_intent] -> [retrieve_kb] -> [build_plan] -> [apply_tuning_advisor]
        -> [validate] -> [safety_gate] -> [tool_execute] -> [finalize_response]
```

## Data Model

- run.yaml: benchmark, platform, scenarios, EAL options, logging, env snapshot commands
- tuning_profile.yaml: hugepages, IRQ affinity, isolcpus/nohz_full/rcu_nocbs guidance, BIOS notes, verification commands
- metrics.json: normalized outputs per benchmark
- citations.json: doc_id, chunk_id, source_file, page_start/end, section

## Tool Contracts (MCP)

- render_command: run.yaml + scenario key -> cmd.sh
- parse_results: benchmark + log paths -> metrics.json
- compare_runs: baseline + candidate metrics -> delta.json + summary.md
- validate_plan: run.yaml + tuning_profile + env snapshot -> valid/invalid + fixes
- build_dataset: SQLite DB -> SFT JSONL + eval cases
- explain_metric: metric name -> KB-grounded definition + citations

## Reasoning Boundaries

- KB is the source of truth for tuning recommendations, methodology, and metric definitions.
- If the KB does not support a claim, the system must return `NOT FOUND IN KB`.
- Deterministic MCP tools are the only source of command/script outputs.
