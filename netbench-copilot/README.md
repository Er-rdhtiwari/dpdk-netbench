# NetBench Copilot

NetBench Copilot is a production-style PoC for planning, running, and analyzing DPDK benchmarks with KB-grounded guidance.
- Builds a local RAG index from tuning PDFs.
- Converts natural language goals into run plans and tuning profiles.
- Enforces safety gating for BIOS/reboot steps.
- Produces deterministic commands via MCP tools.
- Parses benchmark logs into normalized metrics.
- Compares baseline vs candidate runs with deltas.
- Stores run artifacts in SQLite for lineage.
- Exports SFT/eval datasets from run records.
- Evaluates grounding, tool correctness, parsers, and safety.
- Supports optional LoRA finetuning for formatting consistency.

## Quickstart

```bash
uv sync
bash scripts/00_bootstrap.sh
bash scripts/10_build_index.sh
bash scripts/20_demo.sh
```

Place your PDFs under `data/kb/pdfs/` and register them in `data/kb/manifest.yaml`.

## Architecture (ASCII)

```
User -> CLI (Typer)
   -> LangGraph workflow
      -> LlamaIndex retrieve
      -> Tuning advisor (KB-grounded)
      -> MCP tools (render/parse/compare/validate)
   -> Artifacts in out/
   -> SQLite run store
```

## Safety

BIOS/reboot guidance is never auto-executed. If a tuning profile includes BIOS changes or reboot steps, the workflow
requires `NETBENCH_APPROVAL_TOKEN` to proceed.

## Limitations

- Sample KB and logs are synthetic.
- This PoC uses deterministic embeddings for offline operation; replace with production embeddings as needed.
- Command templates are simplified and should be validated against your DPDK version.
