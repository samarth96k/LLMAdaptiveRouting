"""
LangGraph Builder — constructs and compiles the adaptive routing StateGraph.

This is the heart of the system. The graph has:
  - 5 nodes (analyze, route, execute_single, execute_multi, evaluate+feedback)
  - Conditional branching after routing (single vs multi)
  - Linear flow otherwise

Graph structure:

  START → analyze_and_estimate → route_task ─┬─→ execute_single ─┬─→ evaluate_output → log_feedback → END
                                              └─→ execute_multi  ─┘
"""

from langgraph.graph import StateGraph, END

from .state import TaskState
from .nodes import (
    analyze_and_estimate,
    route_task,
    execute_single,
    execute_multi,
    evaluate_output,
    log_feedback,
)


def _routing_branch(state: TaskState) -> str:
    """Conditional edge: pick execution path based on routing decision."""
    if state.get("route") == "multi_agent":
        return "execute_multi"
    return "execute_single"


def build_adaptive_graph() -> StateGraph:
    """
    Build the LangGraph StateGraph for adaptive routing.

    Returns a compiled graph ready to invoke with .invoke(state_dict).
    """
    graph = StateGraph(TaskState)

    # ── Add nodes ────────────────────────────────────────────────────────
    graph.add_node("analyze_and_estimate", analyze_and_estimate)
    graph.add_node("route_task", route_task)
    graph.add_node("execute_single", execute_single)
    graph.add_node("execute_multi", execute_multi)
    graph.add_node("evaluate_output", evaluate_output)
    graph.add_node("log_feedback", log_feedback)

    # ── Define edges ─────────────────────────────────────────────────────
    graph.set_entry_point("analyze_and_estimate")

    graph.add_edge("analyze_and_estimate", "route_task")

    # conditional branch after routing
    graph.add_conditional_edges(
        "route_task",
        _routing_branch,
        {
            "execute_single": "execute_single",
            "execute_multi": "execute_multi",
        },
    )

    # both execution paths converge to evaluation
    graph.add_edge("execute_single", "evaluate_output")
    graph.add_edge("execute_multi", "evaluate_output")

    graph.add_edge("evaluate_output", "log_feedback")
    graph.add_edge("log_feedback", END)

    # ── Compile ──────────────────────────────────────────────────────────
    compiled = graph.compile()

    return compiled


# convenience: pre-built graph instance
adaptive_router = build_adaptive_graph()
