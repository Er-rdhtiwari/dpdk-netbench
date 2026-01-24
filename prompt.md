You are “Codex”, an expert Senior AI Engineer + LLMOps engineer.

GOAL
Build a production-style PoC repository named:

  netbench-copilot

It is an AI-domain PoC implemented using:
- LlamaIndex (RAG indexing + retrieval)
- LangChain (LLM interface + tool calling glue)
- LangGraph (deterministic workflow orchestration)
- MCP (Model Context Protocol) (tool server boundary for deterministic tools)

Non-negotiables:
1) All factual claims (tuning recommendations, benchmark methodology, parameter meanings, metrics definitions) MUST be grounded in retrieved KB snippets; otherwise output exactly: “NOT FOUND IN KB”.
2) Any command/script content must be produced only via deterministic MCP tools with Pydantic schema validation (no free-form LLM command output).
3) BIOS changes / reboot steps are never executed automatically; they must be manual steps gated by NETBENCH_APPROVAL_TOKEN.

Use-case:
“NetBench Copilot” converts natural-language benchmark goals into:
1) a validated run plan (run.yaml)
2) a tuning profile (tuning_profile.yaml)
3) runnable command scripts (cmd.sh)
4) parsing of benchmark logs into normalized metrics (metrics.json)
5) comparison report (summary.md + delta.json)
6) dataset generation from stored run records (SFT JSONL + eval set)
7) optional LoRA fine-tuning pipeline + evaluation harness

BENCHMARKS IN SCOPE (must implement end-to-end):
A) CryptoPerf (DPDK crypto performance app / dpdk-test-crypto-perf)
B) testpmd (forwarding/perf mode)
C) L3 forwarding + L2 forwarding (l3fwd / l2fwd)

CRITICAL CONSTRAINTS
1) All “facts” about tuning recommendations, benchmark methodology, and parameter meanings MUST be grounded in the local KB PDFs (RAG). If not found in KB, the assistant must output: “NOT FOUND IN KB”.
2) Commands must be generated via deterministic tooling (MCP tools) + schema validation, not free-form LLM output.
3) Safety: BIOS changes / reboot are never executed automatically. They must be surfaced as “manual steps” with a safety gate requiring an explicit approval token in config.
4) Repo must be runnable locally with sample data (no external infra required).

REPO OUTPUT REQUIREMENTS
- Generate a complete repository with:
  - source code
  - tests
  - sample data
  - documentation
  - runbooks
  - Makefile
  - CI skeleton (GitHub Actions yaml)
  - strict formatting/lint config
- Everything must run end-to-end locally with a “demo” command.

LANGUAGE / STACK
- Python 3.11+
- Package manager: uv (preferred) OR poetry (choose ONE and be consistent)
- Use pydantic v2 + pydantic-settings for config.
- CLI: Typer
- Storage: SQLite (sqlite3) for run store + artifacts + dataset lineage
- Logging: structlog OR standard logging with JSON formatter (choose one)
- Testing: pytest
- Optional ML finetune: transformers + peft + bitsandbytes (keep optional; CPU-only path must still work)

