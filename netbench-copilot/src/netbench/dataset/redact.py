from __future__ import annotations

import re


HOST_RE = re.compile(r"\b[a-zA-Z0-9_-]+\.(local|corp|internal)\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
BDF_RE = re.compile(r"\b[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.\d\b")


def redact(text: str) -> str:
    text = HOST_RE.sub("<HOST>", text)
    text = IP_RE.sub("<IP>", text)
    text = BDF_RE.sub("<BDF>", text)
    return text
