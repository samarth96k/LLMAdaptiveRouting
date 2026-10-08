"""
Checkpoint Manager — saves and resumes experiment progress.

Enables experiments to:
- Resume from last successful task on crash/rate-limit
- Track progress in real-time
- Avoid re-running completed tasks
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class CheckpointManager:
    """Manages experiment checkpoints for fault tolerance."""

    def __init__(self, run_dir: Path, experiment_name: str):
        """
        Initialize checkpoint manager.

        Args:
            run_dir: Directory for this experiment run
            experiment_name: e.g., "exp1_single_llm", "exp2_multi_agent"
        """
        self.run_dir = run_dir
        self.experiment_name = experiment_name
        self.checkpoint_dir = run_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoint_file = self.checkpoint_dir / f"{experiment_name}_checkpoint.json"
        self.progress_file = self.checkpoint_dir / f"{experiment_name}_progress.json"
        self.error_log = self.checkpoint_dir / f"{experiment_name}_errors.jsonl"

    def save_checkpoint(self, results: List[Dict], completed_indices: List[int],
                       total_tasks: int, metadata: Optional[Dict] = None):
        """
        Save checkpoint after processing tasks.

        Args:
            results: List of completed task results
            completed_indices: List of task indices that are done
            total_tasks: Total number of tasks in experiment
            metadata: Additional metadata (thresholds, counters, etc.)
        """
        checkpoint_data = {
            "experiment_name": self.experiment_name,
            "timestamp": datetime.now().isoformat(),
            "completed_count": len(completed_indices),
            "total_tasks": total_tasks,
            "completed_indices": sorted(completed_indices),
            "results": results,
            "metadata": metadata or {},
        }

        # Write checkpoint
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False, default=str)

        # Update progress tracker
        self._update_progress(len(completed_indices), total_tasks)

    def load_checkpoint(self) -> Optional[Dict]:
        """
        Load checkpoint if it exists.

        Returns:
            Checkpoint data dict or None if no checkpoint exists
        """
        if not self.checkpoint_file.exists():
            return None

        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Failed to load checkpoint: {e}")
            return None

    def log_error(self, task_id: str, task_index: int, error: str,
                  provider: str = "unknown", retry_count: int = 0):
        """
        Log error to error log file.

        Args:
            task_id: Task identifier
            task_index: Task index in dataset
            error: Error message
            provider: Provider that failed
            retry_count: Number of retries attempted
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "experiment": self.experiment_name,
            "task_id": task_id,
            "task_index": task_index,
            "error": str(error),
            "provider": provider,
            "retry_count": retry_count,
        }

        # Append to error log
        with open(self.error_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_entry, ensure_ascii=False, default=str) + "\n")

    def get_remaining_indices(self, total_tasks: int) -> List[int]:
        """
        Get list of task indices that still need to be processed.

        Args:
            total_tasks: Total number of tasks

        Returns:
            List of indices that haven't been completed yet
        """
        checkpoint = self.load_checkpoint()
        if checkpoint is None:
            return list(range(total_tasks))

        completed = set(checkpoint.get("completed_indices", []))
        return [i for i in range(total_tasks) if i not in completed]

    def clear_checkpoint(self):
        """Clear checkpoint files (call after successful completion)."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        if self.progress_file.exists():
            self.progress_file.unlink()

    def _update_progress(self, completed: int, total: int):
        """Update progress tracker file."""
        progress = {
            "experiment": self.experiment_name,
            "completed": completed,
            "total": total,
            "percentage": round(100 * completed / total, 2) if total > 0 else 0,
            "remaining": total - completed,
            "timestamp": datetime.now().isoformat(),
        }

        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)

    def get_progress(self) -> Dict:
        """Get current progress status."""
        if not self.progress_file.exists():
            return {"completed": 0, "total": 0, "percentage": 0}

        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"completed": 0, "total": 0, "percentage": 0}


class ProviderFallbackChain:
    """Manages fallback between providers on errors/rate limits."""

    PROVIDER_ORDER = ["groq", "mistral", "huggingface", "gemini"]

    # Rate limit error patterns
    RATE_LIMIT_PATTERNS = [
        "rate limit",
        "rate_limit",
        "429",
        "quota exceeded",
        "too many requests",
        "RateLimitError",
    ]

    def __init__(self):
        self.provider_index = 0
        self.provider_failures = {p: 0 for p in self.PROVIDER_ORDER}
        self.current_provider = self.PROVIDER_ORDER[0]

    def is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit error."""
        error_str = str(error).lower()
        return any(pattern.lower() in error_str for pattern in self.RATE_LIMIT_PATTERNS)

    def get_next_provider(self, current_provider: str, error: Exception) -> Optional[str]:
        """
        Get next provider in fallback chain.

        Args:
            current_provider: Provider that just failed
            error: The error that occurred

        Returns:
            Next provider to try, or None if all exhausted
        """
        # Record failure
        if current_provider in self.provider_failures:
            self.provider_failures[current_provider] += 1

        # Find next provider
        try:
            current_idx = self.PROVIDER_ORDER.index(current_provider)
        except ValueError:
            current_idx = -1

        next_idx = current_idx + 1
        if next_idx >= len(self.PROVIDER_ORDER):
            return None  # All providers exhausted

        return self.PROVIDER_ORDER[next_idx]

    def reset(self):
        """Reset to first provider (call after successful request)."""
        self.provider_index = 0
        self.current_provider = self.PROVIDER_ORDER[0]

    def get_status(self) -> Dict:
        """Get current fallback status."""
        return {
            "current_provider": self.current_provider,
            "failures_by_provider": self.provider_failures.copy(),
            "providers_remaining": len(self.PROVIDER_ORDER) - self.provider_index - 1,
        }
