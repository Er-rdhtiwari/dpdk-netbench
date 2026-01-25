#!/usr/bin/env bash
set -euo pipefail

uv run python -m netbench.app dataset export --out ./out/dataset
