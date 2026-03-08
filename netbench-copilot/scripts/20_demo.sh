#!/usr/bin/env bash
set -euo pipefail

bash scripts/00_bootstrap.sh
bash scripts/10_build_index.sh

uv run python -m netbench.app ask --query "Define throughput metric."

NETBENCH_APPROVAL_TOKEN=demo uv run python -m netbench.app plan --benchmark cryptoperf --platform generic --nl "AES-GCM cryptoperf on 4 cores"

baseline=$(uv run python -m netbench.app parse --benchmark testpmd --run-dir data/sample_runs/testpmd_run_001 --store true | tail -n1 | cut -d= -f2)
candidate=$(uv run python -m netbench.app parse --benchmark testpmd --run-dir data/sample_runs/testpmd_run_001 --store true | tail -n1 | cut -d= -f2)

uv run python -m netbench.app compare --baseline "$baseline" --candidate "$candidate"
uv run python -m netbench.app dataset export --out ./out/dataset

uv run python -m netbench.app eval run --cases data/golden_prompts/eval_cases.yaml

echo "Demo complete"