PROJECT STRUCTURE (exact)
netbench-copilot/
  README.md
  LICENSE
  SECURITY.md
  DESIGN.md
  Makefile
  pyproject.toml
  .env.example
  .gitignore
  docs/
    runbook.md
    architecture.md
    safety.md
    evaluation.md
    dataset.md
    tuning.md
    benchmarks/
      cryptoperf.md
      testpmd.md
      l3fwd_l2fwd.md
  data/
    kb/
      pdfs/                # user will place PDFs here
      manifest.yaml        # list of PDFs + tags + version
    sample_runs/
      cryptoperf_run_001/  # sample logs + env snapshot
      testpmd_run_001/
      l3fwd_run_001/
    golden_prompts/
      plan_prompts.yaml
      ask_prompts.yaml
      eval_cases.yaml
  scripts/
    00_bootstrap.sh
    10_build_index.sh
    20_demo.sh
    30_add_pdf.sh
    40_export_dataset.sh
    50_run_eval.sh
    60_optional_finetune.sh
  src/
    netbench/
      __init__.py
      app.py                 # Typer CLI entry
      config.py              # pydantic-settings config
      kb/
        ingest.py            # LlamaIndex ingestion/index build
        retrieve.py          # retrieval wrapper
        citations.py         # citation packaging & enforcement
      graph/
        workflow.py          # LangGraph StateGraph
        state.py             # state schema
        policies.py          # safety/grounding policies
      tools/
        mcp_client.py        # MCP client wrapper
      mcp_server/
        server.py            # MCP server entry
        tools.py             # deterministic tools
        schemas.py           # tool request/response schemas
      benchmarks/
        base.py              # interface
        cryptoperf.py        # adapter: plan/render/parse
        testpmd.py
        l3fwd.py
        l2fwd.py
      tuning/
        advisor.py           # hybrid RAG + rules
        rules.py             # deterministic rule checks
        validators.py        # run plan validation
        envprobe.py          # collects env snapshot commands
      parsing/
        common.py
        cryptoperf_parser.py
        testpmd_parser.py
        l3fwd_parser.py
      store/
        db.py                # SQLite schema + access layer
        models.py            # DB models (pydantic)
      dataset/
        export.py            # run_records -> SFT JSONL + eval split
        redact.py            # hostname/ip redaction
        templates.py         # instruction templates
      eval/
        harness.py           # grounding + correctness evaluation
        metrics.py           # eval metrics + rubric scoring
      finetune/
        train_lora.py        # optional LoRA
        eval_lora.py         # compare base vs lora
  tests/
    test_kb_grounding.py
    test_plan_schema.py
    test_validators.py
    test_mcp_tools.py
    test_parsers_cryptoperf.py
    test_parsers_testpmd.py
    test_compare_runs.py
  .github/
    workflows/
      ci.yml

KB PDFs TO SUPPORT (user will provide locally)
- AMD EPYC DPDK tuning guides (multiple families)
- DPDK performance reports (Crypto report + NIC performance report PDFs)

IMPORTANT: Do NOT commit vendor PDFs into repo. Instead:
- Provide docs/runbook.md instructions for where to place PDFs under data/kb/pdfs/
- Provide data/kb/manifest.yaml format and scripts/30_add_pdf.sh to register PDFs.

FUNCTIONAL FEATURES (must implement)
1) RAG Indexing (LlamaIndex)
- Build a persistent local index from PDFs in data/kb/pdfs/
- Chunking:
  - Use heading-aware chunking if available; else fallback to fixed chunk + overlap
- Store metadata: filename, vendor, platform, version, benchmark tags (cryptoperf/testpmd/l3fwd), EPYC family tags (7003/8004/9004), release tags.
- Store metadata: source_file, page_start, page_end, and (if available) section/heading for each chunk.
- Output:
  - index stored under .cache/index/
  - manifest hash stored for reproducibility

2) Ask Mode (KB grounded Q&A)
CLI:
  python -m netbench.app ask --query "<question>"
Rules:
- Must retrieve top-k chunks
- Must output citations.json with doc ids + chunk ids
- citations.json must also include: source_file, page_start, page_end, and (if available) section/heading for each cited chunk; CLI output must show source_file + page_start-page_end.
- If answer requires info not found in retrieved chunks -> “NOT FOUND IN KB”

3) Plan Mode (NL -> run plan + tuning profile + commands)
CLI:
  python -m netbench.app plan --benchmark {cryptoperf|testpmd|l3fwd|l2fwd} --platform {epyc7003|epyc8004|epyc9004|generic} --nl "<goal>"
Outputs (written to ./out/<run_id>/):
- run.yaml (strict schema)
- tuning_profile.yaml (strict schema)
- cmd.sh (generated by MCP render_command tool)
- citations.json (must exist)
- citations.json must include source_file + page_start-page_end + doc ids + chunk ids; CLI output must show source_file + page_start-page_end.
- plan.json (full structured plan used)

Plan requirements:
- run.yaml includes:
  - benchmark name
  - platform
  - scenario matrix (frame sizes / algo sets / core counts etc)
  - EAL options structure
  - NIC allowlist placeholders
  - logging paths
  - env snapshot commands list (from envprobe)
