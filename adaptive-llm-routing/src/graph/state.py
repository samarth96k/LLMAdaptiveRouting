"""
Graph State for the Adaptive LLM Routing System.

Phase 1 state contains:
- Task input
- Complexity analysis
- Routing decision
- Execution result
- Basic evaluation
- Performance metrics
- Feedback
"""

from typing import Any, Dict, List, Optional, TypedDict


class TaskState(TypedDict, total=False):
    # ========================================================
    # INPUT
    # ========================================================

    task_id: str
    prompt: str
    task_type: str
    ground_truth: str

    # ========================================================
    # COMPLEXITY ANALYSIS
    # ========================================================

    complexity_score: float
    complexity_features: Dict[str, Any]
    analysis_time: float

    # ========================================================
    # ROUTING
    # ========================================================

    route: str
    routing_confidence: float
    routing_reason: str

    # ========================================================
    # EXECUTION
    # ========================================================

    response: str
    intermediate_steps: List[str]
    model_used: str

    # ========================================================
    # EVALUATION
    # ========================================================

    accuracy_score: float
    quality_score: float

    # ========================================================
    # PERFORMANCE
    # ========================================================

    latency_seconds: float
    token_usage: int
    estimated_cost: float

    # ========================================================
    # FEEDBACK
    # ========================================================

    feedback: Dict[str, Any]
    routing_was_correct: bool

    # ========================================================
    # TIMESTAMPS
    # ========================================================

    start_time: float
    end_time: float