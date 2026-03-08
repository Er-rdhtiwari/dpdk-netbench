# Dataset

## Export
`python -m netbench.app dataset export --out ./out/dataset`

## Contents
- `run_records.jsonl`: full run records
- `sft_train.jsonl`, `sft_val.jsonl`: SFT data with system/user/assistant messages
- `eval_cases.json`: eval metadata

## Redaction
Hostnames, IPs, and PCI BDFs are replaced with placeholders.
