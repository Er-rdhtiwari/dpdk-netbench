SHELL := /bin/bash

.PHONY: bootstrap index demo test eval dataset lint

bootstrap:
	uv sync
	bash scripts/00_bootstrap.sh

index:
	bash scripts/10_build_index.sh

demo:
	bash scripts/20_demo.sh

test:
	uv run pytest

eval:
	uv run python -m netbench.app eval run --cases data/golden_prompts/eval_cases.yaml

dataset:
	uv run python -m netbench.app dataset export --out ./out/dataset

lint:
	uv run ruff check src tests