- tuning_profile.yaml includes:
  - hugepages guidance
  - kernel cmdline suggestions
  - irq affinity guidance
  - isolcpus/nohz_full/rcu_nocbs guidance
  - disable irqbalance / THP suggestions
  - verification checklist commands

Safety gate:
- If tuning_profile includes BIOS changes or reboot recommendations:
  - add “requires_approval: true”
  - workflow must stop unless config provides NETBENCH_APPROVAL_TOKEN

4) MCP Tool Server (deterministic boundary)
Implement MCP server in src/netbench/mcp_server/server.py with tools:

Tool A: render_command(request) -> response
- Input: benchmark + run.yaml content + target scenario key
- Output: deterministic command line(s) + cmd.sh content
- Must be schema validated

Tool B: parse_results(request) -> response
- Input: benchmark + log paths
- Output: normalized metrics.json (schema)
- Must include “parse_warnings” list

Tool C: compare_runs(request) -> response
- Input: two metrics.json + context (benchmark)
- Output: delta.json + markdown summary

Tool D: validate_plan(request) -> response
- Input: run.yaml + tuning_profile.yaml + env_snapshot
- Output: valid/invalid + reasons + suggested fixes

Tool E: build_dataset(request) -> response
- Input: sqlite db path + export options
- Output: sft_train.jsonl, sft_val.jsonl, eval_cases.json

Tool F: explain_metric(request) -> response
- Input: metric_name
- Output: KB-grounded description with citations.json-style source_file + page_start-page_end + doc ids + chunk ids; if not found -> “NOT FOUND IN KB”
- Must be schema validated

5) Parse Mode
CLI:
  python -m netbench.app parse --benchmark testpmd --run-dir data/sample_runs/testpmd_run_001 --store true

- Must read sample logs in each sample_runs folder
- Must output metrics.json
- Must store a run record in SQLite when --store true

6) Compare Mode
CLI:
  python -m netbench.app compare --baseline <run_id> --candidate <run_id>
- Must load metrics from SQLite artifacts
- Must output delta + summary report

7) Dataset Generation (training data)
CLI:
  python -m netbench.app dataset export --out ./out/dataset

Data spec:
- Build run_records.jsonl from SQLite:
  Each line includes:
    - run_id
    - benchmark
    - platform
    - nl_goal (if exists)
    - run.yaml
    - tuning_profile.yaml
    - cmd.sh
    - metrics.json
    - summary.md (optional)
    - citations.json
    - env snapshot
- Create SFT JSONL in instruction format:
  Messages: system, user, assistant
  - For planning tasks: input = nl_goal + env snapshot summary; output = run.yaml + tuning_profile.yaml (as YAML in assistant output)
  - For parsing tasks: input = log snippet; output = normalized metrics summary
  - For compare tasks: input = baseline + candidate metrics; output = markdown delta summary
- Redaction:
  - remove hostnames/IPs
  - replace PCI BDF patterns with placeholders
- Split:
  - deterministic split by hash(run_id): 80/10/10 train/val/test
- Also build eval_cases.json with golden prompts and expected patterns.

8) Evaluation Harness (validation + regression)
CLI:
  python -m netbench.app eval run --cases data/golden_prompts/eval_cases.yaml

Must implement evaluation categories:
A) Grounding (faithfulness)
- Check that any tuning recommendation returned is supported by retrieved citations.
- If “NOT FOUND IN KB” expected, enforce it.

B) Tool correctness (command validity checks)
- Ensure generated cmd.sh includes required parts for each benchmark (only if KB confirms them; otherwise do not hallucinate).
- Validate schema for run.yaml and tuning_profile.yaml.
- Validate plan vs env snapshot constraints (hugepages capacity, NUMA mapping placeholders, etc.)

C) Parser correctness
- Unit tests: parse sample logs and compare to expected extracted numbers (provide expected fixtures)

D) Safety
- Ensure BIOS/reboot steps require approval token and workflow stops without it.

Provide a rubric scoring function in src/netbench/eval/metrics.py and output:
- eval_report.json
- eval_report.md

