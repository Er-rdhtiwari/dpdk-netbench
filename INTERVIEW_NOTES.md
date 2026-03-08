# NetBench Copilot - Repo Analysis + Interview Notes

## 1) What this repo is (1-paragraph summary)
NetBench Copilot is a production-style proof-of-concept that plans, runs, and analyzes DPDK benchmarks using a KB-grounded workflow. It ingests tuning PDFs into a local RAG index, converts natural language goals into run plans and tuning profiles, enforces safety checks for BIOS/reboot steps, generates deterministic benchmark commands via MCP tools, parses logs into normalized metrics, compares baseline vs candidate runs, stores artifacts in SQLite, and can export datasets for SFT/eval and optional LoRA finetuning.

## 2) Repository layout (high level)
- Root: README, LICENSE
- `netbench-copilot/` (main project)
  - `src/netbench/` core package
  - `docs/` architecture, runbook, tuning, evaluation, safety, benchmarks
  - `scripts/` bootstrap, index build, demo, dataset export, eval, optional finetune
  - `data/` KB manifest, sample logs, golden prompts
  - `tests/` parser/tool/validator/grounding tests

## 3) Architecture (components + data flow)

### Components
- CLI (Typer) entrypoint: `src/netbench/app.py`
- KB ingest + retrieval: LlamaIndex + SimpleHashEmbedding (`src/netbench/kb/*`)
- Planning + tuning advisor: deterministic extraction from KB chunks (`src/netbench/tuning/*`)
- LangGraph workflow (optional orchestration): `src/netbench/graph/*`
- MCP tool boundary: deterministic schemas + tools (`src/netbench/mcp_server/*`)
- Benchmark adapters + parsers: `src/netbench/benchmarks/*`, `src/netbench/parsing/*`
- Run store: SQLite + RunRecord model (`src/netbench/store/*`)
- Dataset export + eval harness: `src/netbench/dataset/*`, `src/netbench/eval/*`

### Data flow (typical plan/parse/compare lifecycle)
1) KB ingest builds local index from PDFs in `data/kb/pdfs/`.
2) `plan` retrieves KB chunks and extracts tuning guidance.
3) Run plan and tuning profile are validated by MCP tool schema.
4) Command is rendered deterministically by benchmark adapter.
5) Runs are stored in SQLite for lineage.
6) `parse` reads logs and produces metrics.
7) `compare` calculates deltas and summary.
8) Optional dataset export and evaluation.

### ASCII architecture diagram
```
User
  -> CLI (Typer)
     -> (Optional) LangGraph State Machine
        classify -> retrieve -> plan -> tune -> validate -> safety -> tools -> finalize
     -> KB Retriever (LlamaIndex + SimpleHashEmbedding)
     -> Tuning Advisor (KB-grounded extraction)
     -> MCP Tools (render/parse/compare/validate/build_dataset)
     -> Bench Adapters + Parsers
     -> Artifacts in out/
     -> SQLite run store (.cache/netbench.db)
```

### State machine (from DESIGN.md)
```
[classify_intent] -> [retrieve_kb] -> [build_plan] -> [apply_tuning_advisor]
        -> [validate] -> [safety_gate] -> [tool_execute] -> [finalize_response]
```

## 4) Key design choices and how they work

### KB ingestion and retrieval
- Uses LlamaIndex with a simple hash-based embedding for offline determinism.
- PDFs are split into sections and chunked; metadata includes doc_id, page, vendor, platform.
- Retrieval filters low-score chunks and enforces keyword presence.

### Planning + tuning
- Run plan includes benchmark, platform, scenarios, EAL options, logging, env snapshot commands.
- Tuning advisor extracts HUGEPAGES, IRQ_AFFINITY, ISOLCPUS, etc., from KB chunks.
- If required fields are missing, the system returns `NOT FOUND IN KB`.

### MCP tools (deterministic boundary)
- Tools validate request/response schemas (Pydantic) and avoid free-form generation.
- Core tools: render_command, parse_results, compare_runs, validate_plan, build_dataset, explain_metric.

