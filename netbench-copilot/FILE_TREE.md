# NetBench Copilot - Complete File Tree

This document shows the complete file structure of the repository, indicating which files are implemented (✅) and which are specified but need implementation (📋).

```
netbench-copilot/
│
├── README.md                           ✅ Project overview and quickstart
├── LICENSE                             ✅ MIT License
├── DESIGN.md                           ✅ Architecture and design document
├── SECURITY.md                         ✅ Security policies
├── IMPLEMENTATION_GUIDE.md             ✅ Detailed implementation reference
├── PROJECT_SUMMARY.md                  ✅ Project status and summary
├── FILE_TREE.md                        ✅ This file
├── Makefile                            ✅ Build and task automation
├── pyproject.toml                      ✅ Project configuration and dependencies
├── .env.example                        ✅ Environment variable template
├── .gitignore                          ✅ Git ignore rules
│
├── .github/
│   └── workflows/
│       └── ci.yml                      ✅ GitHub Actions CI pipeline
│
├── docs/
│   ├── runbook.md                      📋 Step-by-step usage guide
│   ├── architecture.md                 📋 Detailed architecture
│   ├── safety.md                       📋 Safety policies expanded
│   ├── evaluation.md                   📋 Evaluation framework
│   ├── dataset.md                      📋 Dataset format and generation
│   ├── tuning.md                       📋 Tuning advisor internals
│   └── benchmarks/
│       ├── cryptoperf.md               📋 CryptoPerf documentation
│       ├── testpmd.md                  📋 testpmd documentation
│       ├── l3fwd_l2fwd.md              📋 L3fwd/L2fwd documentation
│       └── README.md                   📋 Benchmarks overview
│
├── data/
│   ├── kb/
│   │   ├── pdfs/                       📁 User-provided PDFs (not in repo)
│   │   │   └── .gitkeep                📋 Keep directory
│   │   └── manifest.yaml               ✅ KB manifest template
│   │
│   ├── sample_runs/
│   │   ├── cryptoperf_run_001/
│   │   │   ├── logs/
│   │   │   │   └── stdout.txt          📋 Synthetic CryptoPerf log
│   │   │   └── env/
│   │   │       ├── lscpu.txt           📋 Mock CPU info
│   │   │       ├── numactl.txt         📋 Mock NUMA info
│   │   │       └── hugepages.txt       📋 Mock hugepages info
│   │   │
│   │   ├── testpmd_run_001/
│   │   │   ├── logs/
│   │   │   │   └── stdout.txt          📋 Synthetic testpmd log
│   │   │   └── env/
│   │   │       └── (same as above)     📋
│   │   │
│   │   └── l3fwd_run_001/
│   │       ├── logs/
│   │       │   └── stdout.txt          📋 Synthetic L3fwd log
│   │       └── env/
│   │           └── (same as above)     📋
│   │
│   └── golden_prompts/
│       ├── plan_prompts.yaml           📋 Planning test cases
│       ├── ask_prompts.yaml            📋 Q&A test cases
│       └── eval_cases.yaml             📋 Evaluation test cases
│
├── scripts/
│   ├── 00_bootstrap.sh                 ✅ Environment setup
│   ├── 10_build_index.sh               ✅ KB index building
│   ├── 20_demo.sh                      ✅ Interactive demo
│   ├── 30_add_pdf.sh                   📋 Add PDF to KB
│   ├── 40_export_dataset.sh            📋 Export dataset
│   ├── 50_run_eval.sh                  📋 Run evaluation
│   └── 60_optional_finetune.sh         📋 Optional fine-tuning
│
├── src/
│   └── netbench/
│       ├── __init__.py                 ✅ Package init
│       ├── config.py                   ✅ Configuration management
│       ├── app.py                      📋 Typer CLI application (structure provided)
│       │
│       ├── kb/
│       │   ├── __init__.py             ✅ KB module init
│       │   ├── ingest.py               ✅ LlamaIndex ingestion
│       │   ├── retrieve.py             ✅ Retrieval wrapper
│       │   └── citations.py            ✅ Citation management
│       │
│       ├── graph/
│       │   ├── __init__.py             📋 Graph module init
│       │   ├── workflow.py             📋 LangGraph workflow (structure provided)
│       │   ├── state.py                📋 State schema (provided)
│       │   └── policies.py             📋 Safety policies
│       │
│       ├── tools/
│       │   ├── __init__.py             📋 Tools module init
│       │   └── mcp_client.py           📋 MCP client wrapper
│       │
│       ├── mcp_server/
│       │   ├── __init__.py             ✅ MCP server module init
│       │   ├── server.py               📋 MCP server entry (provided)
│       │   ├── tools.py                📋 Tool implementations (provided)
│       │   └── schemas.py              ✅ Request/response schemas
│       │
│       ├── benchmarks/
│       │   ├── __init__.py             📋 Benchmarks module init (structure provided)
│       │   ├── base.py                 📋 Base adapter interface (provided)
│       │   ├── cryptoperf.py           📋 CryptoPerf adapter
│       │   ├── testpmd.py              📋 testpmd adapter
│       │   ├── l3fwd.py                📋 L3fwd adapter
│       │   └── l2fwd.py                📋 L2fwd adapter
│       │
│       ├── tuning/
│       │   ├── __init__.py             📋 Tuning module init
│       │   ├── advisor.py              📋 Hybrid RAG + rules advisor
│       │   ├── rules.py                📋 Deterministic rules
│       │   ├── validators.py           📋 Plan validators
│       │   └── envprobe.py             📋 Environment snapshot
│       │
│       ├── parsing/
│       │   ├── __init__.py             📋 Parsing module init
│       │   ├── common.py               📋 Common parsing utilities
│       │   ├── cryptoperf_parser.py    📋 CryptoPerf parser
│       │   ├── testpmd_parser.py       📋 testpmd parser
│       │   └── l3fwd_parser.py         📋 L3fwd parser
│       │
│       ├── store/
│       │   ├── __init__.py             ✅ Store module init
│       │   ├── db.py                   ✅ SQLite access layer
│       │   └── models.py               ✅ Database models
│       │
│       ├── dataset/
│       │   ├── __init__.py             📋 Dataset module init
│       │   ├── export.py               📋 Dataset export
│       │   ├── redact.py               📋 Sensitive data redaction
│       │   └── templates.py            📋 Instruction templates
│       │
│       ├── eval/
│       │   ├── __init__.py             📋 Eval module init
│       │   ├── harness.py              📋 Evaluation harness
│       │   └── metrics.py              📋 Eval metrics and rubrics
│       │
│       └── finetune/
│           ├── __init__.py             📋 Finetune module init
│           ├── train_lora.py           📋 LoRA training
│           └── eval_lora.py            📋 LoRA evaluation
│
└── tests/
    ├── __init__.py                     📋 Tests init
    ├── conftest.py                     📋 Pytest configuration
    ├── test_kb_grounding.py            📋 Grounding tests
    ├── test_plan_schema.py             📋 Schema validation tests
    ├── test_validators.py              📋 Validator tests
    ├── test_mcp_tools.py               📋 MCP tool tests
    ├── test_parsers_cryptoperf.py      📋 CryptoPerf parser tests
    ├── test_parsers_testpmd.py         📋 testpmd parser tests
    ├── test_compare_runs.py            📋 Comparison tests
    ├── test_dataset_export.py          📋 Dataset export tests
    ├── test_eval_harness.py            📋 Eval harness tests
    ├── test_safety_policies.py         📋 Safety policy tests
    └── fixtures/
        ├── sample_logs/                📋 Test log fixtures
        ├── sample_plans/               📋 Test plan fixtures
        └── expected_metrics/           📋 Expected metric fixtures

```

