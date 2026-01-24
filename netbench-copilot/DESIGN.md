# NetBench Copilot - Design Document

## Overview

NetBench Copilot is an AI-powered assistant for DPDK benchmark planning, execution, and analysis. It uses a hybrid architecture combining:

- **LlamaIndex** for RAG-based knowledge retrieval
- **LangChain** for LLM interface and tool calling
- **LangGraph** for deterministic workflow orchestration
- **MCP (Model Context Protocol)** for deterministic tool execution boundary

## Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (Typer CLI: netbench)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangGraph Workflow                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Classify    │→ │  Retrieve    │→ │  Build Plan  │          │
│  │  Intent      │  │  KB (RAG)    │  │  (LLM)       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                  │
│         ▼                  ▼                  ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Apply       │→ │  Validate    │→ │  Safety      │          │
│  │  Tuning      │  │  (MCP Tool)  │  │  Gate        │          │
│  │  Advisor     │  └──────────────┘  └──────────────┘          │
│  └──────────────┘         │                  │                  │
│         │                  │                  │                  │
│         ▼                  ▼                  ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Tool        │→ │  Finalize    │→ │  Store       │          │
│  │  Execute     │  │  Response    │  │  Artifacts   │          │
│  │  (MCP)       │  │  + Citations │  │  (SQLite)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Tool Server                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Tool A: render_command    (run.yaml → cmd.sh)           │   │
│  │  Tool B: parse_results     (logs → metrics.json)         │   │
│  │  Tool C: compare_runs      (metrics → delta + summary)   │   │
│  │  Tool D: validate_plan     (plan + env → valid/invalid)  │   │
│  │  Tool E: build_dataset     (runs → SFT JSONL)            │   │
│  │  Tool F: explain_metric    (metric → KB explanation)     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Base (RAG)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LlamaIndex Vector Store                                 │   │
│  │  - PDF ingestion with metadata                           │   │
│  │  - Chunking with page/section tracking                   │   │
│  │  - Embedding: HuggingFace BGE-small                      │   │
│  │  - Retrieval with similarity threshold                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Ask Mode (KB Q&A)
```
User Query → Retrieve KB → Format Citations → Return Answer or "NOT FOUND IN KB"
```

### 2. Plan Mode (NL → Artifacts)
```
NL Goal → Classify Intent → Retrieve KB Context
    ↓
Build Plan (LLM) → Apply Tuning Advisor (Hybrid RAG + Rules)
    ↓
Validate Plan (MCP Tool) → Safety Gate (Check Approval Token)
    ↓
Render Command (MCP Tool) → Store Artifacts → Return run.yaml + tuning_profile.yaml + cmd.sh
```

### 3. Parse Mode (Logs → Metrics)
```
Log Files → Parse Results (MCP Tool) → Normalize Metrics → Store Run Record
```

### 4. Compare Mode (Baseline vs Candidate)
```
Load Metrics (SQLite) → Compare Runs (MCP Tool) → Generate Delta + Summary
```

### 5. Dataset Export
```
Query Runs (SQLite) → Redact Sensitive Data → Build SFT JSONL → Split Train/Val/Test
```

### 6. Evaluation
```
Load Eval Cases → Run Workflow → Score Grounding + Correctness + Safety → Report
```

## Component Details

### LangGraph State Machine

**State Schema:**
```python
class WorkflowState(TypedDict):
    intent: str  # ask, plan, parse, compare, dataset, eval
    query: str
    benchmark: Optional[str]
    platform: Optional[str]
    
    # Retrieval
    citations: List[Citation]
    kb_context: str
    
    # Planning
    run_yaml: Optional[str]
    tuning_profile_yaml: Optional[str]
    cmd_sh: Optional[str]
    requires_approval: bool
    
    # Validation
    validation_errors: List[str]
    validation_warnings: List[str]
    
    # Output
    response: str
    artifacts: Dict[str, Any]
    error: Optional[str]
```

