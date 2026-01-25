from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores.simple import SimpleVectorStore
from pypdf import PdfReader


@dataclass
class IngestStats:
    docs: int
    chunks: int
    manifest_hash: str


class SimpleHashEmbedding(BaseEmbedding):
    dim: int = 256

    def _embed_text(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in text.lower().split():
            h = hashlib.md5(token.encode("utf-8")).hexdigest()
            idx = int(h[:8], 16) % self.dim
            vec[idx] += 1.0
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._embed_text(text)

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._embed_text(query)

    async def _aget_text_embedding(self, text: str) -> list[float]:
        return self._embed_text(text)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._embed_text(query)

    def get_text_embedding(self, text: str) -> list[float]:
        return self._embed_text(text)

    async def aget_text_embedding(self, text: str) -> list[float]:
        return self._embed_text(text)

    def get_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    async def aget_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]


def _manifest_hash(manifest_path: Path) -> str:
    raw = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else ""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _is_heading(line: str) -> bool:
    if not line:
        return False
    if line.startswith("SECTION:"):
        return True
    if line.endswith(":") and len(line) < 60:
        return True
    return line.isupper() and len(line) < 80


def _split_sections(text: str) -> list[tuple[str | None, str]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return [(None, text)]
    sections: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in lines:
        if _is_heading(line):
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines)))
                current_lines = []
            current_heading = line
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_heading, "\n".join(current_lines)))
    return sections or [(None, text)]


def _load_manifest(manifest_path: Path) -> list[dict]:
    if not manifest_path.exists():
        return []
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    return data.get("pdfs", [])


def _iter_documents(pdf_path: Path, meta: dict) -> Iterable[Document]:
    reader = PdfReader(str(pdf_path))
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for section_index, (heading, section_text) in enumerate(_split_sections(text)):
            metadata = {
                "source_file": pdf_path.name,
                "page_start": page_index,
                "page_end": page_index,
                "section": heading,
                "vendor": meta.get("vendor"),
                "platform": meta.get("platform"),
                "version": meta.get("version"),
                "tags": meta.get("tags", []),
                "doc_id": f"{pdf_path.name}:{page_index}:{section_index}",
            }
            yield Document(text=section_text, metadata=metadata)


def build_index(manifest_path: Path, pdf_dir: Path, index_dir: Path) -> IngestStats:
    pdf_entries = _load_manifest(manifest_path)
    docs: list[Document] = []
    for entry in pdf_entries:
        pdf_path = pdf_dir / entry["file"]
        if not pdf_path.exists():
            continue
        docs.extend(list(_iter_documents(pdf_path, entry)))

    parser = SentenceSplitter(chunk_size=512, chunk_overlap=80)
    nodes = parser.get_nodes_from_documents(docs)
    for idx, node in enumerate(nodes):
        node.metadata["chunk_id"] = f"chunk-{idx}"  # stable enough for demo

    embed_model = SimpleHashEmbedding()
    vector_store = SimpleVectorStore()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes, embed_model=embed_model, storage_context=storage_context)

    index_dir.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(index_dir))

    manifest_hash = _manifest_hash(manifest_path)
    (index_dir / "manifest.sha256").write_text(manifest_hash, encoding="utf-8")

    return IngestStats(docs=len(docs), chunks=len(nodes), manifest_hash=manifest_hash)
