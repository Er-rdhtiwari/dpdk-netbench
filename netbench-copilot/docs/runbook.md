# Runbook

## Add PDFs
1) Place PDFs in `data/kb/pdfs/`
2) Register them in `data/kb/manifest.yaml` or use:
   ```bash
   bash scripts/30_add_pdf.sh /path/to/file.pdf
   ```

## Build Index
```bash
bash scripts/10_build_index.sh
```
`scripts/00_bootstrap.sh` generates a synthetic sample PDF if none exist.

## Run Demo
```bash
bash scripts/20_demo.sh
```

## Plan a Benchmark
```bash
uv run python -m netbench.app plan --benchmark cryptoperf --platform generic --nl "AES-GCM on 4 cores"
```
If the tuning profile includes BIOS/reboot steps, set `NETBENCH_APPROVAL_TOKEN` before generating commands.

## Parse and Compare
```bash
uv run python -m netbench.app parse --benchmark testpmd --run-dir data/sample_runs/testpmd_run_001 --store true
uv run python -m netbench.app compare --baseline <run_id> --candidate <run_id>
```

## Export Dataset
```bash
uv run python -m netbench.app dataset export --out ./out/dataset
```

## Run Evaluation
```bash
uv run python -m netbench.app eval run --cases data/golden_prompts/eval_cases.yaml
```

## Optional LoRA Finetune
```bash
uv sync --extra finetune
uv run python -m netbench.app finetune lora --dataset ./out/dataset/sft_train.jsonl --val ./out/dataset/sft_val.jsonl
```

## Troubleshooting
- If answers return `NOT FOUND IN KB`, ensure PDFs are indexed and contain the requested facts.
- If index build fails, verify PDFs exist in `data/kb/pdfs/` and manifest entries are correct.
