from __future__ import annotations

from abc import ABC, abstractmethod


class BenchmarkAdapter(ABC):
    name: str

    @abstractmethod
    def render_command(self, run_yaml: dict, scenario_key: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def parse_results(self, log_paths: list[str]) -> tuple[dict, list[str]]:
        raise NotImplementedError
