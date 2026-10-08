"""
Multi-Agent Pipeline.

Phase 1 architecture:

    Planner → Executor → Verifier

All agents use the Phase 1 provider strategy:

    Groq → HuggingFace fallback

The `role="multi_agent"` argument is retained for compatibility
with the provider interface.
"""

from ..llm_provider import invoke_with_fallback


# ============================================================
# PLANNER
# ============================================================

def _run_planner(prompt: str):
    """
    Planner agent.

    Breaks the task into a structured sequence of steps.
    """

    planner_prompt = f"""
You are the Planner in a multi-agent problem-solving system.

Your job is to analyze the user's task and create a clear,
step-by-step plan for solving it.

Do not solve the task yet.

Task:
{prompt}

Provide:
1. The main objective
2. The important sub-problems
3. A step-by-step solution plan
4. Important considerations or constraints
"""

    response, _provider = invoke_with_fallback(
        messages=[
            {
                "role": "user",
                "content": planner_prompt,
            }
        ],
        model_tier="large",
        role="multi_agent",
    )

    return response.content


# ============================================================
# EXECUTOR
# ============================================================

def _run_executor(
    prompt: str,
    plan: str,
):
    """
    Executor agent.

    Uses the planner's output to produce the actual solution.
    """

    executor_prompt = f"""
You are the Executor in a multi-agent problem-solving system.

Solve the user's task using the plan provided by the Planner.

User Task:
{prompt}

Planner's Plan:
{plan}

Follow the plan carefully.

Provide a complete and useful solution.
Show important reasoning or implementation details where
appropriate.
"""

    response, _provider = invoke_with_fallback(
        messages=[
            {
                "role": "user",
                "content": executor_prompt,
            }
        ],
        model_tier="large",
        role="multi_agent",
    )

    return response.content


# ============================================================
# VERIFIER
# ============================================================

def _run_verifier(
    prompt: str,
    plan: str,
    solution: str,
):
    """
    Verifier agent.

    Reviews the generated solution and improves it when
    necessary.
    """

    verifier_prompt = f"""
You are the Verifier in a multi-agent problem-solving system.

Review the solution produced by the Executor.

User Task:
{prompt}

Planner's Plan:
{plan}

Executor's Solution:
{solution}

Check the solution for:

1. Correctness
2. Missing information
3. Logical errors
4. Implementation errors
5. Whether the original task was actually answered
6. Clarity and completeness

If the solution is correct, return a polished final answer.

If there are problems, correct them and return the corrected
final answer.

Return ONLY the final answer that should be given to the user.
"""

    response, _provider = invoke_with_fallback(
        messages=[
            {
                "role": "user",
                "content": verifier_prompt,
            }
        ],
        model_tier="large",
        role="multi_agent",
    )

    return response.content


# ============================================================
# MULTI-AGENT PIPELINE
# ============================================================

def run_multi_agent(
    prompt: str,
):
    """
    Execute the complete Phase 1 multi-agent pipeline.

    Returns:
        dict containing:
            response
            intermediate_steps
            model_used
    """

    # --------------------------------------------------------
    # Step 1: Planning
    # --------------------------------------------------------

    plan = _run_planner(prompt)

    # --------------------------------------------------------
    # Step 2: Execution
    # --------------------------------------------------------

    solution = _run_executor(
        prompt,
        plan,
    )

    # --------------------------------------------------------
    # Step 3: Verification
    # --------------------------------------------------------

    verified_answer = _run_verifier(
        prompt,
        plan,
        solution,
    )

    # --------------------------------------------------------
    # Return pipeline result
    # --------------------------------------------------------

    return {
        "response": verified_answer,

        "intermediate_steps": [
            f"Planner:\n{plan}",
            f"Executor:\n{solution}",
            f"Verifier:\n{verified_answer}",
        ],

        "model_used": "groq",
    }