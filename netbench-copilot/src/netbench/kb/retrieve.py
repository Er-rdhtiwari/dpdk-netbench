from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.embeddings import BaseEmbedding

from netbench.kb.ingest import SimpleHashEmbedding


@dataclass
class RetrievedChunk:
    text: str
    score: float
    metadata: dict


class Retriever:
    def __init__(self, index_dir: Path, embed_model: BaseEmbedding | None = None):
        self.index_dir = index_dir
        self.embed_model = embed_model or SimpleHashEmbedding()
        self.index = self._load_index()

    def _load_index(self):
        storage_context = StorageContext.from_defaults(persist_dir=str(self.index_dir))
        return load_index_from_storage(storage_context, embed_model=self.embed_model)

    def retrieve(self, query: str, top_k: int = 4, min_score: float = 0.2) -> list[RetrievedChunk]:
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(query)
        keywords = {tok for tok in query.lower().split() if len(tok) > 3}
        chunks: list[RetrievedChunk] = []
        for result in results:
            score = float(result.score or 0.0)
            if score < min_score:
                continue
            if keywords and not any(tok in result.node.text.lower() for tok in keywords):
                continue
            chunks.append(
                RetrievedChunk(
                    text=result.node.text,
                    score=score,
                    metadata=result.node.metadata,
                )
            )
        return chunks


def load_retriever(index_dir: Path) -> Retriever:
    if not index_dir.exists():
        raise FileNotFoundError(f"Index directory not found: {index_dir}")
    return Retriever(index_dir=index_dir)
