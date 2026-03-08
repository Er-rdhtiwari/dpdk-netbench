from __future__ import annotations

from typing import Callable
from pathlib import Path

from langgraph.graph import END, StateGraph

from netbench.config import settings
from netbench.graph.policies import enforce_grounding_or_not_found, has_citations, requires_approval
from netbench.graph.state import GraphState
from netbench.kb.citations import build_citations
from netbench.kb.retrieve import load_retriever
from netbench.mcp_server.server import MCPServer
from netbench.tuning.advisor import build_run_plan, build_tuning_profile
from netbench.eval.harness import run_eval


def classify_intent(state: GraphState) -> GraphState:
    if state.intent:
        return state
    if state.extra.get("log_paths"):
        state.intent = "parse"
    elif state.extra.get("baseline_metrics") and state.extra.get("candidate_metrics"):
        state.intent = "compare"
    elif state.extra.get("db_path") and state.extra.get("out_dir"):
        state.intent = "dataset"
    elif state.extra.get("eval_cases"):
        state.intent = "eval"
    elif state.query and state.benchmark:
        state.intent = "plan"
    elif state.query:
        state.intent = "ask"
    return state


def retrieve_kb(state: GraphState) -> GraphState:
    if not state.query and not state.nl_goal:
        return state
    retriever = load_retriever(settings.index_dir)
    if state.intent == "plan" and state.benchmark:
        query = (
            f"{state.benchmark} tuning HUGEPAGES IRQ_AFFINITY ISOLCPUS DISABLE_IRQBALANCE "
            "DISABLE_THP KERNEL_CMDLINE BIOS VERIFY_CMD"
        )
    else:
        query = state.query or state.nl_goal or ""
    chunks = retriever.retrieve(query, top_k=4)
    state.retrieved_chunks = [
        {"text": c.text, "score": c.score, "metadata": c.metadata} for c in chunks
    ]
    state.citations = [c.__dict__ for c in build_citations(chunks)]
    return state


def _retry_or_continue(state: GraphState) -> str:
    if not state.query and not state.nl_goal:
        return "build_plan"
    attempts = int(state.extra.get("retrieval_attempts", 0))
    if not state.retrieved_chunks and attempts < 2:
        state.extra["retrieval_attempts"] = attempts + 1
        return "retrieve_kb"
    return "build_plan"


def build_plan(state: GraphState) -> GraphState:
    if not state.benchmark or not state.platform or not state.nl_goal:
        return state
    state.run_plan = build_run_plan(
        benchmark=state.benchmark,
        platform=state.platform,
        nl_goal=state.nl_goal,
    )
    return state


def apply_tuning_advisor(state: GraphState) -> GraphState:
    if not state.run_plan:
        return state
    tuning, errors = build_tuning_profile(state.retrieved_chunks)
    if errors:
        state.errors.extend(errors)
    state.tuning_profile = tuning
    return state


def validate(state: GraphState) -> GraphState:
    if not state.run_plan or not state.tuning_profile:
        return state
    server = MCPServer()
    response = server.validate_plan({
        "run_yaml": state.run_plan,
        "tuning_profile": state.tuning_profile,
        "env_snapshot": {},
    })
    if not response["valid"]:
        state.errors.extend(response["reasons"])
    return state


def safety_gate(state: GraphState) -> GraphState:
    if requires_approval(state.tuning_profile) and not settings.approval_token:
        state.errors.append("Approval token required for BIOS/reboot steps")
    return state


def tool_execute(state: GraphState) -> GraphState:
    server = MCPServer()
    try:
        if state.intent == "ask":
            if not has_citations(state.citations):
                state.errors.append("NOT FOUND IN KB")
            return state
        if state.intent == "plan" and state.run_plan:
            response = server.render_command({
                "benchmark": state.run_plan.get("benchmark"),
                "run_yaml": state.run_plan,
                "scenario_key": list(state.run_plan.get("scenarios", {}).keys())[0],
            })
            state.cmd_sh = response["cmd_sh"]
        if state.intent == "parse":
            log_paths = state.extra.get("log_paths", [])
            response = server.parse_results({"benchmark": state.benchmark, "log_paths": log_paths})
            state.metrics = response["metrics"]
        if state.intent == "compare":
            response = server.compare_runs(
                {
                    "benchmark": state.benchmark,
                    "baseline_metrics": state.extra.get("baseline_metrics", {}),
                    "candidate_metrics": state.extra.get("candidate_metrics", {}),
                }
            )
            state.delta = response["delta"]
            state.summary_md = response["summary_md"]
        if state.intent == "dataset":
            response = server.build_dataset(
                {"db_path": str(state.extra.get("db_path")), "out_dir": str(state.extra.get("out_dir"))}
            )
            state.extra["dataset"] = response
        if state.intent == "explain":
            response = server.explain_metric({"metric_name": state.query or ""})
            state.extra["explain"] = response
        if state.intent == "eval":
            cases_path = state.extra.get("eval_cases")
            out_dir = state.extra.get("out_dir") or settings.out_dir
            if cases_path:
                report = run_eval(Path(cases_path), Path(out_dir))
                state.extra["eval_report"] = report
    except Exception as exc:  # pragma: no cover - defensive retry hook
        state.errors.append(f"tool_failure:{exc}")
    return state


def _retry_tool(state: GraphState) -> str:
    attempts = int(state.extra.get("tool_attempts", 0))
    if any(err.startswith("tool_failure") for err in state.errors) and attempts < 2:
        state.extra["tool_attempts"] = attempts + 1
        return "tool_execute"
    return "finalize"


def finalize(state: GraphState) -> GraphState:
    if state.intent in {"ask", "plan"}:
        grounded = has_citations(state.citations)
        not_found = enforce_grounding_or_not_found(grounded)
        if not_found:
            state.errors.append(not_found)
    return state


def build_workflow() -> Callable[[GraphState], GraphState]:
    graph = StateGraph(GraphState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_kb", retrieve_kb)
    graph.add_node("build_plan", build_plan)
    graph.add_node("apply_tuning_advisor", apply_tuning_advisor)
    graph.add_node("validate", validate)
    graph.add_node("safety_gate", safety_gate)
    graph.add_node("tool_execute", tool_execute)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "retrieve_kb")
    graph.add_conditional_edges("retrieve_kb", _retry_or_continue)
    graph.add_edge("build_plan", "apply_tuning_advisor")
    graph.add_edge("apply_tuning_advisor", "validate")
    graph.add_edge("validate", "safety_gate")
    graph.add_edge("safety_gate", "tool_execute")
    graph.add_conditional_edges("tool_execute", _retry_tool)
    graph.add_edge("finalize", END)

    return graph.compile()
