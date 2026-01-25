#!/usr/bin/env bash
set -euo pipefail

uv run python -m netbench.app eval run --cases data/golden_prompts/eval_cases.yaml
