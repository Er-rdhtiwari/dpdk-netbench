from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalResult:
    total: int
    passed: int

    @property
    def score(self) -> float:
        return (self.passed / self.total) if self.total else 0.0


def rubric(results: list[bool]) -> EvalResult:
    return EvalResult(total=len(results), passed=sum(1 for r in results if r))
