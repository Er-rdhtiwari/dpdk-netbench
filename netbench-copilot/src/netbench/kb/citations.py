"""Citation management and enforcement."""

import json
from pathlib import Path
from typing import Any, Dict, List

from netbench.store.models import Citation


class CitationManager:
    """Manage citations and enforce grounding requirements."""

    NOT_FOUND_MESSAGE = "NOT FOUND IN KB"

    @staticmethod
    def format_citation(citation: Citation) -> str:
        """Format a citation for display.

        Args:
            citation: Citation object

        Returns:
            Formatted citation string
        """
        section_str = f" ({citation.section})" if citation.section else ""
        return (
            f"[{citation.source_file}, "
            f"pages {citation.page_start}-{citation.page_end}{section_str}]"
        )

    @staticmethod
    def format_citations_list(citations: List[Citation]) -> str:
        """Format a list of citations for display.

        Args:
            citations: List of Citation objects

        Returns:
            Formatted citations string
        """
        if not citations:
            return "No citations available"

        formatted = []
        for idx, citation in enumerate(citations, start=1):
            formatted.append(
                f"{idx}. {CitationManager.format_citation(citation)} "
                f"(score: {citation.score:.3f})"
            )

        return "\n".join(formatted)

    @staticmethod
    def save_citations(citations: List[Citation], output_path: Path) -> None:
        """Save citations to JSON file.

        Args:
            citations: List of Citation objects
            output_path: Path to save citations JSON
        """
        citations_data = [citation.model_dump() for citation in citations]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(citations_data, f, indent=2, default=str)

    @staticmethod
    def load_citations(citations_path: Path) -> List[Citation]:
        """Load citations from JSON file.

        Args:
            citations_path: Path to citations JSON file

        Returns:
            List of Citation objects
        """
        with open(citations_path, "r") as f:
            citations_data = json.load(f)

        return [Citation(**c) for c in citations_data]

    @staticmethod
    def enforce_grounding(
        response: str,
        citations: List[Citation],
        min_citations: int = 1,
    ) -> str:
        """Enforce grounding requirement on a response.

        If response makes factual claims but has insufficient citations,
        replace with NOT_FOUND_MESSAGE.

        Args:
            response: Response text to check
            citations: Available citations
            min_citations: Minimum number of citations required

        Returns:
            Original response if grounded, NOT_FOUND_MESSAGE otherwise
        """
        # Check if response contains factual claims (heuristic)
        factual_indicators = [
            "recommend",
            "should",
            "must",
            "configure",
            "set",
            "use",
            "enable",
            "disable",
            "optimal",
            "best",
            "performance",
        ]

        response_lower = response.lower()
        has_factual_claims = any(indicator in response_lower for indicator in factual_indicators)

        if has_factual_claims and len(citations) < min_citations:
            return CitationManager.NOT_FOUND_MESSAGE

        return response

    @staticmethod
    def extract_citation_snippets(citations: List[Citation]) -> List[str]:
        """Extract text snippets from citations.

        Args:
            citations: List of Citation objects

        Returns:
            List of text snippets
        """
        return [citation.text_snippet for citation in citations]

    @staticmethod
    def build_context_from_citations(citations: List[Citation]) -> str:
        """Build a context string from citations for LLM prompting.

        Args:
            citations: List of Citation objects

        Returns:
            Context string with numbered citations
        """
        if not citations:
            return "No relevant information found in knowledge base."

        context_parts = ["Retrieved information from knowledge base:\n"]

        for idx, citation in enumerate(citations, start=1):
            context_parts.append(
                f"\n[{idx}] Source: {citation.source_file}, "
                f"Pages {citation.page_start}-{citation.page_end}\n"
                f"{citation.text_snippet}\n"
            )

        return "".join(context_parts)

    @staticmethod
    def validate_response_grounding(
        response: str,
        citations: List[Citation],
        strict: bool = True,
    ) -> Dict[str, Any]:
        """Validate that a response is properly grounded in citations.

        Args:
            response: Response text to validate
            citations: Available citations
            strict: If True, require strong grounding evidence

        Returns:
            Validation result dictionary with 'is_grounded' and 'details'
        """
        if not citations:
            return {
                "is_grounded": False,
                "details": "No citations provided",
                "recommendation": "Use NOT_FOUND_MESSAGE",
            }

        # Extract key claims from response (simplified)
        response_sentences = [s.strip() for s in response.split(".") if s.strip()]

        grounded_count = 0
        ungrounded_claims = []

        for sentence in response_sentences:
            # Check if sentence is grounded in any citation
            is_grounded = False
            sentence_lower = sentence.lower()

            for citation in citations:
                snippet_lower = citation.text_snippet.lower()

                # Simple keyword overlap check
                sentence_words = set(sentence_lower.split())
                snippet_words = set(snippet_lower.split())
                overlap = sentence_words & snippet_words

                if len(overlap) >= 3:  # At least 3 common words
                    is_grounded = True
                    break

            if is_grounded:
                grounded_count += 1
            else:
                ungrounded_claims.append(sentence)

        total_claims = len(response_sentences)
        grounding_ratio = grounded_count / total_claims if total_claims > 0 else 0

        threshold = 0.7 if strict else 0.5
        is_grounded = grounding_ratio >= threshold

        return {
            "is_grounded": is_grounded,
            "grounding_ratio": grounding_ratio,
            "grounded_count": grounded_count,
            "total_claims": total_claims,
            "ungrounded_claims": ungrounded_claims[:3],  # Show first 3
            "recommendation": "OK" if is_grounded else "Use NOT_FOUND_MESSAGE or revise",
        }

# Made with Bob
