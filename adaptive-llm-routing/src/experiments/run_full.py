"""
Full Experiment Runner — runs all 49 tasks through 4 experiments.

Saves results to a versioned directory (run2_result, run3_result, etc.)
Includes HuggingFace fallback for Groq rate limits.
"""

import os, sys
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import json, time, shutil
from pathlib import Path
from datetime import datetime

from src.config import validate_keys, RESULTS_DIR, get_next_run_dir
from src.experiments.dataset_generator import BENCHMARK_TASKS
from src.experiments.run_experiments import (
    run_experiment_single_llm,
    run_experiment_multi_agent,
    run_experiment_adaptive,
    run_experiment_adaptive_feedback,
    display_comparison,
)
from src.experiments.generate_visuals import generate_all
from rich.console import Console

console = Console(force_terminal=True)


def save_to_run(data, filename: str, run_dir: Path):
    """Save JSON results to the versioned run directory."""
    path = run_dir / filename
    clean = []
    for r in (data if isinstance(data, list) else [data]):
        entry = {}
        for k, v in r.items():
            if k == "intermediate_steps":
                entry[k] = [{"agent": s.get("agent", "?"), "tokens": s.get("tokens", 0),
                              "provider": s.get("provider", "?")} for s in (v or [])]
            elif isinstance(v, (str, int, float, bool, list, dict, type(None))):
                entry[k] = v
        clean.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False, default=str)
    console.print(f"[dim]  → {path.name}[/dim]")


def main():
    validate_keys()
    console.print("[bold green][OK] API keys loaded[/bold green]")

    # Create versioned run directory
    run_dir = get_next_run_dir()
    console.print(f"[bold cyan] Saving results to: {run_dir.name}[/bold cyan]")

    tasks = BENCHMARK_TASKS
    console.print(f"\n[bold]Running FULL experiment with {len(tasks)} tasks[/bold]")
    console.print(f"  Simple: {sum(1 for t in tasks if t['difficulty']=='simple')}")
    console.print(f"  Medium: {sum(1 for t in tasks if t['difficulty']=='medium')}")
    console.print(f"  Complex: {sum(1 for t in tasks if t['difficulty']=='complex')}\n")

    # Save run metadata
    save_to_run({
        "run_dir": run_dir.name,
        "timestamp": datetime.now().isoformat(),
        "total_tasks": len(tasks),
        "task_distribution": {
            "simple": sum(1 for t in tasks if t['difficulty'] == 'simple'),
            "medium": sum(1 for t in tasks if t['difficulty'] == 'medium'),
            "complex": sum(1 for t in tasks if t['difficulty'] == 'complex'),
        },
    }, "run_metadata.json", run_dir)

    # Experiment 1: Single LLM
    console.print("\n[bold]═══ Experiment 1/4: Single LLM ═══[/bold]")
    single_results = run_experiment_single_llm(tasks)
    save_to_run(single_results, "exp1_single_llm.json", run_dir)

    # Experiment 2: Multi-Agent
    console.print("\n[bold]═══ Experiment 2/4: Multi-Agent ═══[/bold]")
    multi_results = run_experiment_multi_agent(tasks)
    save_to_run(multi_results, "exp2_multi_agent.json", run_dir)

    # Experiment 3: Adaptive Router
    console.print("\n[bold]═══ Experiment 3/4: Adaptive Router ═══[/bold]")
    adaptive_results = run_experiment_adaptive(tasks)
    save_to_run(adaptive_results, "exp3_adaptive.json", run_dir)

    # Also save to main results dir (generate_visuals reads from there)
    from src.experiments.run_experiments import save_results
    save_results(single_results, "exp1_single_llm.json")
    save_results(multi_results, "exp2_multi_agent.json")
    save_results(adaptive_results, "exp3_adaptive.json")

    # Comparison
    comparison = display_comparison(single_results, multi_results, adaptive_results)
    save_to_run([comparison], "experiment_comparison.json", run_dir)
    save_results([comparison], "experiment_comparison.json")

    # Experiment 4: Feedback Loop
    console.print("\n[bold]═══ Experiment 4/4: Feedback Loop (3 rounds) ═══[/bold]")
    feedback_results = run_experiment_adaptive_feedback(tasks, rounds=3)
    save_to_run([{
        "threshold_history": feedback_results["threshold_history"],
        "final_stats": feedback_results["final_stats"],
    }], "exp4_feedback_loop.json", run_dir)
    save_results([{
        "threshold_history": feedback_results["threshold_history"],
        "final_stats": feedback_results["final_stats"],
    }], "exp4_feedback_loop.json")

    for round_data in feedback_results["rounds"]:
        fname = f"exp4_round_{round_data['round']}.json"
        save_to_run(round_data["results"], fname, run_dir)
        save_results(round_data["results"], fname)

    # Generate charts (reads from main results dir, saves to figures/)
    console.print("\n[bold]Generating visualizations...[/bold]")
    generate_all()

    # Copy figures to run dir
    main_figures = RESULTS_DIR / "figures"
    run_figures = run_dir / "figures"
    for fig_file in main_figures.glob("*.png"):
        shutil.copy2(fig_file, run_figures / fig_file.name)

    console.print(f"\n[bold green][OK] Full experiment complete![/bold green]")
    console.print(f"  Run directory: {run_dir}")
    console.print(f"  Results: {len(list(run_dir.glob('*.json')))} JSON files")
    console.print(f"  Figures: {len(list(run_figures.glob('*.png')))} charts")


if __name__ == "__main__":
    main()
