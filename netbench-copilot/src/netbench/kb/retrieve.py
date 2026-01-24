"""KB retrieval using LlamaIndex."""

from pathlib import Path
from typing import List, Optional

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage

from netbench.config import settings
from netbench.store.models import Citation


class KBRetriever:
    """Retrieve relevant chunks from KB index."""

    def __init__(self, index_path: Optional[Path] = None) -> None:
        """Initialize the retriever.

        Args:
            index_path: Path to vector index. Uses settings.index_path if None.
        """
        self.index_path = index_path or settings.index_path
        self.index: Optional[VectorStoreIndex] = None

    def load_index(self) -> VectorStoreIndex:
        """Load the vector index from disk.

        Returns:
            Loaded VectorStoreIndex

        Raises:
            FileNotFoundError: If index doesn't exist
        """
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Index not found at {self.index_path}. Run 'make index' to build it."
            )

        storage_context = StorageContext.from_defaults(persist_dir=str(self.index_path))
        self.index = load_index_from_storage(storage_context)
        return self.index

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> List[Citation]:
        """Retrieve relevant chunks for a query.

        Args:
            query: Query string
            top_k: Number of chunks to retrieve. Uses settings.top_k if None.
            similarity_threshold: Minimum similarity score. Uses settings.similarity_threshold if None.

        Returns:
            List of Citation objects with retrieved chunks and metadata
        """
        if self.index is None:
            self.load_index()

        top_k = top_k or settings.top_k
        similarity_threshold = similarity_threshold or settings.similarity_threshold

        # Create retriever
        retriever = self.index.as_retriever(similarity_top_k=top_k)

        # Retrieve nodes
        nodes = retriever.retrieve(query)

        # Convert to citations
        citations = []
        for idx, node in enumerate(nodes):
            # Filter by similarity threshold
            if node.score < similarity_threshold:
                continue

            metadata = node.node.metadata
            citation = Citation(
                doc_id=node.node.id_,
                chunk_id=f"chunk_{idx}",
                source_file=metadata.get("source_file", "unknown"),
                page_start=metadata.get("page_start", 0),
                page_end=metadata.get("page_end", 0),
                section=metadata.get("section"),
                score=node.score,
                text_snippet=node.node.get_content()[:500],  # Truncate for display
            )
            citations.append(citation)

        return citations

    def retrieve_with_context(
        self,
        query: str,
        benchmark: Optional[str] = None,
        platform: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[Citation]:
        """Retrieve chunks with optional metadata filtering.

        Args:
            query: Query string
            benchmark: Filter by benchmark tag
            platform: Filter by platform
            top_k: Number of chunks to retrieve

        Returns:
            List of Citation objects
        """
        # Build enhanced query with context
        enhanced_query = query
        if benchmark:
            enhanced_query = f"{query} (benchmark: {benchmark})"
        if platform:
            enhanced_query = f"{enhanced_query} (platform: {platform})"

        citations = self.retrieve(query=enhanced_query, top_k=top_k)

        # Post-filter by metadata if needed
        if benchmark or platform:
            filtered = []
            for citation in citations:
                # Load full metadata from index
                if self.index:
                    node = self.index.docstore.get_document(citation.doc_id)
                    if node:
                        metadata = node.metadata
                        benchmark_tags = metadata.get("benchmark_tags", "").split(",")
                        platform_match = metadata.get("platform", "").lower()

                        # Check filters
                        if benchmark and benchmark.lower() not in [t.lower() for t in benchmark_tags]:
                            continue
                        if platform and platform.lower() not in platform_match:
                            continue

                filtered.append(citation)
            return filtered

        return citations

    def check_grounding(self, claim: str, citations: List[Citation]) -> bool:
        """Check if a claim is grounded in the provided citations.

        Args:
            claim: Claim to verify
            citations: List of citations to check against

        Returns:
            True if claim appears grounded, False otherwise
        """
        if not citations:
            return False

        # Simple keyword-based grounding check
        # In production, use more sophisticated semantic similarity
        claim_lower = claim.lower()
        claim_keywords = set(claim_lower.split())

        for citation in citations:
            snippet_lower = citation.text_snippet.lower()
            snippet_keywords = set(snippet_lower.split())

            # Check for keyword overlap (simple heuristic)
            overlap = claim_keywords & snippet_keywords
            if len(overlap) >= min(3, len(claim_keywords) // 2):
                return True

        return False

# Made with Bob
