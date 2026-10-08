"""
Graph Nodes for the Adaptive LLM Routing System.

Phase 1:
    1. Complexity Analysis
    2. Task Routing
    3. Single LLM Execution
    4. Multi-Agent Execution
    5. Output Evaluation
    6. Feedback Logging

Routing:
    complexity < 0.6  -> Single LLM
    complexity >= 0.6 -> Multi-Agent

Borderline cases are resolved using an LLM-assisted routing
decision.
"""

import time

from ..config import (
    COMPLEXITY_THRESHOLD,
    CONFIDENCE_THRESHOLD,
    ROUTING_MARGIN,
)
from ..llm_provider import invoke_with_fallback
from ..agents.single_llm import run_single_llm
from ..agents.multi_agent import run_multi_agent
from ..utils.complexity import estimate_complexity
from ..evaluation.metrics import fuzzy_accuracy


# ============================================================
# COMPLEXITY ANALYSIS
# ============================================================

def analyze_and_estimate(state):
    """
    Analyze the prompt and calculate its complexity score.
    """

    start_time = time.time()

    score, features = estimate_complexity(
        state["prompt"]
    )

    state["complexity_score"] = score
    state["complexity_features"] = features

    state["analysis_time"] = time.time() - start_time

    return state


# ============================================================
# TASK ROUTING
# ============================================================

def route_task(state):
    """
    Route the task to either:

        single_llm
        multi_agent

    Phase 1 uses one global complexity threshold.

    Clear cases:
        score <= threshold - margin -> single_llm
        score >= threshold + margin -> multi_agent

    Borderline cases:
        LLM-assisted routing
    """

    score = state.get(
        "complexity_score",
        0.0
    )

    threshold = COMPLEXITY_THRESHOLD
    margin = ROUTING_MARGIN

    # --------------------------------------------------------
    # Clearly simple
    # --------------------------------------------------------

    if score <= threshold - margin:

        state["route"] = "single_llm"
        state["routing_confidence"] = 1.0
        state["routing_reason"] = (
            f"Complexity score {score:.4f} is clearly below "
            f"the Phase 1 threshold {threshold:.2f}."
        )

        return state

    # --------------------------------------------------------
    # Clearly complex
    # --------------------------------------------------------

    if score >= threshold + margin:

        state["route"] = "multi_agent"
        state["routing_confidence"] = 1.0
        state["routing_reason"] = (
            f"Complexity score {score:.4f} is clearly above "
            f"the Phase 1 threshold {threshold:.2f}."
        )

        return state

    # --------------------------------------------------------
    # Borderline case
    # --------------------------------------------------------

    prompt = state["prompt"]

    routing_prompt = f"""
You are a routing classifier.

Decide whether the following task should be handled by:

1. single_llm
   - straightforward
   - simple explanation
   - simple factual answer
   - basic coding or calculation

2. multi_agent
   - complex reasoning
   - multiple steps
   - difficult coding/debugging
   - detailed analysis
   - tasks requiring planning and verification

Task:
{prompt}

Respond in exactly this format:

ROUTE: single_llm

or

ROUTE: multi_agent

CONFIDENCE: <number between 0 and 1>

REASON: <short reason>
"""

    try:

        response, _provider = invoke_with_fallback(
            messages=[
                {
                    "role": "user",
                    "content": routing_prompt,
                }
            ],
            model_tier="small",
            role="routing",
        )

        content = response.content.strip()

        route = "single_llm"

        if "ROUTE: multi_agent" in content:
            route = "multi_agent"
        elif "ROUTE: single_llm" in content:
            route = "single_llm"

        confidence = 0.5

        for line in content.splitlines():

            if line.upper().startswith("CONFIDENCE:"):

                try:
                    confidence = float(
                        line.split(":", 1)[1].strip()
                    )

                    confidence = max(
                        0.0,
                        min(1.0, confidence)
                    )

                except ValueError:
                    confidence = 0.5

        reason = "LLM-assisted routing for borderline complexity."

        for line in content.splitlines():

            if line.upper().startswith("REASON:"):
                reason = line.split(
                    ":", 1
                )[1].strip()
                break

        state["route"] = route
        state["routing_confidence"] = confidence
        state["routing_reason"] = reason

        return state

    except Exception as exc:

        # ----------------------------------------------------
        # Safe fallback
        # ----------------------------------------------------

        # If the routing LLM fails, use the global threshold.
        route = (
            "multi_agent"
            if score >= threshold
            else "single_llm"
        )

        state["route"] = route
        state["routing_confidence"] = CONFIDENCE_THRESHOLD
        state["routing_reason"] = (
            "LLM-assisted routing failed; "
            "used the Phase 1 global complexity threshold. "
            f"Error: {exc}"
        )

        return state

