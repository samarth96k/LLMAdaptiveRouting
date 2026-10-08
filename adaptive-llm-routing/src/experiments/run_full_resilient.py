"""
Resilient Full Experiment Runner — with checkpointing and fallback.

Features:
- Resume from last checkpoint on failure
- Automatic provider fallback on rate limits
- Retry with exponential backoff
- Real-time progress tracking
- Error logging

Usage:
    python run.py resilient       # Run with resilience
    python run.py resilient --resume  # Resume from checkpoint
"""

import os
import sys
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from src.config import validate_keys, RESULTS_DIR, get_next_run_dir
from src.experiments.dataset_generator import BENCHMARK_TASKS
from src.experiments.checkpoint_manager import CheckpointManager, ProviderFallbackChain
from src.agents.single_llm import run_single_llm
from src.agents.multi_agent import run_multi_agent
from src.graph.builder import build_adaptive_graph
from src.graph.nodes import evaluate_output, log_feedback
from src.utils.complexity import estimate_complexity
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console(force_terminal=True)


class ResilientExperimentRunner:
    """Runs experiments with full fault tolerance."""

    MAX_RETRIES = 5
    BASE_RETRY_DELAY = 5  # seconds
    RATE_LIMIT_BACKOFF = 60  # seconds to wait on rate limit

    def __init__(self, run_dir: Path, tasks: List[Dict]):
        self.run_dir = run_dir
        self.tasks = tasks
        self.fallback_chain = ProviderFallbackChain()

    def _retry_with_backoff(self, fn, task, max_retries=None):
        """
        Execute function with exponential backoff retry.

        Args:
            fn: Function to execute
            task: Task dict
            max_retries: Max retry attempts (defaults to self.MAX_RETRIES)

        Returns:
            Result from function
        """
        max_retries = max_retries or self.MAX_RETRIES
        last_error = None

        for attempt in range(max_retries):
            try:
                result = fn()
                self.fallback_chain.reset()  # Success - reset fallback chain
                return result

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check if it's a rate limit error
                if self.fallback_chain.is_rate_limit_error(e):
                    wait_time = self.RATE_LIMIT_BACKOFF * (attempt + 1)
                    console.print(f"    [yellow]Rate limit hit. Waiting {wait_time}s...[/yellow]")
                    time.sleep(wait_time)
                else:
                    # Regular error - exponential backoff
                    wait_time = self.BASE_RETRY_DELAY * (2 ** attempt)
                    console.print(f"    [yellow]Error: {str(e)[:80]}. Retry {attempt + 1}/{max_retries} in {wait_time}s[/yellow]")
                    time.sleep(wait_time)

        # All retries exhausted
        raise last_error

    def _run_single_task_resilient(self, task, task_index: int, run_fn, route_label: str,
                                   checkpoint_mgr: CheckpointManager, extra_sleep=1) -> Dict:
        """
        Run single task with full error handling and retry logic.

        Args:
            task: Task dict
            task_index: Index in task list
            run_fn: Execution function
            route_label: Experiment label
            checkpoint_mgr: Checkpoint manager
            extra_sleep: Additional sleep after task

        Returns:
            Task result dict
        """
        task_id = task.get("task_id", f"task_{task_index}")

        try:
            # Define execution function
            def execute():
                exec_result = run_fn(
                    prompt=task["prompt"],
                    task_type=task.get("task_type", "general")
                )
                complexity_score, features = estimate_complexity(task["prompt"])

                state = {
                    "task_id": task_id,
                    "prompt": task["prompt"],
                    "task_type": task.get("task_type", "general"),
                    "ground_truth": task.get("ground_truth"),
                    "response": exec_result["response"],
                    "complexity_score": complexity_score,
                    "route": route_label,
                    "model_used": exec_result["model_used"],
                    "token_usage": exec_result["token_usage"],
                    "latency_seconds": exec_result["latency_seconds"],
                    "intermediate_steps": exec_result.get("intermediate_steps", []),
                    "routing_confidence": 1.0,
                    "routing_reason": f"Forced {route_label} (experiment control)",
                }

                # Evaluate
                eval_r = evaluate_output(state)
                state.update(eval_r)

                # Log feedback
                fb_r = log_feedback(state)
                state.update(fb_r)

                return state

            # Execute with retry
            result = self._retry_with_backoff(execute, task)

            # Success
            time.sleep(extra_sleep)
            return result

        except Exception as e:
            # Log error
            checkpoint_mgr.log_error(task_id, task_index, str(e), "unknown", self.MAX_RETRIES)

            console.print(f"    [red][ERROR] {task_id}: Failed after {self.MAX_RETRIES} retries[/red]")
            console.print(f"    [red]  Error: {str(e)[:120]}[/red]")

            # Return error state
            time.sleep(extra_sleep + 2)
            return {
                "task_id": task_id,
                "route": route_label,
                "error": str(e),
                "complexity_score": 0,
                "accuracy_score": 0,
                "quality_score": 0,
                "latency_seconds": 0,
                "token_usage": {"total": 0},
                "estimated_cost": 0,
                "failed": True,
            }

    def run_experiment_single_llm_resilient(self, resume: bool = False):
        """Experiment 1: Single LLM with checkpointing."""
        exp_name = "exp1_single_llm"
        checkpoint_mgr = CheckpointManager(self.run_dir, exp_name)

        # Check for resume
        if resume:
            checkpoint = checkpoint_mgr.load_checkpoint()
            if checkpoint:
                console.print(f"[bold cyan] Resuming {exp_name} from checkpoint[/bold cyan]")
                console.print(f"   Completed: {checkpoint['completed_count']}/{checkpoint['total_tasks']}")
                results = checkpoint["results"]
                completed_indices = set(checkpoint["completed_indices"])
            else:
                console.print(f"[yellow]No checkpoint found for {exp_name}, starting fresh[/yellow]")
                results = []
                completed_indices = set()
        else:
            results = []
            completed_indices = set()

        console.print(f"\n[bold cyan]═══ Experiment 1/4: Single LLM ({len(self.tasks)} tasks) ═══[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task_bar = progress.add_task(f"[cyan]Single LLM", total=len(self.tasks))

            for i, task in enumerate(self.tasks):
                # Skip if already completed
                if i in completed_indices:
                    progress.advance(task_bar)
                    continue

                # Run task
                fn = lambda prompt, task_type: run_single_llm(prompt, task_type, use_large=False)
                result = self._run_single_task_resilient(
                    task, i, fn, "single_llm", checkpoint_mgr, extra_sleep=1
                )
                results.append(result)
                completed_indices.add(i)

                # Save checkpoint every 5 tasks
                if len(completed_indices) % 5 == 0:
                    checkpoint_mgr.save_checkpoint(
                        results,
                        list(completed_indices),
                        len(self.tasks)
                    )

                progress.advance(task_bar)

                # Batch delay every 15 tasks
                if (i + 1) % 15 == 0 and (i + 1) < len(self.tasks):
                    console.print("    [dim]Batch pause (20s to avoid rate limits)...[/dim]")
                    time.sleep(20)

        # Final checkpoint
        checkpoint_mgr.save_checkpoint(results, list(completed_indices), len(self.tasks))
        console.print(f"[green][OK] Experiment 1 complete ({len(results)} tasks)[/green]")

        return results

    def run_experiment_multi_agent_resilient(self, resume: bool = False):
        """Experiment 2: Multi-Agent with checkpointing."""
        exp_name = "exp2_multi_agent"
        checkpoint_mgr = CheckpointManager(self.run_dir, exp_name)

        # Check for resume
        if resume:
            checkpoint = checkpoint_mgr.load_checkpoint()
            if checkpoint:
                console.print(f"[bold yellow] Resuming {exp_name} from checkpoint[/bold yellow]")
                console.print(f"   Completed: {checkpoint['completed_count']}/{checkpoint['total_tasks']}")
                results = checkpoint["results"]
                completed_indices = set(checkpoint["completed_indices"])
            else:
                console.print(f"[yellow]No checkpoint found for {exp_name}, starting fresh[/yellow]")
                results = []
                completed_indices = set()
        else:
            results = []
            completed_indices = set()

        console.print(f"\n[bold yellow]═══ Experiment 2/4: Multi-Agent ({len(self.tasks)} tasks) ═══[/bold yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task_bar = progress.add_task(f"[yellow]Multi-Agent", total=len(self.tasks))

            for i, task in enumerate(self.tasks):
                # Skip if already completed
                if i in completed_indices:
                    progress.advance(task_bar)
                    continue

                # Run task
                fn = lambda prompt, task_type: run_multi_agent(prompt, task_type)
                result = self._run_single_task_resilient(
                    task, i, fn, "multi_agent", checkpoint_mgr, extra_sleep=2
                )
                results.append(result)
                completed_indices.add(i)

                # Save checkpoint every 5 tasks
                if len(completed_indices) % 5 == 0:
                    checkpoint_mgr.save_checkpoint(
                        results,
                        list(completed_indices),
                        len(self.tasks)
                    )

                progress.advance(task_bar)

                # Batch delay every 15 tasks
                if (i + 1) % 15 == 0 and (i + 1) < len(self.tasks):
                    console.print("    [dim]Batch pause (20s to avoid rate limits)...[/dim]")
                    time.sleep(20)

        # Final checkpoint
        checkpoint_mgr.save_checkpoint(results, list(completed_indices), len(self.tasks))
        console.print(f"[green][OK] Experiment 2 complete ({len(results)} tasks)[/green]")

        return results

    def run_experiment_adaptive_resilient(self, resume: bool = False):
        """Experiment 3: Adaptive with checkpointing."""
        exp_name = "exp3_adaptive"
        checkpoint_mgr = CheckpointManager(self.run_dir, exp_name)

        # Check for resume
        if resume:
            checkpoint = checkpoint_mgr.load_checkpoint()
            if checkpoint:
                console.print(f"[bold green] Resuming {exp_name} from checkpoint[/bold green]")
                console.print(f"   Completed: {checkpoint['completed_count']}/{checkpoint['total_tasks']}")
                results = checkpoint["results"]
                completed_indices = set(checkpoint["completed_indices"])
            else:
                console.print(f"[yellow]No checkpoint found for {exp_name}, starting fresh[/yellow]")
                results = []
                completed_indices = set()
        else:
            results = []
            completed_indices = set()

        console.print(f"\n[bold green]═══ Experiment 3/4: Adaptive Router ({len(self.tasks)} tasks) ═══[/bold green]")

        graph = build_adaptive_graph()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task_bar = progress.add_task(f"[green]Adaptive", total=len(self.tasks))

            for i, task in enumerate(self.tasks):
                # Skip if already completed
                if i in completed_indices:
                    progress.advance(task_bar)
                    continue

                # Run task with retry
                try:
                    def execute():
                        state = {
                            "task_id": task["task_id"],
                            "prompt": task["prompt"],
                            "task_type": task.get("task_type", "general")
                        }
                        if task.get("ground_truth"):
                            state["ground_truth"] = task["ground_truth"]
                        return graph.invoke(state)

                    result = self._retry_with_backoff(execute, task)
                    results.append(result)
                    completed_indices.add(i)
                    time.sleep(1.5)

                except Exception as e:
                    checkpoint_mgr.log_error(task["task_id"], i, str(e), "adaptive", self.MAX_RETRIES)
                    console.print(f"    [red][ERROR] {task['task_id']}: {str(e)[:120]}[/red]")

                    results.append({
                        "task_id": task["task_id"],
                        "route": "error",
                        "error": str(e),
                        "complexity_score": 0,
                        "accuracy_score": 0,
                        "quality_score": 0,
                        "latency_seconds": 0,
                        "token_usage": {"total": 0},
                        "estimated_cost": 0,
                        "failed": True,
                    })
                    completed_indices.add(i)
                    time.sleep(2)

                # Save checkpoint every 5 tasks
                if len(completed_indices) % 5 == 0:
                    checkpoint_mgr.save_checkpoint(
                        results,
                        list(completed_indices),
                        len(self.tasks)
                    )

                progress.advance(task_bar)

                # Batch delay every 15 tasks
                if (i + 1) % 15 == 0 and (i + 1) < len(self.tasks):
                    console.print("    [dim]Batch pause (20s to avoid rate limits)...[/dim]")
                    time.sleep(20)

        # Final checkpoint
        checkpoint_mgr.save_checkpoint(results, list(completed_indices), len(self.tasks))
        console.print(f"[green][OK] Experiment 3 complete ({len(results)} tasks)[/green]")

        return results


def save_to_run(data, filename: str, run_dir: Path):
    """Save JSON results to the versioned run directory."""
    path = run_dir / filename
    clean = []
    for r in (data if isinstance(data, list) else [data]):
        entry = {}
        for k, v in r.items():
            if k == "intermediate_steps":
                entry[k] = [
                    {
                        "agent": s.get("agent", "?"),
                        "tokens": s.get("tokens", 0),
                        "provider": s.get("provider", "?")
                    } for s in (v or [])
                ]
            elif isinstance(v, (str, int, float, bool, list, dict, type(None))):
                entry[k] = v
        clean.append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False, default=str)
    console.print(f"[dim]  → {path.name}[/dim]")


def main(resume: bool = False):
    """Main resilient experiment runner."""
    validate_keys()
    console.print("[bold green][OK] API keys loaded[/bold green]")

    # Create versioned run directory
    run_dir = get_next_run_dir()
    console.print(f"[bold cyan] Saving results to: {run_dir.name}[/bold cyan]")

    tasks = BENCHMARK_TASKS
    console.print(f"\n[bold]Running RESILIENT experiment with {len(tasks)} tasks[/bold]")
    console.print(f"  Simple: {sum(1 for t in tasks if t['difficulty']=='simple')}")
    console.print(f"  Medium: {sum(1 for t in tasks if t['difficulty']=='medium')}")
    console.print(f"  Complex: {sum(1 for t in tasks if t['difficulty']=='complex')}\n")

    if resume:
        console.print("[bold yellow][WARNING] RESUME mode enabled - will continue from checkpoints[/bold yellow]\n")

    # Save run metadata
    save_to_run({
        "run_dir": run_dir.name,
        "timestamp": datetime.now().isoformat(),
        "total_tasks": len(tasks),
        "mode": "resilient",
        "resume": resume,
        "task_distribution": {
            "simple": sum(1 for t in tasks if t['difficulty'] == 'simple'),
            "medium": sum(1 for t in tasks if t['difficulty'] == 'medium'),
            "complex": sum(1 for t in tasks if t['difficulty'] == 'complex'),
        },
    }, "run_metadata.json", run_dir)

    # Initialize runner
    runner = ResilientExperimentRunner(run_dir, tasks)

    # Run experiments
    try:
        # Experiment 1: Single LLM
        single_results = runner.run_experiment_single_llm_resilient(resume=resume)
        save_to_run(single_results, "exp1_single_llm.json", run_dir)

        # Experiment 2: Multi-Agent
        multi_results = runner.run_experiment_multi_agent_resilient(resume=resume)
        save_to_run(multi_results, "exp2_multi_agent.json", run_dir)

        # Experiment 3: Adaptive Router
        adaptive_results = runner.run_experiment_adaptive_resilient(resume=resume)
        save_to_run(adaptive_results, "exp3_adaptive.json", run_dir)

        # Comparison (import here to avoid circular dependency)
        from src.experiments.run_experiments import display_comparison, save_results

        console.print("\n[bold]═══ Generating Comparison ═══[/bold]")
        comparison = display_comparison(single_results, multi_results, adaptive_results)
        save_to_run([comparison], "experiment_comparison.json", run_dir)

        # Also save to main results dir for visualization
        save_results(single_results, "exp1_single_llm.json")
        save_results(multi_results, "exp2_multi_agent.json")
        save_results(adaptive_results, "exp3_adaptive.json")
        save_results([comparison], "experiment_comparison.json")

        # Generate visualizations
        console.print("\n[bold]═══ Generating Visualizations ═══[/bold]")
        from src.experiments.generate_visuals import generate_all
        generate_all()

        # Copy figures to run dir
        main_figures = RESULTS_DIR / "figures"
        run_figures = run_dir / "figures"
        run_figures.mkdir(exist_ok=True)
        for fig_file in main_figures.glob("*.png"):
            shutil.copy2(fig_file, run_figures / fig_file.name)

        # Success summary
        console.print(f"\n[bold green][OK] Resilient experiment complete![/bold green]")
        console.print(f"  Run directory: {run_dir}")
        console.print(f"  Results: {len(list(run_dir.glob('*.json')))} JSON files")
        console.print(f"  Figures: {len(list(run_figures.glob('*.png')))} charts")
        console.print(f"  Checkpoints: {run_dir / 'checkpoints'}")

        # Count failures
        total_failures = sum(
            1 for r in single_results + multi_results + adaptive_results
            if r.get("failed") or r.get("error")
        )
        if total_failures > 0:
            console.print(f"\n[yellow][WARNING] {total_failures} tasks failed (see error logs)[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[bold red][WARNING] Interrupted by user[/bold red]")
        console.print("[yellow]Progress saved to checkpoints. Resume with:[/yellow]")
        console.print(f"[cyan]  python run.py resilient --resume[/cyan]")
        sys.exit(1)

    except Exception as e:
        console.print(f"\n[bold red][ERROR] Fatal error: {e}[/bold red]")
        console.print("[yellow]Progress saved to checkpoints. Resume with:[/yellow]")
        console.print(f"[cyan]  python run.py resilient --resume[/cyan]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    resume_flag = "--resume" in sys.argv
    main(resume=resume_flag)
