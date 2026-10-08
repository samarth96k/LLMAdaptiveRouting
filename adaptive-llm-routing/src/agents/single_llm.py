"""
Single LLM Agent — baseline A.

Routes simple tasks to a single LLM call.
Uses the smaller/faster model for cost efficiency.
Falls back to HuggingFace if Groq is rate-limited.
"""

import time
from langchain_core.messages import HumanMessage, SystemMessage
from ..llm_provider import invoke_with_fallback


def run_single_llm(prompt: str, task_type: str = "general", use_large: bool = False) -> dict:
    """
    Execute a task with a single LLM call.

    Returns:
        dict with keys: response, model_used, token_usage, latency_seconds
    """
    model_tier = "large" if use_large else "small"

    system_msg = SystemMessage(content=(
        "You are a helpful, precise AI assistant. "
        "Answer the user's question thoroughly and accurately. "
        f"This is a {task_type} task — tailor your response appropriately."
    ))
    human_msg = HumanMessage(content=prompt)

    start = time.time()
    response, provider = invoke_with_fallback(
        [system_msg, human_msg], model_tier=model_tier
    )
    latency = time.time() - start

    token_usage = {
        "input": response.response_metadata.get("token_usage", {}).get("prompt_tokens", 0),
        "output": response.response_metadata.get("token_usage", {}).get("completion_tokens", 0),
        "total": response.response_metadata.get("token_usage", {}).get("total_tokens", 0),
    }

    return {
        "response": response.content,
        "model_used": provider,
        "token_usage": token_usage,
        "latency_seconds": round(latency, 3),
        "intermediate_steps": [],
    }