# ============================================================
# SINGLE LLM EXECUTION
# ============================================================

def execute_single(state):
    """
    Execute the task using the single-LLM baseline.
    """

    start_time = time.time()

    result = run_single_llm(
        prompt=state["prompt"],
        task_type=state.get("task_type", "general"),
    )

    state["response"] = result.get("response", "")
    state["model_used"] = result.get("model_used", "groq")
    state["token_usage"] = result.get("token_usage", {})
    state["latency_seconds"] = result.get(
        "latency_seconds",
        round(time.time() - start_time, 3),
    )
    state["intermediate_steps"] = result.get(
        "intermediate_steps",
        [],
    )

    return state

# ============================================================
# MULTI-AGENT EXECUTION
# ============================================================

def execute_multi(state):
    """
    Execute the task using the Planner -> Executor -> Verifier
    multi-agent pipeline.
    """

    start_time = time.time()

    result = run_multi_agent(
        prompt=state["prompt"]
    )

    state["response"] = result.get("response", "")
    state["model_used"] = result.get("model_used", "groq")
    state["intermediate_steps"] = result.get(
        "intermediate_steps",
        [],
    )

    state["latency_seconds"] = round(
        time.time() - start_time,
        3,
    )

    state["token_usage"] = result.get(
        "token_usage",
        {},
    )

    return state

# ============================================================
# OUTPUT EVALUATION
# ============================================================

def evaluate_output(state):
    """
    Evaluate the generated response.

    Phase 1 evaluation uses:
        - fuzzy/exact accuracy
        - LLM-as-judge quality evaluation

    Phase 2 semantic similarity and composite scoring
    are intentionally not used here.
    """

    response = state.get(
        "response",
        ""
    )

    ground_truth = state.get(
        "ground_truth",
        ""
    )

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    if ground_truth and response:

        accuracy = fuzzy_accuracy(
            response,
            ground_truth
        )

    else:

        accuracy = 0.0

    # --------------------------------------------------------
    # LLM-as-judge quality
    # --------------------------------------------------------

    quality = 0.0

    if response:

        evaluation_prompt = f"""
Evaluate the quality of the following answer.

Task:
{state.get("prompt", "")}

Answer:
{response}

Ground Truth:
{ground_truth}

Give a quality score from 0 to 1.

Consider:
- correctness
- relevance
- completeness
- clarity

Respond in exactly this format:

SCORE: <number between 0 and 1>
REASON: <short explanation>
"""

        try:

            judge_response, _provider = invoke_with_fallback(
                messages=[
                    {
                        "role": "user",
                        "content": evaluation_prompt,
                    }
                ],
                model_tier="small",
                role="evaluation",
            )

            content = judge_response.content.strip()

            for line in content.splitlines():

                if line.upper().startswith("SCORE:"):

                    try:

                        quality = float(
                            line.split(
                                ":",
                                1
                            )[1].strip()
                        )

                        quality = max(
                            0.0,
                            min(1.0, quality)
                        )

                    except ValueError:

                        quality = 0.0

                    break

        except Exception:

            quality = 0.0

    state["accuracy_score"] = round(
        accuracy,
        4
    )

    state["quality_score"] = round(
        quality,
        4
    )

    state["end_time"] = time.time()

    return state


# ============================================================
# FEEDBACK LOGGING
# ============================================================

def log_feedback(state):
    """
    Record feedback about the routing decision.

    A routing decision is considered correct when:

        single_llm + good accuracy
            OR
        multi_agent + good accuracy

    The feedback is stored for later threshold adaptation.
    """

    accuracy = state.get(
        "accuracy_score",
        0.0
    )

    route = state.get(
        "route",
        "single_llm"
    )

    # --------------------------------------------------------
    # Basic routing correctness heuristic
    # --------------------------------------------------------

    routing_was_correct = True

    if route == "single_llm":

        # A poor answer from a single model suggests that
        # the task may have been too complex.
        if accuracy < 0.5:
            routing_was_correct = False

    elif route == "multi_agent":

        # A good answer is generally acceptable for a
        # complex task. The feedback loop can use this
        # information later.
        if accuracy < 0.5:
            routing_was_correct = False

    state["routing_was_correct"] = (
        routing_was_correct
    )

    # --------------------------------------------------------
    # Store feedback
    # --------------------------------------------------------

    state["feedback"] = {
        "accuracy": accuracy,
        "quality": state.get(
            "quality_score",
            0.0
        ),
        "route": route,
        "routing_was_correct": routing_was_correct,
    }

    return state