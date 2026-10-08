"""
Quick Experiment Runner — runs a smaller subset (15 tasks) to validate
the pipeline works before running the full 49-task benchmark.

Runs: 5 simple + 5 medium + 5 complex = 15 tasks × 3 systems = 45 API sequences
"""

import json
import time
from pathlib import Path

from src.config import validate_keys, RESULTS_DIR
from src.experiments.dataset_generator import BENCHMARK_TASKS
from src.experiments.run_experiments import (
    run_experiment_single_llm,
    run_experiment_multi_agent,
    run_experiment_adaptive,
    run_experiment_adaptive_feedback,
    save_results,
    display_comparison,
)
from src.experiments.generate_visuals import generate_all
from rich.console import Console

console = Console()


def select_subset(tasks, n_per_difficulty=5):
    """Pick n tasks per difficulty level."""
    subset = []
    for diff in ["simple", "medium", "complex"]:
        filtered = [t for t in tasks if t["difficulty"] == diff]
        subset.extend(filtered[:n_per_difficulty])
    return subset


def main():
    validate_keys()
    console.print("[bold green][OK] API keys loaded[/bold green]")

    tasks = select_subset(BENCHMARK_TASKS, n_per_difficulty=5)
    console.print(f"\n[bold]Running quick experiment with {len(tasks)} tasks[/bold]")
    console.print(f"  Simple: {sum(1 for t in tasks if t['difficulty']=='simple')}")
    console.print(f"  Medium: {sum(1 for t in tasks if t['difficulty']=='medium')}")
    console.print(f"  Complex: {sum(1 for t in tasks if t['difficulty']=='complex')}\n")

    # Experiment 1: Single LLM
    console.print("[bold]Starting Experiment 1/4...[/bold]")
    single_results = run_experiment_single_llm(tasks)
    save_results(single_results, "exp1_single_llm.json")

    # Experiment 2: Multi-Agent
    console.print("[bold]Starting Experiment 2/4...[/bold]")
    multi_results = run_experiment_multi_agent(tasks)
    save_results(multi_results, "exp2_multi_agent.json")

    # Experiment 3: Adaptive
    console.print("[bold]Starting Experiment 3/4...[/bold]")
    adaptive_results = run_experiment_adaptive(tasks)
    save_results(adaptive_results, "exp3_adaptive.json")

    # Comparison
    

    # Experiment 4: Adaptive Routing + Feedback
    console.print("[bold]Starting Experiment 4/4 (Feedback Loop)...[/bold]")
    feedback_results = run_experiment_adaptive_feedback(tasks)

    save_results(
    feedback_results,
    "exp4_feedback_loop.json"
)
        
    # Comparison
    comparison = display_comparison(single_results, multi_results, adaptive_results)
    save_results([comparison], "experiment_comparison.json")

    # Generate all charts
    console.print("\n[bold]Generating visualizations...[/bold]")
    generate_all()

    console.print("\n[bold green][OK] All experiments and visualizations complete![/bold green]")
    console.print(f"  Results: {RESULTS_DIR}")
    console.print(f"  Figures: {RESULTS_DIR / 'figures'}")


if __name__ == "__main__":
    main()
