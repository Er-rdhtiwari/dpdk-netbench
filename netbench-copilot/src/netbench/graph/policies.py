from __future__ import annotations

from typing import Iterable


def has_citations(citations: Iterable[dict]) -> bool:
    return any(bool(c.get("source_file")) for c in citations)


def requires_approval(tuning_profile: dict | None) -> bool:
    if not tuning_profile:
        return False
    return bool(tuning_profile.get("requires_approval"))


def enforce_grounding_or_not_found(found: bool) -> str | None:
    if not found:
        return "NOT FOUND IN KB"
    return None
