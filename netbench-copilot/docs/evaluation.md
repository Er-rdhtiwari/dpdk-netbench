# Evaluation

## Categories
- Grounding: enforce `NOT FOUND IN KB` when citations are missing.
- Tool correctness: validate schemas and command requirements.
- Parser correctness: unit tests against sample logs.
- Safety: BIOS/reboot steps require approval token.

## Adding cases
Edit `data/golden_prompts/eval_cases.yaml` and add a case with expected patterns.

## CI gating
CI runs `pytest` and a small demo smoke test. Failed grounding or schema checks will fail the pipeline.
