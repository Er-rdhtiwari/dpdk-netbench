# NetBench Copilot - Project Summary

## Repository Status

This repository provides a **production-style PoC** for an AI-powered DPDK benchmark assistant. The implementation includes:

### ✅ Completed Components

1. **Project Structure & Configuration**
   - `pyproject.toml` with all dependencies (LlamaIndex, LangChain, LangGraph, MCP)
   - `.env.example` with configuration templates
   - `.gitignore` with proper exclusions
   - `Makefile` with all commands
   - `LICENSE` (MIT)

2. **Core Configuration & Models**
   - `src/netbench/config.py` - Pydantic settings management
   - `src/netbench/store/models.py` - Complete data models (RunRecord, Citation, etc.)
   - `src/netbench/store/db.py` - SQLite storage layer

3. **Knowledge Base (RAG)**
   - `src/netbench/kb/ingest.py` - LlamaIndex PDF ingestion with metadata
   - `src/netbench/kb/retrieve.py` - Vector retrieval with filtering
   - `src/netbench/kb/citations.py` - Citation management and grounding enforcement

4. **MCP Server Foundation**
   - `src/netbench/mcp_server/schemas.py` - Pydantic schemas for all 6 tools
   - `src/netbench/mcp_server/__init__.py` - Module structure

5. **Documentation**
   - `README.md` - Project overview and quickstart
   - `DESIGN.md` - Complete architecture with ASCII diagrams
   - `SECURITY.md` - Security policies and best practices
   - `IMPLEMENTATION_GUIDE.md` - Detailed implementation reference (1000+ lines)

6. **Scripts**
   - `scripts/00_bootstrap.sh` - Environment setup
   - `scripts/10_build_index.sh` - KB index building
   - `scripts/20_demo.sh` - Interactive demo

7. **Data Structure**
   - `data/kb/manifest.yaml` - KB manifest template
   - Directory structure for sample runs

8. **CI/CD**
   - `.github/workflows/ci.yml` - GitHub Actions workflow

### 🚧 Implementation Required

The following components are **architecturally designed** with complete specifications in `IMPLEMENTATION_GUIDE.md`:

1. **MCP Server Implementation** (~500 lines)
   - `src/netbench/mcp_server/server.py`
   - `src/netbench/mcp_server/tools.py`

2. **LangGraph Workflow** (~1000 lines)
   - `src/netbench/graph/state.py` ✅ (schema provided)
   - `src/netbench/graph/workflow.py` (node implementations needed)
   - `src/netbench/graph/policies.py`

3. **Benchmark Adapters** (~2000 lines)
   - `src/netbench/benchmarks/base.py` ✅ (interface provided)
   - `src/netbench/benchmarks/cryptoperf.py`
   - `src/netbench/benchmarks/testpmd.py`
   - `src/netbench/benchmarks/l3fwd.py`
   - `src/netbench/benchmarks/l2fwd.py`
   - `src/netbench/benchmarks/__init__.py` ✅ (structure provided)

4. **Parsers** (~1500 lines)
   - `src/netbench/parsing/common.py`
   - `src/netbench/parsing/cryptoperf_parser.py`
   - `src/netbench/parsing/testpmd_parser.py`
   - `src/netbench/parsing/l3fwd_parser.py`

5. **Tuning Advisor** (~800 lines)
   - `src/netbench/tuning/advisor.py`
   - `src/netbench/tuning/rules.py`
   - `src/netbench/tuning/validators.py`
   - `src/netbench/tuning/envprobe.py`

6. **Dataset Generation** (~600 lines)
   - `src/netbench/dataset/export.py`
   - `src/netbench/dataset/redact.py`
   - `src/netbench/dataset/templates.py`

7. **Evaluation Harness** (~700 lines)
   - `src/netbench/eval/harness.py`
   - `src/netbench/eval/metrics.py`

8. **CLI Application** (~500 lines)
   - `src/netbench/app.py` ✅ (structure provided)

9. **Optional Fine-tuning** (~500 lines)
   - `src/netbench/finetune/train_lora.py`
   - `src/netbench/finetune/eval_lora.py`

