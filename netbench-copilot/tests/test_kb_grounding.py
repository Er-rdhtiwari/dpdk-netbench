from __future__ import annotations

from pathlib import Path

import yaml

from netbench.kb.ingest import build_index
from netbench.kb.retrieve import load_retriever
from tests.utils import SAMPLE_LINES, build_pdf


def test_not_found_in_kb(tmp_path: Path) -> None:
    pdf_dir = tmp_path / "pdfs"
    pdf_path = pdf_dir / "sample.pdf"
    build_pdf(pdf_path, SAMPLE_LINES)

    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "pdfs": [
                    {
                        "file": "sample.pdf",
                        "vendor": "synthetic",
                        "platform": "generic",
                        "version": "0.1",
                        "tags": ["tuning"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    index_dir = tmp_path / "index"
    build_index(manifest, pdf_dir, index_dir)
    retriever = load_retriever(index_dir)

    chunks = retriever.retrieve("microcode version", top_k=3)
    assert chunks == []
