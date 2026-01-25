# Tuning Advisor

## Sources
- RAG-sourced: tuning recommendations and parameter meanings.
- Rule-sourced: deterministic checks (e.g., missing core list warnings).

## Updating rules
Edit `src/netbench/tuning/rules.py` to add new deterministic checks.

## Verification
Use the verification commands in `tuning_profile.yaml` to confirm changes on the target system.
