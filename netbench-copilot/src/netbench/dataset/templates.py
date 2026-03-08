from __future__ import annotations

SYSTEM_PROMPT = "You are NetBench Copilot. Follow KB grounding rules strictly."

PLAN_TEMPLATE = """Goal: {nl_goal}
Env summary: {env_summary}
Return run.yaml and tuning_profile.yaml."""

PARSE_TEMPLATE = """Parse the following log snippet into normalized metrics JSON:
{log_snippet}
"""

COMPARE_TEMPLATE = """Compare baseline and candidate metrics and summarize deltas:
Baseline: {baseline}
Candidate: {candidate}
"""
