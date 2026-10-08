"""
Experiment Runner.

Phase 1 experiments:

1. Single LLM baseline
2. Multi-Agent baseline
3. Adaptive LLM Routing
4. Adaptive Routing with Feedback Loop

Phase 2 statistical significance analysis is intentionally
not included in this Phase 1 version.
"""

import time
from typing import Any, Dict, List

from ..agents.single_llm import run_single_llm
from ..agents.multi_agent import run_multi_agent
from ..graph.nodes import (
    analyze_and_estimate,
    route_task,
    evaluate_output,
    log_feedback,
)
from ..evaluation.metrics import compute_run_metrics
import json
from pathlib import Path

# ============================================================
# SINGLE LLM EXPERIMENT
# ============================================================

def run_experiment_single_llm(
    tasks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Run all tasks using the Single LLM baseline.
    """

    results = []

    for task in tasks:

        start_time = time.time()

        try:

            result = run_single_llm(
                task["prompt"],
                task.get("task_type", "general"),
            )

            response = result.get(
                "response",
                ""
            )

            model_used = result.get(
                "model_used",
                "groq"
            )

            intermediate_steps = result.get(
                "intermediate_steps",
                []
            )

            error = None

        except Exception as exc:

            response = ""
            model_used = "error"
            intermediate_steps = []
            error = str(exc)

        end_time = time.time()
        eval_state = {
            "prompt": task["prompt"],
            "ground_truth": task.get("ground_truth", ""),
            "response": response,
        }

        eval_state = evaluate_output(eval_state)

        accuracy = eval_state.get("accuracy_score", 0.0)
        quality = eval_state.get("quality_score", 0.0)
        results.append({
            "task_id": task.get("task_id"),
            "prompt": task["prompt"],
            "task_type": task.get(
                "task_type",
                "general"
            ),
            "ground_truth": task.get(
                "ground_truth",
                ""
            ),
            "response": response,
            "model_used": model_used,
            "intermediate_steps": intermediate_steps,
            "latency": end_time - start_time,
            "accuracy": accuracy,
            "quality": quality,
            "tokens": result.get("token_usage", {}).get("total", 0),
            "cost": 0.0,
            "error": error,
        })

    return results


# ============================================================
# MULTI-AGENT EXPERIMENT
# ============================================================

def run_experiment_multi(
    tasks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Run all tasks using the Multi-Agent baseline.
    """

    results = []

    for task in tasks:

        start_time = time.time()

        try:

            result = run_multi_agent(
                task["prompt"]
            )

            response = result.get(
                "response",
                ""
            )

            model_used = result.get(
                "model_used",
                "groq"
            )

            intermediate_steps = result.get(
                "intermediate_steps",
                []
            )

            error = None

        except Exception as exc:

            response = ""
            model_used = "error"
            intermediate_steps = []
            error = str(exc)

        end_time = time.time()
        eval_state = {
            "prompt": task["prompt"],
            "ground_truth": task.get("ground_truth", ""),
            "response": response,
        }

        eval_state = evaluate_output(eval_state)

        accuracy = eval_state.get("accuracy_score", 0.0)
        quality = eval_state.get("quality_score", 0.0)

        results.append({
            "task_id": task.get("task_id"),
            "prompt": task["prompt"],
            "task_type": task.get(
                "task_type",
                "general"
            ),
            "ground_truth": task.get(
                "ground_truth",
                ""
            ),
            "response": response,
            "model_used": model_used,
            "intermediate_steps": intermediate_steps,
            "latency": end_time - start_time,
            "accuracy": accuracy,
            "quality": quality,
            "tokens": 0,
            "cost": 0.0,
            "error": error,
        })

    return results


# ============================================================
# ADAPTIVE ROUTING EXPERIMENT
# ============================================================

def run_experiment_adaptive(
    tasks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Run tasks using the Phase 1 adaptive routing system.

    Flow:

        Complexity Analysis
                ↓
             Routing
             ↙     ↘
        Single      Multi-Agent
                ↓
             Evaluation
    """

    results = []

    for task in tasks:

        start_time = time.time()

        state = {
            "task_id": task.get("task_id"),
            "prompt": task["prompt"],
            "task_type": task.get(
                "task_type",
                "general"
            ),
            "ground_truth": task.get(
                "ground_truth",
                ""
            ),
            "start_time": start_time,
        }

        try:

            # ------------------------------------------------
            # Complexity analysis
            # ------------------------------------------------

            state = analyze_and_estimate(
                state
            )

            # ------------------------------------------------
            # Routing
            # ------------------------------------------------

            state = route_task(
                state
            )

            # ------------------------------------------------
            # Execution
            # ------------------------------------------------

            if state["route"] == "single_llm":

                result = run_single_llm(
                    task["prompt"],
                    task.get(
                        "task_type",
                        "general"
                    )
                )

            else:

                result = run_multi_agent(
                    task["prompt"]
                )

            state["response"] = result.get(
                "response",
                ""
            )

            state["model_used"] = result.get(
                "model_used",
                "groq"
            )

            state["intermediate_steps"] = result.get(
                "intermediate_steps",
                []
            )

            # ------------------------------------------------
            # Evaluation
            # ------------------------------------------------

            state = evaluate_output(
                state
            )

            # ------------------------------------------------
            # Feedback
            # ------------------------------------------------

            state = log_feedback(
                state
            )

            error = None

        except Exception as exc:

            state["response"] = ""
            state["model_used"] = "error"
            state["accuracy_score"] = 0.0
            state["quality_score"] = 0.0
            state["latency_seconds"] = (
                time.time() - start_time
            )
            error = str(exc)

        end_time = time.time()

        state["latency_seconds"] = (
            end_time - start_time
        )

        results.append({
            "task_id": state.get("task_id"),
            "prompt": state.get("prompt"),
            "task_type": state.get(
                "task_type",
                "general"
            ),
            "ground_truth": state.get(
                "ground_truth",
                ""
            ),
            "complexity_score": state.get(
                "complexity_score",
                0.0
            ),
            "route": state.get(
                "route",
                "unknown"
            ),
            "routing_confidence": state.get(
                "routing_confidence",
                0.0
            ),
            "routing_reason": state.get(
                "routing_reason",
                ""
            ),
            "response": state.get(
                "response",
                ""
            ),
            "model_used": state.get(
                "model_used",
                "unknown"
            ),
            "accuracy": state.get(
                "accuracy_score",
                0.0
            ),
            "quality": state.get(
                "quality_score",
                0.0
            ),
            "latency": state.get(
                "latency_seconds",
                0.0
            ),
            "tokens": state.get(
                "token_usage",
                0
            ),
            "cost": state.get(
                "estimated_cost",
                0.0
            ),
            "routing_was_correct": state.get(
                "routing_was_correct",
                True
            ),
            "error": error,
        })

    return results


# ============================================================
# ADAPTIVE + FEEDBACK EXPERIMENT
# ============================================================

def run_experiment_adaptive_feedback(
    tasks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Run adaptive routing with the feedback loop enabled.

    Feedback from previous tasks is used to adapt the routing
    threshold through the existing FeedbackStore mechanism.
    """

    results = []

    # Import here to avoid unnecessary initialization when
    # the feedback experiment is not being executed.
    from ..evaluation.feedback import FeedbackStore

    feedback_store = FeedbackStore()

    for task in tasks:

        start_time = time.time()

        state = {
            "task_id": task.get("task_id"),
            "prompt": task["prompt"],
            "task_type": task.get(
                "task_type",
                "general"
            ),
            "ground_truth": task.get(
                "ground_truth",
                ""
            ),
            "start_time": start_time,
        }

        try:

            # ------------------------------------------------
            # Complexity analysis
            # ------------------------------------------------

            state = analyze_and_estimate(
                state
            )

            # ------------------------------------------------
            # Routing
            # ------------------------------------------------

            state = route_task(
                state
            )

            # ------------------------------------------------
            # Execution
            # ------------------------------------------------

            if state["route"] == "single_llm":

                result = run_single_llm(
                    task["prompt"],
                    task.get(
                        "task_type",
                        "general"
                    )
                )

            else:

                result = run_multi_agent(
                    task["prompt"]
                )

            state["response"] = result.get(
                "response",
                ""
            )

            state["model_used"] = result.get(
                "model_used",
                "groq"
            )

            # ------------------------------------------------
            # Evaluation
            # ------------------------------------------------

            state = evaluate_output(
                state
            )

            # ------------------------------------------------
            # Feedback
            # ------------------------------------------------

            state = log_feedback(
                state
            )

            # Store feedback using the existing Phase 1
            # feedback mechanism.
            try:
                feedback_store.log(
    {
        "task_id": state.get("task_id"),
        "complexity_score": state.get("complexity_score", 0.0),
        "route": state.get("route", "unknown"),
        "routing_correct": state.get(
            "routing_was_correct",
            True
        ),
        "accuracy": state.get(
            "accuracy_score",
            0.0
        ),
        "cost": state.get(
            "estimated_cost",
            0.0
        ),
    }
)
            except Exception:
                pass

            error = None

        except Exception as exc:

            state["response"] = ""
            state["accuracy_score"] = 0.0
            state["quality_score"] = 0.0
            error = str(exc)

        end_time = time.time()

        latency = (
            end_time - start_time
        )

        results.append({
            "task_id": state.get(
                "task_id"
            ),
            "prompt": state.get(
                "prompt"
            ),
            "task_type": state.get(
                "task_type",
                "general"
            ),
            "ground_truth": state.get(
                "ground_truth",
                ""
            ),
            "complexity_score": state.get(
                "complexity_score",
                0.0
            ),
            "route": state.get(
                "route",
                "unknown"
            ),
            "routing_confidence": state.get(
                "routing_confidence",
                0.0
            ),
            "response": state.get(
                "response",
                ""
            ),
            "model_used": state.get(
                "model_used",
                "unknown"
            ),
            "accuracy": state.get(
                "accuracy_score",
                0.0
            ),
            "quality": state.get(
                "quality_score",
                0.0
            ),
            "latency": latency,
            "tokens": state.get(
                "token_usage",
                0
            ),
            "cost": state.get(
                "estimated_cost",
                0.0
            ),
            "routing_was_correct": state.get(
                "routing_was_correct",
                True
            ),
            "error": error,
        })

    return results

# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    results: List[Dict[str, Any]],
    output_path,
):
    """
    Save experiment results as JSON.

    Kept as a public helper because the existing quick/full
    experiment runners use this function.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    return output_path
# ============================================================
# COMPARISON
# ============================================================

def display_comparison(
    single_results: List[Dict[str, Any]],
    multi_results: List[Dict[str, Any]],
    adaptive_results: List[Dict[str, Any]],
    feedback_results: List[Dict[str, Any]],
):
    """
    Display a Phase 1 comparison of all four approaches.
    """

    experiments = {
        "Single LLM": single_results,
        "Multi-Agent": multi_results,
        "Adaptive Routing": adaptive_results,
        "Adaptive + Feedback": feedback_results,
    }

    print()
    print("=" * 75)
    print("PHASE 1 EXPERIMENT COMPARISON")
    print("=" * 75)

    print(
        f"{'Experiment':<25}"
        f"{'Accuracy':>12}"
        f"{'Quality':>12}"
        f"{'Latency':>12}"
        f"{'Tokens':>12}"
        f"{'Cost':>12}"
    )

    print("-" * 75)

    comparison = {}

    for name, results in experiments.items():

        metrics = compute_run_metrics(
        results
    )

        comparison[name] = metrics

        print(
        f"{name:<25}"
        f"{metrics['avg_accuracy']:>12.4f}"
        f"{metrics['avg_quality']:>12.4f}"
        f"{metrics['avg_latency']:>12.4f}"
        f"{metrics['total_tokens']:>12}"
        f"{metrics['total_cost']:>12.6f}"
    )

    print("=" * 75)

    return comparison

    
    
    # ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

# Existing experiment runners use this Phase 1 function name.
# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

run_experiment_single = run_experiment_single_llm
run_experiment_multi_agent = run_experiment_multi