10. **Sample Data** (~500 lines)
    - Synthetic logs for all benchmarks
    - Environment snapshots
    - Golden prompts for evaluation

11. **Tests** (~2000 lines)
    - Unit tests for all components
    - Integration tests
    - Grounding enforcement tests

12. **Additional Documentation** (~3000 lines)
    - `docs/runbook.md`
    - `docs/architecture.md`
    - `docs/safety.md`
    - `docs/evaluation.md`
    - `docs/dataset.md`
    - `docs/tuning.md`
    - `docs/benchmarks/*.md`

## Architecture Highlights

### 1. Grounding Enforcement
- All factual claims MUST be supported by KB citations
- Output "NOT FOUND IN KB" when information unavailable
- Citations include: source_file, page_start, page_end, doc_id, chunk_id
- Grounding validation in evaluation harness

### 2. Deterministic Tool Boundary (MCP)
- Commands generated via schema-validated tools, not free-form LLM
- 6 tools: render_command, parse_results, compare_runs, validate_plan, build_dataset, explain_metric
- Pydantic request/response schemas for all tools
- Prevents shell injection and ensures reproducibility

### 3. Safety Policies
- BIOS changes / reboots NEVER executed automatically
- Requires `NETBENCH_APPROVAL_TOKEN` in environment
- Workflow stops if approval required but token missing
- Manual steps clearly documented

### 4. LangGraph Workflow
- 8 nodes: classify_intent, retrieve_kb, build_plan, apply_tuning_advisor, validate, safety_gate, tool_execute, finalize_response
- Conditional routing based on intent
- Retry edges for failures (max 3 attempts)
- State tracking with TypedDict

### 5. Hybrid Tuning Advisor
- RAG-based recommendations from KB
- Rule-based validation for constraints
- Environment snapshot integration
- Conflict detection and resolution

## Implementation Patterns

All components follow consistent patterns:

### Benchmark Adapter Pattern
```python
class BenchmarkAdapter(ABC):
    def build_plan(nl_goal, platform, kb_context) -> Dict
    def render_command(run_yaml, scenario_key) -> str
    def parse_logs(log_paths) -> Tuple[Dict, List[str]]
    def compare_metrics(baseline, candidate) -> Tuple[Dict, str, List[str]]
    def get_metric_definitions() -> Dict[str, str]
```

### Parser Pattern
```python
def parse_benchmark_logs(log_paths: List[str]) -> Tuple[Dict[str, Any], List[str]]:
    """Parse logs to normalized metrics.
    
    Returns:
        Tuple of (metrics dict, warnings list)
    """
    metrics = {}
    warnings = []
    
    for log_path in log_paths:
        # Regex-based extraction
        # Normalize to common format
        # Collect warnings
    
    return metrics, warnings
```

### Tool Pattern
```python
def tool_function(request: RequestSchema) -> ResponseSchema:
    """Tool implementation with error handling.
    
    Args:
        request: Validated request schema
        
    Returns:
        Response schema with success flag and errors
    """
    try:
        # Implementation
        return ResponseSchema(success=True, ...)
    except Exception as e:
        return ResponseSchema(success=False, errors=[str(e)])
```

## Quick Start Guide

### 1. Bootstrap
```bash
cd netbench-copilot
bash scripts/00_bootstrap.sh
```

### 2. Add PDFs
```bash
# Copy your DPDK tuning PDFs
cp /path/to/pdfs/*.pdf data/kb/pdfs/

# Update manifest
vim data/kb/manifest.yaml
```

### 3. Build Index
```bash
make index
```

### 4. Configure
```bash
# Edit .env and add OPENAI_API_KEY
vim .env
```

### 5. Run Demo
```bash
make demo
```

### 6. Ask Questions
```bash
netbench ask --query "What are recommended hugepage settings for EPYC 9004?"
```

### 7. Plan Benchmark
```bash
netbench plan --benchmark cryptoperf --platform epyc9004 \
  --nl "Test AES-GCM-128 at 64B and 1024B frame sizes"
```

## Development Workflow

### Adding a New Benchmark

