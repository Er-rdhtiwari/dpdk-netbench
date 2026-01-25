from __future__ import annotations

from pathlib import Path


def read_logs(log_paths: list[str]) -> str:
    content = []
    for path in log_paths:
        text = Path(path).read_text(encoding="utf-8")
        content.append(text)
    return "\n".join(content)