### Bench adapters + parsers
- Adapters render benchmark-specific commands; parsers normalize metrics from logs.
- Benchmarks included: testpmd, l3fwd, l2fwd, cryptoperf.

### Storage and artifacts
- Run artifacts and metadata stored in SQLite (`RunRecord`).
- Output files (plans, tuning profiles, metrics, comparisons) written to `out/`.

## 5) Safety and grounding
- BIOS/reboot steps require `NETBENCH_APPROVAL_TOKEN` to proceed.
- All tuning recommendations must be grounded in the KB or return `NOT FOUND IN KB`.
- Deterministic MCP tools are the only source of command output.

## 6) Tests and evaluation
- Unit tests cover parsers, MCP tool outputs, validators, and grounding.
- Evaluation harness runs gold prompt cases for grounding/tool correctness/safety.

## 7) Limitations (as documented + code)
- Sample KB and logs are synthetic.
- Embeddings are deterministic (not semantic) for offline operation.
- Command templates are simplified; must be validated for real DPDK versions.
- LangGraph workflow exists but CLI currently uses direct calls (graph is optional for future integration).

## 8) How to discuss this in an interview

### 30-second pitch
"I built a PoC called NetBench Copilot that turns natural language benchmarking goals into DPDK run plans. It uses a local RAG index of tuning PDFs, extracts validated tuning profiles, gates BIOS changes behind an approval token, generates deterministic commands through MCP tools, parses logs into metrics, compares runs, and stores everything in SQLite for lineage and dataset export. The design separates LLM-style planning from deterministic tool execution to keep safety and reproducibility." 

### Deeper dive talking points (what to emphasize)
- **Problem statement**: DPDK tuning is complex and error-prone; this system makes it reproducible and auditable.
- **Architecture**: KB-grounded advice + deterministic tool boundary (MCP) + validation and safety gates.
- **Design tradeoffs**: Offline deterministic embeddings vs semantic quality; simplified commands vs portability.
- **Reliability**: Schema validation, safety token gating, and test coverage for parsers and tools.
- **Extensibility**: Add new benchmarks by implementing a new adapter + parser + docs.

### Good technical details to mention
- Uses LlamaIndex to build a local vector index from PDFs; retrieval is filtered for relevance.
- A LangGraph state machine defines the lifecycle from retrieval to final response.
- MCP tools enforce strict schemas and deterministic outputs.
- Run artifacts are stored in SQLite and can be exported for SFT and eval datasets.

### What you would improve (shows maturity)
- Swap hash embedding for real semantic embeddings for better retrieval quality.
- Expand validators to check NIC/NUMA compatibility and real hardware constraints.
- Add richer scenario inference or a real LLM planner for complex NL goals.
- Integrate actual DPDK versions and hardware inventory in env snapshot.
- Add CI coverage for end-to-end flows using real sample logs.

## 9) Likely interviewer follow-ups (with hints)
- **How do you ensure safety for BIOS changes?**
  - Explain the approval token gating and explicit `requires_approval` flag in tuning profile.
- **How do you keep outputs reproducible?**
  - Deterministic embeddings, strict schemas, MCP tool boundaries, and fixed templates.
- **How do you add a new benchmark?**
  - Implement adapter + parser, add docs, update tools for benchmark selection.
- **How do you handle missing KB coverage?**
  - Return `NOT FOUND IN KB` and fail early; also add missing docs to KB.
- **How do you test parsing correctness?**
  - Unit tests against sample logs; assert expected metrics.

## 10) Follow-up questions you can ask the interviewer
- "What level of automation vs human approval do you require for system tuning changes?"
- "How do you validate benchmarking recommendations against real hardware in your pipeline?"
- "What logging/traceability requirements do you expect for benchmark and tuning workflows?"
- "Do you prefer deterministic tooling boundaries or more flexible LLM reasoning in production?"
- "How do you currently manage KB updates and doc/version provenance?"
