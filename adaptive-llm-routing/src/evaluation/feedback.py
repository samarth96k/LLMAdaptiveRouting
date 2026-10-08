"""
Feedback System — logs results and adapts routing thresholds over time.

This is what makes the system "adaptive": it learns from past routing decisions
and adjusts the complexity threshold to improve future routing accuracy.
"""

import json
import time
from pathlib import Path
from typing import Optional

from ..config import RESULTS_DIR, COMPLEXITY_THRESHOLD


class FeedbackStore:
    """
    Persistent feedback storage and routing strategy adaptation.

    Stores all run results in a JSON Lines file and computes
    updated routing thresholds based on historical performance.
    """

    def __init__(self, store_path: Optional[Path] = None):
        self.store_path = store_path or (RESULTS_DIR / "feedback_log.jsonl")
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._history: list[dict] = []
        self._load_history()

    def _load_history(self):
        """Load existing feedback from disk."""
        if self.store_path.exists():
            with open(self.store_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._history.append(json.loads(line))

    def log(self, feedback: dict):
        """Append a feedback entry and persist to disk."""
        feedback["timestamp"] = time.time()
        self._history.append(feedback)

        with open(self.store_path, "a") as f:
            f.write(json.dumps(feedback) + "\n")

    def get_history(self) -> list[dict]:
        return self._history.copy()

    def compute_adapted_threshold(self) -> float:
        """
        Adapt the routing complexity threshold based on historical feedback.

        Strategy:
          - Look at cases where routing was incorrect
          - If single_llm failed on tasks with complexity > X → lower threshold
          - If multi_agent was overkill on tasks with complexity < X → raise threshold
          - Use the average of misrouted complexity scores as the new threshold
        """
        if len(self._history) < 5:
            return COMPLEXITY_THRESHOLD  # not enough data to adapt

        misrouted = [
            h for h in self._history
            if not h.get("routing_correct", True)
        ]

        if not misrouted:
            return COMPLEXITY_THRESHOLD

        # separate by type of misroute
        single_failures = [
            h["complexity_score"] for h in misrouted
            if h.get("route") == "single_llm"
        ]
        multi_overkills = [
            h["complexity_score"] for h in misrouted
            if h.get("route") == "multi_agent"
        ]

        # adjust threshold toward the boundary of misrouted tasks
        new_threshold = COMPLEXITY_THRESHOLD

        if single_failures:
            # single LLM failed → lower threshold (more tasks go to multi)
            avg_failure = sum(single_failures) / len(single_failures)
            new_threshold = min(new_threshold, avg_failure - 0.05)

        if multi_overkills:
            # multi-agent was overkill → raise threshold (fewer tasks go to multi)
            avg_overkill = sum(multi_overkills) / len(multi_overkills)
            new_threshold = max(new_threshold, avg_overkill + 0.05)

        # clamp to reasonable range
        new_threshold = max(0.3, min(0.85, new_threshold))

        return round(new_threshold, 3)

    def get_stats(self) -> dict:
        """Quick summary statistics of all logged feedback."""
        if not self._history:
            return {"total_runs": 0}

        total = len(self._history)
        correct = sum(1 for h in self._history if h.get("routing_correct", False))
        single_count = sum(1 for h in self._history if h.get("route") == "single_llm")
        multi_count = sum(1 for h in self._history if h.get("route") == "multi_agent")

        accuracies = [h.get("accuracy", 0) for h in self._history]
        costs = [h.get("cost", 0) for h in self._history]

        return {
            "total_runs": total,
            "routing_accuracy": round(correct / total, 3) if total else 0,
            "single_llm_count": single_count,
            "multi_agent_count": multi_count,
            "avg_accuracy": round(sum(accuracies) / len(accuracies), 3),
            "total_cost": round(sum(costs), 6),
            "adapted_threshold": self.compute_adapted_threshold(),
        }
