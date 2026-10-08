"""
Application configuration.

Phase 1:
- Groq as the primary LLM provider
- HuggingFace as the fallback provider
- Global complexity threshold
- No task-specific routing thresholds
- No Phase 2 Mistral/Gemini configuration
"""

import os

from dotenv import load_dotenv
from datetime import datetime
import os
from datetime import datetime
from pathlib import Path

# Load environment variables
# Load environment variables from the Phase 1 project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# API KEYS
# ============================================================

GROQ_API_KEY_1 = os.getenv("GROQ_API_1")
GROQ_API_KEY_2 = os.getenv("GROQ_API_2")

# Keep support for multiple Groq keys for compatibility.
GROQ_API_KEYS = [
    key
    for key in [GROQ_API_KEY_1, GROQ_API_KEY_2]
    if key
]

# Primary Groq key
GROQ_API_KEY = GROQ_API_KEY_1 or os.getenv("GROQ_API_KEY")

# HuggingFace fallback
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API")


# ============================================================
# MODELS
# ============================================================

# Groq models
GROQ_MODEL_FAST = "openai/gpt-oss-20b"
GROQ_MODEL_SMALL = "openai/gpt-oss-20b"
GROQ_MODEL_LARGE = "openai/gpt-oss-120b"

# HuggingFace fallback model
HUGGINGFACE_MODEL = os.getenv(
    "HUGGINGFACE_MODEL",
    "Qwen/Qwen2.5-7B-Instruct-1M"
)


# ============================================================
# ROUTING CONFIGURATION
# ============================================================

# Phase 1 uses one global complexity threshold.
#
# score < 0.6  -> Single LLM
# score >= 0.6 -> Multi-Agent
#
# Phase 2 introduced task-specific thresholds.
COMPLEXITY_THRESHOLD = 0.6


# Confidence threshold used by the LLM-assisted
# borderline routing decision.
CONFIDENCE_THRESHOLD = 0.7


# Margin around the complexity threshold.
#
# Example:
# threshold = 0.6
# margin = 0.10
#
# score <= 0.50 -> clearly simple
# score >= 0.70 -> clearly complex
# otherwise     -> borderline / LLM-assisted routing
ROUTING_MARGIN = 0.10


# ============================================================
# PROVIDER ROLES
# ============================================================

# Phase 1 does not use separate providers for different roles.
# All LLM operations primarily use Groq with HuggingFace fallback.

PROVIDER_ROLES = {
    "single_llm": "groq",
    "multi_agent": "groq",
    "evaluation": "groq",
    "routing": "groq",
    "fallback": "huggingface",
}


# ============================================================
# EXECUTION CONFIGURATION
# ============================================================

# Phase 1 does not require the Phase 2 provider-specific
# throttling configuration.

MULTI_AGENT_DELAY = 0.0
BATCH_DELAY = 0.0


# ============================================================
# API KEY VALIDATION
# ============================================================

# ============================================================
# PROJECT DIRECTORIES
# ============================================================

# ============================================================
# PROJECT DIRECTORIES
# ============================================================

BASE_DIR = Path(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

def get_next_run_dir():
    """
    Create and return a unique directory for an experiment run.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    run_dir = RESULTS_DIR / f"run_{timestamp}"

    counter = 1

    while run_dir.exists():

        run_dir = (
            RESULTS_DIR
            / f"run_{timestamp}_{counter}"
        )

        counter += 1

    run_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return run_dir


def validate_keys():
    """
    Validate the API keys required by the Phase 1 system.

    Groq is required because it is the primary provider.
    HuggingFace is required as the fallback provider.
    """

    missing = []

    if not GROQ_API_KEYS:
        missing.append("GROQ_API_1 or GROQ_API_KEY")


    if missing:
        raise ValueError(
            "Missing required API keys: "
            + ", ".join(missing)
        )

    return True