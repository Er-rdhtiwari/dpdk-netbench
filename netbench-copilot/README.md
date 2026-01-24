# NetBench Copilot

**AI-powered DPDK benchmark planning, execution, and analysis assistant**

NetBench Copilot converts natural-language benchmark goals into validated run plans, tuning profiles, and executable commands for DPDK benchmarks (CryptoPerf, testpmd, L3fwd, L2fwd). All factual claims are grounded in retrieved knowledge base documents, with deterministic tool execution via MCP.

## What It Does

- **KB-Grounded Q&A**: Ask questions about DPDK tuning, benchmarks, and best practices with citations
- **Plan Generation**: Convert NL goals → validated `run.yaml` + `tuning_profile.yaml` + `cmd.sh`
- **Result Parsing**: Parse benchmark logs into normalized `metrics.json`
- **Run Comparison**: Compare baseline vs candidate runs with delta reports
- **Dataset Export**: Generate SFT training data from stored benchmark runs
- **Evaluation**: Validate grounding, tool correctness, and safety policies
- **Optional Fine-tuning**: LoRA fine-tuning pipeline for improved consistency

## Architecture

```
User NL Goal → LangGraph Workflow → RAG Retrieval (LlamaIndex)
                    ↓
              Tuning Advisor (hybrid RAG + rules)
                    ↓
              MCP Tools (deterministic command/parse/compare)
                    ↓
              Validated Artifacts (run.yaml, cmd.sh, metrics.json)
```

## Quickstart

```bash
# 1. Bootstrap environment
make bootstrap

# 2. Add your DPDK tuning PDFs to data/kb/pdfs/
cp /path/to/amd-epyc-dpdk-tuning.pdf data/kb/pdfs/

# 3. Build KB index
make index

# 4. Run demo (uses sample data)
make demo

# 5. Ask a question
netbench ask --query "What are the recommended hugepage settings for EPYC 9004?"

# 6. Plan a benchmark
netbench plan --benchmark cryptoperf --platform epyc9004 --nl "Test AES-GCM-128 at 64B and 1024B frame sizes"

# 7. Parse sample logs
netbench parse --benchmark testpmd --run-dir data/sample_runs/testpmd_run_001 --store true

# 8. Compare runs
netbench compare --baseline run_001 --candidate run_002

# 9. Export dataset
make dataset

# 10. Run evaluation
make eval
```

## Safety Statement

**IMPORTANT**: NetBench Copilot will NEVER automatically execute BIOS changes or system reboots. Any tuning profile requiring such actions will be marked `requires_approval: true` and will halt unless `NETBENCH_APPROVAL_TOKEN` is explicitly set in your environment.

## Supported Benchmarks

- **CryptoPerf** (`dpdk-test-crypto-perf`): Crypto algorithm performance testing
- **testpmd**: Packet forwarding and NIC performance
- **L3fwd**: Layer 3 forwarding performance
- **L2fwd**: Layer 2 forwarding performance

## Key Features

### Grounding Enforcement
All tuning recommendations and benchmark methodology claims MUST be supported by retrieved KB citations. If information is not found in the KB, the system outputs: `"NOT FOUND IN KB"`.

### Deterministic Tools (MCP)
Commands, parsing, and comparisons are generated via schema-validated MCP tools, not free-form LLM output.

### Dataset Generation
Export stored runs as SFT JSONL for fine-tuning, with automatic redaction of hostnames/IPs/PCI addresses.

### Evaluation Harness
Validate grounding faithfulness, tool correctness, parser accuracy, and safety policies with a rubric-based evaluation framework.

## Documentation

- [Runbook](docs/runbook.md) - Step-by-step usage guide
- [Architecture](docs/architecture.md) - System design and data flow
- [Safety](docs/safety.md) - Human-in-the-loop policies
- [Evaluation](docs/evaluation.md) - Eval cases and rubrics
- [Dataset](docs/dataset.md) - Dataset generation and format
- [Tuning](docs/tuning.md) - Tuning advisor internals
- [Benchmarks](docs/benchmarks/) - Per-benchmark documentation

## Requirements

- Python 3.11+
- OpenAI API key (or local LLM endpoint)
- DPDK tuning PDFs (user-provided, not included)

## Limitations

- Requires user-provided DPDK tuning PDFs for KB
- LLM quality depends on model and prompt engineering
- Parsers are regex-based and may need updates for new DPDK versions
- Fine-tuning is optional and requires GPU for practical training times

## Contributing

See [DESIGN.md](DESIGN.md) for architecture details and [SECURITY.md](SECURITY.md) for security policies.

## License

MIT License - see [LICENSE](LICENSE)