**Nodes:**
1. `classify_intent`: Determine user intent (ask/plan/parse/compare/dataset/eval)
2. `retrieve_kb`: Retrieve relevant KB chunks using LlamaIndex
3. `build_plan`: Generate run plan using LLM with KB context
4. `apply_tuning_advisor`: Apply hybrid RAG + rule-based tuning recommendations
5. `validate`: Call MCP validate_plan tool
6. `safety_gate`: Check if approval token required and present
7. `tool_execute`: Execute MCP tools (render_command, parse_results, compare_runs, explain_metric)
8. `finalize_response`: Package response with citations and artifacts

**Edges:**
- Conditional routing based on intent
- Retry edges for retrieval/tool failures (max 3 attempts)
- Safety gate blocks execution if approval required but token missing

### MCP Tool Boundary

**Why MCP?**
- Enforces deterministic tool execution with schema validation
- Prevents free-form LLM command generation
- Provides clear contract between LLM reasoning and tool execution
- Enables testing and verification of tool behavior independently

**Tool Contracts:**

All tools use Pydantic schemas for request/response validation.

**Tool A: render_command**
- Input: benchmark + run.yaml + scenario_key
- Output: cmd.sh content + command lines
- Validation: Ensures all required parameters present, no shell injection

**Tool B: parse_results**
- Input: benchmark + log paths
- Output: normalized metrics.json + warnings
- Validation: Regex-based parsing with error handling

**Tool C: compare_runs**
- Input: baseline metrics + candidate metrics + benchmark
- Output: delta.json + summary.md + significant changes list
- Validation: Ensures metrics are comparable

**Tool D: validate_plan**
- Input: run.yaml + tuning_profile.yaml + env_snapshot
- Output: valid/invalid + errors + warnings + suggested fixes
- Validation: Schema validation + constraint checking

**Tool E: build_dataset**
- Input: db_path + output_dir + split ratios + redact flag
- Output: train/val/test JSONL paths + record counts
- Validation: Ensures splits sum to 1.0, redaction applied

**Tool F: explain_metric**
- Input: metric_name + optional benchmark context
- Output: explanation (or "NOT FOUND IN KB") + citations
- Validation: Must retrieve from KB or return NOT_FOUND

### Grounding Enforcement

**Policy:**
1. All factual claims about tuning, benchmarks, parameters MUST be grounded in KB
2. If KB doesn't contain information, output exactly: "NOT FOUND IN KB"
3. Citations must include: source_file, page_start, page_end, doc_id, chunk_id
4. Grounding validation in eval harness checks citation support

**Implementation:**
- `CitationManager.enforce_grounding()`: Checks if response has sufficient citations
- `CitationManager.validate_response_grounding()`: Scores grounding ratio
- Eval harness includes grounding test cases

### Safety Policies

**BIOS Changes / Reboots:**
- Never executed automatically
- Marked in tuning_profile.yaml with `requires_approval: true`
- Workflow checks for `NETBENCH_APPROVAL_TOKEN` in environment
- If token missing, workflow stops and returns manual steps

**Redaction:**
- Hostnames: replaced with `HOST_<hash>`
- IP addresses: replaced with `IP_<hash>`
- PCI BDF: replaced with `PCI_<hash>`
- Applied during dataset export

**Audit Log:**
- All tool executions logged to SQLite
- Includes: timestamp, tool name, request, response, user

## Storage Schema (SQLite)

**Tables:**

1. **runs**: Stores complete run records
   - Primary key: run_id
   - Fields: benchmark, platform, status, nl_goal, run_yaml, tuning_profile_yaml, cmd_sh, env_snapshot, metrics_json, summary_md, citations_json, log_paths, requires_approval, parse_warnings, validation_errors

2. **comparisons**: Stores comparison results
   - Primary key: comparison_id
   - Foreign keys: baseline_run_id, candidate_run_id
   - Fields: delta_json, summary_md, significant_changes

3. **datasets**: Stores dataset export metadata
   - Primary key: dataset_id
   - Fields: source_run_ids, split, record_count, export_path, redacted

4. **eval_results**: Stores evaluation results
   - Primary key: eval_id
   - Fields: case_id, passed, score, details, errors

## Benchmark Adapters

Each benchmark has an adapter implementing:

```python
class BenchmarkAdapter(ABC):
    @abstractmethod
    def build_plan(self, nl_goal: str, platform: str, kb_context: str) -> Dict[str, Any]:
        """Build run plan from NL goal."""
        
    @abstractmethod
    def render_command(self, run_yaml: Dict, scenario_key: str) -> str:
        """Render command script."""
        
    @abstractmethod
    def parse_logs(self, log_paths: List[str]) -> Dict[str, Any]:
        """Parse logs to normalized metrics."""
        
    @abstractmethod
    def get_metric_definitions(self) -> Dict[str, str]:
        """Get metric name to description mapping."""
```

**Implemented Adapters:**
- CryptoPerf: Crypto algorithm performance
- testpmd: Packet forwarding and NIC performance
- L3fwd: Layer 3 forwarding
- L2fwd: Layer 2 forwarding

## Dataset Format

**SFT JSONL Format:**
```json
{
  "messages": [
    {"role": "system", "content": "You are NetBench Copilot..."},
    {"role": "user", "content": "Plan a CryptoPerf benchmark for AES-GCM-128..."},
    {"role": "assistant", "content": "run.yaml:\n...\ntuning_profile.yaml:\n..."}
  ],
  "metadata": {
    "run_id": "run_001",
    "benchmark": "cryptoperf",
    "platform": "epyc9004",
    "split": "train"
  }
}
```

**Instruction Templates:**
- Planning: NL goal + env → run.yaml + tuning_profile.yaml
- Parsing: Log snippet → metrics summary
- Comparison: Baseline + candidate → delta summary

## Evaluation Framework

**Categories:**

1. **Grounding (Faithfulness)**
   - Check tuning recommendations supported by citations
   - Enforce "NOT FOUND IN KB" when appropriate
   - Score: grounding_ratio (grounded_claims / total_claims)

2. **Tool Correctness**
   - Validate cmd.sh includes required components
   - Validate run.yaml and tuning_profile.yaml schemas
   - Check plan vs env snapshot constraints

3. **Parser Correctness**
   - Unit tests with expected fixtures
   - Compare parsed metrics to golden values

4. **Safety**
   - Ensure BIOS/reboot steps require approval
   - Verify workflow stops without token

**Rubric:**
- Grounding: 0-1 score based on citation support
- Correctness: 0-1 score based on schema validation + constraint checks
- Safety: Pass/Fail based on approval gate behavior

## Optional Fine-tuning

**LoRA Pipeline:**
1. Export dataset from stored runs
2. Train LoRA adapter on base model (Mistral-7B or similar)
3. Evaluate base vs LoRA on eval cases
4. Compare grounding, correctness, and consistency

**Important:**
- LoRA improves formatting/consistency, NOT factual knowledge
- Factual tuning guidance must remain RAG-grounded
- Fine-tuning is optional; CPU-only path must work

## Deployment

**Local Development:**
```bash
make bootstrap  # Install dependencies
make index      # Build KB index
make demo       # Run end-to-end demo
make test       # Run tests
```

**Production Considerations:**
- Use persistent vector store (e.g., Qdrant, Weaviate)
- Deploy MCP server separately for scalability
- Add authentication and rate limiting
- Implement audit logging to external system
- Use GPU for embedding and LLM inference

## Limitations

1. **KB Dependency**: Requires user-provided DPDK tuning PDFs
2. **LLM Quality**: Depends on model and prompt engineering
3. **Parser Brittleness**: Regex-based parsers may need updates for new DPDK versions
4. **No Execution**: Does not execute benchmarks, only generates plans
5. **Manual BIOS Changes**: Requires human intervention for system-level changes

## Future Enhancements

1. **Multi-modal KB**: Support videos, diagrams, code examples
2. **Active Learning**: Collect user feedback to improve recommendations
3. **Benchmark Execution**: Integrate with actual benchmark execution
4. **Real-time Monitoring**: Stream metrics during benchmark runs
5. **Collaborative Features**: Share plans and results across teams
6. **Advanced Grounding**: Use semantic similarity for better grounding checks
7. **Automated Tuning**: Iterative tuning based on benchmark results