1. Create adapter: `src/netbench/benchmarks/mybench.py`
2. Implement `BenchmarkAdapter` interface
3. Create parser: `src/netbench/parsing/mybench_parser.py`
4. Add tests: `tests/test_mybench.py`
5. Add sample logs: `data/sample_runs/mybench_run_001/`
6. Update documentation: `docs/benchmarks/mybench.md`

### Adding KB PDFs

1. Copy PDF to `data/kb/pdfs/`
2. Update `data/kb/manifest.yaml`
3. Run `make index`
4. Verify with `netbench ask`

### Running Tests

```bash
make test          # All tests
make lint          # Linters
make format        # Format code
```

## Key Design Decisions

### 1. Why LlamaIndex + LangChain + LangGraph?
- **LlamaIndex**: Best-in-class RAG with metadata filtering
- **LangChain**: Standard LLM interface and tool calling
- **LangGraph**: Deterministic workflow orchestration with state management

### 2. Why MCP for Tools?
- Enforces schema validation
- Prevents free-form LLM command generation
- Enables independent testing
- Clear contract between reasoning and execution

### 3. Why SQLite?
- Simple, local, no external dependencies
- Sufficient for PoC and small-scale production
- Easy to migrate to PostgreSQL if needed

### 4. Why uv over poetry?
- Faster dependency resolution
- Better lock file format
- Modern Python packaging
- Growing ecosystem adoption

### 5. Why Pydantic v2?
- Strong typing with runtime validation
- Excellent error messages
- JSON schema generation
- Settings management

## Limitations & Future Work

### Current Limitations
1. Requires user-provided DPDK PDFs (not included)
2. Parsers are regex-based (brittle for format changes)
3. No actual benchmark execution (only planning)
4. Local-only (no distributed deployment)
5. CPU-only fine-tuning (slow without GPU)

### Future Enhancements
1. Multi-modal KB (videos, diagrams, code)
2. Active learning from user feedback
3. Actual benchmark execution integration
4. Real-time monitoring during runs
5. Collaborative features (share plans/results)
6. Advanced grounding (semantic similarity)
7. Automated iterative tuning

## File Count Summary

- **Configuration**: 5 files
- **Source Code**: 40+ files (20 implemented, 20+ specified)
- **Tests**: 15+ files (specified)
- **Documentation**: 15+ files (8 implemented, 7+ specified)
- **Scripts**: 6 files (3 implemented, 3+ specified)
- **Sample Data**: 12+ files (specified)
- **CI/CD**: 1 file (implemented)

**Total**: ~95 files, ~15,000 lines of code (when fully implemented)

## Estimated Implementation Time

For a senior engineer familiar with the stack:

- **MCP Server & Tools**: 2-3 days
- **LangGraph Workflow**: 2-3 days
- **Benchmark Adapters**: 3-4 days
- **Parsers**: 2-3 days
- **Tuning Advisor**: 2 days
- **Dataset & Eval**: 2 days
- **Tests**: 3-4 days
- **Documentation**: 2 days
- **Sample Data**: 1 day

**Total**: 19-26 days (4-5 weeks)

## Success Criteria

The PoC is considered successful when:

1. ✅ Repository structure complete
2. ✅ Core models and config implemented
3. ✅ KB ingestion and retrieval working
4. ⏳ All 6 MCP tools implemented and tested
5. ⏳ LangGraph workflow runs end-to-end
6. ⏳ At least 2 benchmarks fully supported (CryptoPerf + testpmd)
7. ⏳ Grounding enforcement validated in tests
8. ⏳ Safety policies enforced (approval gate works)
9. ⏳ Dataset export produces valid SFT JSONL
10. ⏳ Evaluation harness runs and scores correctly
11. ⏳ `make demo` runs successfully with sample data
12. ⏳ Documentation complete and accurate

## Contact & Support

- **Repository**: https://github.com/your-org/netbench-copilot
- **Issues**: https://github.com/your-org/netbench-copilot/issues
- **Security**: security@netbench.example.com
- **Documentation**: See `docs/` directory

## License

MIT License - See [LICENSE](LICENSE) file

---

**Status**: Foundation Complete, Implementation In Progress

**Last Updated**: 2024-01-24