## File Statistics

### Implemented Files (✅)
- Configuration: 5 files
- Core Models: 3 files
- KB Components: 4 files
- MCP Schemas: 2 files
- Documentation: 6 files
- Scripts: 3 files
- CI/CD: 1 file

**Total Implemented: 24 files (~3,500 lines)**

### Specified Files (📋)
- MCP Implementation: 2 files
- LangGraph: 3 files
- Benchmarks: 6 files
- Parsers: 4 files
- Tuning: 4 files
- Dataset: 3 files
- Evaluation: 2 files
- Fine-tuning: 2 files
- CLI: 1 file
- Sample Data: 12+ files
- Tests: 15+ files
- Documentation: 8 files
- Scripts: 4 files

**Total Specified: 66+ files (~11,500 lines)**

### Total Project Size
- **Files**: 90+ files
- **Lines of Code**: ~15,000 lines (when fully implemented)
- **Documentation**: ~6,000 lines
- **Tests**: ~2,000 lines

## Implementation Priority

### Phase 1: Core Functionality (Week 1-2)
1. MCP server and tools
2. LangGraph workflow
3. At least 1 benchmark adapter (CryptoPerf)
4. Basic parser for CryptoPerf
5. Simple tuning advisor

### Phase 2: Extended Benchmarks (Week 3)
1. testpmd adapter and parser
2. L3fwd adapter and parser
3. Enhanced tuning advisor with rules
4. Validation framework

### Phase 3: Dataset & Eval (Week 4)
1. Dataset export with redaction
2. Evaluation harness
3. Sample data and fixtures
4. Comprehensive tests

### Phase 4: Polish & Docs (Week 5)
1. Complete documentation
2. Optional fine-tuning
3. CI/CD refinement
4. Demo polish

## Key Files for Quick Start

To get started quickly, implement these files first:

1. `src/netbench/mcp_server/tools.py` - Core tool logic
2. `src/netbench/graph/workflow.py` - Workflow orchestration
3. `src/netbench/benchmarks/cryptoperf.py` - First benchmark
4. `src/netbench/parsing/cryptoperf_parser.py` - First parser
5. `src/netbench/app.py` - CLI interface

These 5 files (~2000 lines) will enable basic end-to-end functionality.

## Notes

- 📁 Directories marked with folder icon are created but empty
- ✅ Files marked with checkmark are fully implemented
- 📋 Files marked with clipboard are specified but need implementation
- All specified files have detailed implementation guidance in `IMPLEMENTATION_GUIDE.md`
- Sample data files are synthetic and clearly marked as such
- User-provided PDFs are not included in repository