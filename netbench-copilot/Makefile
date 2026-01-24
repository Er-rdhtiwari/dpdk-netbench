.PHONY: help bootstrap install index demo test lint format clean dataset eval finetune

help:
	@echo "NetBench Copilot - Makefile Commands"
	@echo "====================================="
	@echo "bootstrap    - Initial setup (install uv, create venv, install deps)"
	@echo "install      - Install dependencies"
	@echo "index        - Build KB index from PDFs"
	@echo "demo         - Run end-to-end demo"
	@echo "test         - Run all tests"
	@echo "lint         - Run linters (ruff, mypy)"
	@echo "format       - Format code (black, ruff)"
	@echo "clean        - Clean cache and build artifacts"
	@echo "dataset      - Export dataset from stored runs"
	@echo "eval         - Run evaluation harness"
	@echo "finetune     - Run optional LoRA fine-tuning"

bootstrap:
	@echo "Running bootstrap script..."
	@bash scripts/00_bootstrap.sh

install:
	@echo "Installing dependencies with uv..."
	uv sync

index:
	@echo "Building KB index..."
	@bash scripts/10_build_index.sh

demo:
	@echo "Running demo..."
	@bash scripts/20_demo.sh

test:
	@echo "Running tests..."
	uv run pytest tests/ -v --cov=src/netbench --cov-report=term-missing

lint:
	@echo "Running linters..."
	uv run ruff check src/ tests/
	uv run mypy src/

format:
	@echo "Formatting code..."
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean:
	@echo "Cleaning cache and artifacts..."
	rm -rf .cache/
	rm -rf out/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

dataset:
	@echo "Exporting dataset..."
	@bash scripts/40_export_dataset.sh

eval:
	@echo "Running evaluation harness..."
	@bash scripts/50_run_eval.sh

finetune:
	@echo "Running optional fine-tuning..."
	@bash scripts/60_optional_finetune.sh