# Architecture

## Components
- **KB ingest (LlamaIndex)**: builds a local vector index from PDFs.
- **Retriever**: top-k retrieval with citations.
- **LangGraph**: orchestrates classify → retrieve → plan → apply_tuning_advisor → validate → safety → tools.
- **MCP server**: deterministic tool boundary with Pydantic schemas.
- **SQLite store**: persists run records and artifacts.

## Data Flow
1) `ask/plan` → retrieve KB chunks
2) tuning advisor builds KB-grounded profile
3) MCP tool renders command scripts and parsing
4) artifacts written to `out/`
5) optional dataset export & evaluation

## Why LangGraph + MCP
LangGraph provides deterministic workflow control while MCP tools ensure all command outputs are schema validated and
repeatable without free-form LLM generation.
