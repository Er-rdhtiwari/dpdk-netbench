from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from netbench.kb.retrieve import RetrievedChunk


@dataclass
class Citation:
    doc_id: str
    chunk_id: str
    source_file: str
    page_start: int
    page_end: int
    section: str | None


def build_citations(chunks: Iterable[RetrievedChunk]) -> list[Citation]:
    citations: list[Citation] = []
    for chunk in chunks:
        meta = chunk.metadata
        citations.append(
            Citation(
                doc_id=str(meta.get("doc_id", "")),
                chunk_id=str(meta.get("chunk_id", "")),
                source_file=str(meta.get("source_file", "")),
                page_start=int(meta.get("page_start", 0) or 0),
                page_end=int(meta.get("page_end", 0) or 0),
                section=meta.get("section"),
            )
        )
    return citations


def write_citations(path: Path, citations: list[Citation]) -> None:
    payload = {
        "citations": [
            {
                "doc_id": c.doc_id,
                "chunk_id": c.chunk_id,
                "source_file": c.source_file,
                "page_start": c.page_start,
                "page_end": c.page_end,
                "section": c.section,
            }
            for c in citations
        ]
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def citations_summary(citations: list[Citation]) -> str:
    if not citations:
        return ""
    parts = []
    for c in citations:
        if c.source_file:
            parts.append(f"{c.source_file}:{c.page_start}-{c.page_end}")
    return ", ".join(parts)