9) Optional Fine-tuning (LoRA)
Provide scripts that run only if user installs optional deps.
CLI:
  python -m netbench.app finetune lora --dataset ./out/dataset/sft_train.jsonl --val ./out/dataset/sft_val.jsonl

Requirements:
- Use PEFT LoRA on a small open model (configurable via env MODEL_ID)
- Provide:
  - training config (yaml)
  - saved adapter
  - eval script that compares base vs lora on eval_cases
- IMPORTANT:
  - Even with LoRA, factual tuning guidance must remain RAG-grounded.
  - LoRA should only improve formatting/consistency and reduce schema errors.

LANGGRAPH WORKFLOW (must implement)
StateGraph nodes (minimum):
1) classify_intent (ask/plan/parse/compare/dataset/eval)
2) retrieve_kb (LlamaIndex)
3) build_plan (LLM structured output -> intermediate)
4) apply_tuning_advisor (hybrid RAG + rules)
5) validate (MCP validate_plan tool)
6) safety_gate (approval token required for disruptive actions)
7) tool_execute (render_command OR parse_results OR compare_runs)
8) finalize_response (attach citations, artifacts, and “NOT FOUND IN KB” if required)
- tool_execute must also support explain_metric.

- Provide state schema in src/netbench/graph/state.py
- Add retry edges for retrieval/tool failures with max attempts.

DOCUMENTATION REQUIREMENTS
1) README.md:
- What it does (in 10 lines)
- Quickstart: uv sync, build index, run demo
- Architecture diagram
- Safety statement
- Limitations

2) docs/runbook.md:
- Step-by-step for:
  - add PDFs
  - build index
  - run demo
  - plan a benchmark
  - parse and compare
  - export dataset
  - run evaluation
  - optional finetune
- Common troubleshooting

3) docs/architecture.md:
- Explain components + data flow
- Why LangGraph + MCP separation
- Artifacts + schemas

4) docs/tuning.md:
- Explain how tuning advisor works:
  - what is RAG-sourced vs rule-sourced
  - how to update tuning rules
  - how to verify tuning changes

5) docs/evaluation.md:
- Explain eval cases, rubric, adding new cases, CI gating

6) SECURITY.md:
- human-in-the-loop for BIOS changes
- redaction strategy for logs and PII
- audit log strategy
- safe tool policies

7) DESIGN.md:
- LangGraph state machine diagram (ASCII)
- data model
- tool contracts
- reasoning boundaries: RAG as truth source

SAMPLE DATA REQUIREMENTS
Under data/sample_runs/, include:
- cryptoperf_run_001/ with:
  - logs/ stdout.txt
  - env/ lscpu.txt, numactl.txt, hugepages.txt (mocked ok)
- testpmd_run_001/
- l3fwd_run_001/
Each must contain plausible-looking logs and the repo must parse them deterministically.

IMPORTANT: If you don’t have real logs, synthesize minimal logs that match your parser patterns and clearly mark them as “synthetic sample logs”.

TESTS / QUALITY GATES
- All parsers must have unit tests.
- All schemas must be validated in tests.
- Must include tests that enforce “NOT FOUND IN KB” behavior when citations do not support a claim.
- Provide GitHub Actions CI that runs:
  - unit tests
  - a small “demo” smoke test (index build can be mocked by prebuilt tiny fixtures if needed)

DELIVERABLES
- Output the full repository file tree with full contents of all key files.
- Code must be complete and runnable with no missing imports.
- Include commands in Makefile:
  make bootstrap
  make index
  make demo
  make test
  make eval
  make dataset
  make lint

STYLE
- Clean, production-style code
- Strong typing
- Clear docstrings
- Minimal but real error handling
- No vague TODOs; if something is optional, implement a working stub with explicit guardrails.

FINAL CHECK
Before finishing, ensure:
- “make demo” runs end-to-end locally using sample runs and produces out/ artifacts.
- The PoC is centered on CryptoPerf, testpmd, and L3/L2 forwarding.
- Dataset generation + eval + optional LoRA pipeline exist and are documented.
