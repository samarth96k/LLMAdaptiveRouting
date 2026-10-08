"""
Evaluation Metrics.

Phase 1 evaluation:
    - Exact accuracy
    - Fuzzy accuracy
    - LLM-as-judge quality
    - Latency
    - Token usage
    - Cost
    - Efficiency
    - Stability

Phase 2 semantic similarity and composite accuracy are not
used in the Phase 1 pipeline.
"""

from typing import Any, Dict, List


# ============================================================
# BASIC ACCURACY
# ============================================================

def accuracy_score(
    prediction: str,
    ground_truth: str,
) -> float:
    """
    Calculate exact-match accuracy.

    Returns:
        1.0 if prediction exactly matches ground truth.
        0.0 otherwise.
    """

    if not prediction or not ground_truth:
        return 0.0

    prediction = prediction.strip().lower()
    ground_truth = ground_truth.strip().lower()

    return 1.0 if prediction == ground_truth else 0.0


def fuzzy_accuracy(
    prediction: str,
    ground_truth: str,
) -> float:
    """
    Calculate a lightweight fuzzy accuracy score.

    Phase 1 heuristic:

        Exact match          -> 1.0
        Ground truth in pred -> 0.8
        Important word match -> 0.4
        Otherwise             -> 0.0
    """

    if not prediction or not ground_truth:
        return 0.0

    prediction = prediction.strip().lower()
    ground_truth = ground_truth.strip().lower()

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    if prediction == ground_truth:
        return 1.0

    # --------------------------------------------------------
    # Ground truth contained in prediction
    # --------------------------------------------------------

    if ground_truth in prediction:
        return 0.8

    # --------------------------------------------------------
    # Important word overlap
    # --------------------------------------------------------

    prediction_words = {
        word
        for word in prediction.split()
        if len(word) > 3
    }

    ground_truth_words = {
        word
        for word in ground_truth.split()
        if len(word) > 3
    }

    if prediction_words and ground_truth_words:

        overlap = (
            prediction_words
            & ground_truth_words
        )

        overlap_ratio = (
            len(overlap)
            / len(ground_truth_words)
        )

        if overlap_ratio >= 0.5:
            return 0.4

    return 0.0


# ============================================================
# LATENCY
# ============================================================

def calculate_latency(
    start_time: float,
    end_time: float,
) -> float:
    """
    Calculate execution latency in seconds.
    """

    return max(
        0.0,
        end_time - start_time
    )


# ============================================================
# EFFICIENCY
# ============================================================

def calculate_efficiency(
    accuracy: float,
    latency: float,
) -> float:
    """
    Calculate a simple accuracy/latency efficiency score.

    Higher accuracy and lower latency produce a higher score.
    """

    if latency <= 0:
        return accuracy

    return accuracy / latency


# ============================================================
# RUN METRICS
# ============================================================

def compute_run_metrics(
    results: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Aggregate metrics across experiment runs.

    Expected result fields may include:

        accuracy
        quality
        latency
        tokens
        cost
        efficiency
    """

    if not results:
        return {
            "count": 0,
            "avg_accuracy": 0.0,
            "avg_quality": 0.0,
            "avg_latency": 0.0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_efficiency": 0.0,
        }

    count = len(results)

    accuracies = [
        float(r.get("accuracy", 0.0))
        for r in results
    ]

    qualities = [
        float(r.get("quality", 0.0))
        for r in results
    ]

    latencies = [
        float(r.get("latency", 0.0))
        for r in results
    ]

    tokens = [
        int(r.get("tokens", 0))
        for r in results
    ]

    costs = [
        float(r.get("cost", 0.0))
        for r in results
    ]

    efficiencies = [
        float(r.get("efficiency", 0.0))
        for r in results
    ]

    return {
        "count": count,

        "avg_accuracy": (
            sum(accuracies) / count
        ),

        "avg_quality": (
            sum(qualities) / count
        ),

        "avg_latency": (
            sum(latencies) / count
        ),

        "total_tokens": sum(tokens),

        "total_cost": sum(costs),

        "avg_efficiency": (
            sum(efficiencies) / count
        ),
    }


# ============================================================
# STABILITY
# ============================================================

def stability_score(
    scores: List[float],
) -> float:
    """
    Calculate a simple stability score.

    A stable system has lower variation between runs.

    Returns a value between 0 and 1.
    """

    if not scores:
        return 0.0

    if len(scores) == 1:
        return 1.0

    mean = sum(scores) / len(scores)

    if mean == 0:
        return 0.0

    variance = sum(
        (score - mean) ** 2
        for score in scores
    ) / len(scores)

    std_dev = variance ** 0.5

    stability = 1.0 - (
        std_dev / max(abs(mean), 1e-9)
    )

    return max(
        0.0,
        min(1.0, stability)
    )


# ============================================================
# SUMMARY
# ============================================================

def summarize_results(
    results: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Return a Phase 1 experiment summary.
    """

    return compute_run_metrics(results)