#!/usr/bin/env bash
set -euo pipefail

uv run python -m netbench.app finetune lora --dataset ./out/dataset/sft_train.jsonl --val ./out/dataset/sft_val.jsonl
