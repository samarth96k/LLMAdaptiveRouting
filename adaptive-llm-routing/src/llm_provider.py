"""
LLM Provider — Phase 1 multi-provider interface.

Phase 1 provider strategy:

    Primary:
        Groq

    Fallback:
        HuggingFace

The same interface is used by:
    - Single LLM
    - Multi-Agent
    - Routing
    - Evaluation

The `role` argument is retained for compatibility with the
existing project structure, but Phase 1 does not assign
different providers to different roles.
"""

import time
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from .config import (
    GROQ_API_KEYS,
    GROQ_API_KEY,
    GROQ_MODEL_FAST,
    GROQ_MODEL_SMALL,
    GROQ_MODEL_LARGE,
    HUGGINGFACE_API_KEY,
    HUGGINGFACE_MODEL,
)


# ============================================================
# GROQ
# ============================================================

def _get_groq_llm(model: Optional[str] = None):
    """
    Create a Groq LLM instance.

    Phase 1 uses a single Groq API key as the primary provider.
    """
    if not GROQ_API_KEY:
        raise ValueError("Groq API key is not configured.")

    selected_key = GROQ_API_KEY

    # Keep compatibility with multiple-key configuration.
    if GROQ_API_KEYS:
        selected_key = GROQ_API_KEYS[0]

    selected_model = model or GROQ_MODEL_FAST

    return ChatGroq(
        api_key=selected_key,
        model=selected_model,
        temperature=0,
    )

# ============================================================
# HUGGINGFACE
# ============================================================

def _get_huggingface_llm():
    """
    Create the HuggingFace fallback LLM.
    """

    if not HUGGINGFACE_API_KEY:
        raise ValueError(
            "HuggingFace API key is not configured."
        )

    endpoint = HuggingFaceEndpoint(
        repo_id=HUGGINGFACE_MODEL,
        huggingfacehub_api_token=HUGGINGFACE_API_KEY,
        temperature=0.0,
        max_new_tokens=1024,
    )

    return ChatHuggingFace(
        llm=endpoint
    )


# ============================================================
# MODEL SELECTION
# ============================================================

def get_llm(
    provider: str = "groq",
    model_tier: str = "fast",
):
    """
    Return an LLM based on provider and model tier.

    Phase 1 providers:
        groq
        huggingface

    Model tiers:
        small
        fast
        large
    """

    if provider == "groq":

        model_map = {
            "small": GROQ_MODEL_SMALL,
            "fast": GROQ_MODEL_FAST,
            "large": GROQ_MODEL_LARGE,
        }

        model = model_map.get(
            model_tier,
            GROQ_MODEL_FAST
        )

        return _get_groq_llm(model)

    if provider == "huggingface":
        return _get_huggingface_llm()

    raise ValueError(
        f"Unsupported Phase 1 provider: {provider}"
    )


# ============================================================
# ROLE-BASED PROVIDER SELECTION
# ============================================================

def get_llm_for_role(
    role: str = "single_llm",
    model_tier: str = "fast",
):
    """
    Return the Phase 1 LLM for a particular pipeline role.

    Phase 1 uses Groq for every role.

    The role parameter is intentionally retained because the
    rest of the project already passes role names such as:

        single_llm
        multi_agent
        routing
        evaluation

    This allows us to simplify the provider architecture
    without changing the rest of the application.
    """

    return get_llm(
        provider="groq",
        model_tier=model_tier,
    )


# ============================================================
# INVOCATION WITH FALLBACK
# ============================================================

def invoke_with_fallback(
    messages,
    model_tier: str = "fast",
    role: str = "single_llm",
    max_retries: int = 2,
):
    """
    Invoke the primary Groq model.

    If Groq fails, retry it and then fall back to HuggingFace.

    Args:
        messages:
            LangChain messages.

        model_tier:
            small / fast / large.

        role:
            Retained for compatibility with the existing
            Phase 2 code. Phase 1 does not use role-specific
            provider selection.

        max_retries:
            Number of Groq retry attempts.

    Returns:
        LLM response.
    """

    last_error = None

    # --------------------------------------------------------
    # Primary: Groq
    # --------------------------------------------------------

    for attempt in range(max_retries + 1):

        try:
            llm = get_llm_for_role(
                role=role,
                model_tier=model_tier,
            )

            response = llm.invoke(messages)

            return response, "groq"

        except Exception as exc:

            last_error = exc

            if attempt < max_retries:
                # Small delay before retrying.
                time.sleep(1)

    # --------------------------------------------------------
    # Fallback: HuggingFace
    # --------------------------------------------------------

    try:

        fallback_llm = get_llm(
            provider="huggingface",
            model_tier=model_tier,
        )

        response = fallback_llm.invoke(messages)

        return response, "huggingface"

    except Exception as fallback_error:

        raise RuntimeError(
            "Both Groq and HuggingFace providers failed.\n"
            f"Groq error: {last_error}\n"
            f"HuggingFace error: {fallback_error}"
        ) from fallback_error


# ============================================================
# SIMPLE TEXT INVOCATION
# ============================================================

def invoke_text(
    prompt: str,
    system_prompt: Optional[str] = None,
    model_tier: str = "fast",
    role: str = "single_llm",
):
    """
    Convenience wrapper for simple text generation.

    This is useful when a caller has a plain prompt instead
    of manually constructing LangChain messages.
    """

    messages = []

    if system_prompt:
        messages.append(
            SystemMessage(
                content=system_prompt
            )
        )

    messages.append(
        HumanMessage(
            content=prompt
        )
    )

    return invoke_with_fallback(
        messages=messages,
        model_tier=model_tier,
        role=role,
    )