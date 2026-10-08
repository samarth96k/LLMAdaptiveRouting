"""
Main Runner — run the adaptive routing system on tasks.

Usage:
    python -m src.main                         # run on sample tasks
    python -m src.main --task "your prompt"    # run a single task
"""

import sys
import json
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .config import validate_keys, TASKS_DIR
from .graph.builder import adaptive_router
from .evaluation.feedback import FeedbackStore


console = Console()
feedback_store = FeedbackStore()


def run_single_task(prompt: str, task_id: str = "manual", task_type: str = "general",
                    ground_truth: str = None) -> dict:
    """Run one task through the adaptive routing graph."""
    state = {
        "task_id": task_id,
        "prompt": prompt,
        "task_type": task_type,
    }
    if ground_truth:
        state["ground_truth"] = ground_truth

    result = adaptive_router.invoke(state)

    # log feedback
    if result.get("feedback"):
        feedback_store.log(result["feedback"])

    return result


def display_result(result: dict):
    """Pretty-print a single task result."""
    route = result.get("route", "?")
    route_color = "green" if route == "single_llm" else "yellow"

    console.print(Panel(
        f"[bold]{result.get('prompt', '')[:100]}...[/bold]",
        title=" Task",
        border_style="blue",
    ))

    table = Table(title="Routing Decision", show_header=False)
    table.add_row("Route", f"[{route_color}]{route}[/{route_color}]")
    table.add_row("Confidence", f"{result.get('routing_confidence', 0):.2f}")
    table.add_row("Complexity", f"{result.get('complexity_score', 0):.3f}")
    table.add_row("Reason", result.get("routing_reason", "")[:80])
    console.print(table)

    table2 = Table(title="Performance", show_header=False)
    table2.add_row("Model", result.get("model_used", "?"))
    table2.add_row("Latency", f"{result.get('latency_seconds', 0):.2f}s")
    table2.add_row("Tokens", str(result.get("token_usage", {}).get("total", 0)))
    table2.add_row("Quality", f"{result.get('quality_score', 0):.2f}")
    table2.add_row("Accuracy", f"{result.get('accuracy_score', 0):.2f}")
    table2.add_row("Cost", f"${result.get('estimated_cost', 0):.6f}")
    console.print(table2)

    console.print(Panel(
        result.get("response", "")[:500],
        title="💬 Response",
        border_style="green",
    ))

    if result.get("intermediate_steps"):
        console.print(f"\n[dim]Multi-agent steps: {len(result['intermediate_steps'])} agents used[/dim]")

    console.print("─" * 60)


def run_from_dataset(dataset_path: Path):
    """Run all tasks from a JSON dataset file."""
    with open(dataset_path, "r") as f:
        tasks = json.load(f)

    console.print(f"\n[bold blue]Running {len(tasks)} tasks from {dataset_path.name}[/bold blue]\n")

    results = []
    for i, task in enumerate(tasks):
        console.print(f"\n[bold]━━━ Task {i+1}/{len(tasks)} ━━━[/bold]")
        result = run_single_task(
            prompt=task["prompt"],
            task_id=task.get("task_id", f"task_{i}"),
            task_type=task.get("task_type", "general"),
            ground_truth=task.get("ground_truth"),
        )
        display_result(result)
        results.append(result)

    # summary
    stats = feedback_store.get_stats()
    console.print(Panel(
        json.dumps(stats, indent=2),
        title=" Session Summary",
        border_style="magenta",
    ))

    return results


def main():
    parser = argparse.ArgumentParser(description="Adaptive LLM Routing System")
    parser.add_argument("--task", type=str, help="Run a single task prompt")
    parser.add_argument("--dataset", type=str, help="Path to JSON dataset file")
    parser.add_argument("--type", type=str, default="general", help="Task type (math, code, reasoning, general)")
    args = parser.parse_args()

    # validate environment
    validate_keys()
    console.print("[bold green][OK] API keys loaded[/bold green]\n")

    if args.task:
        result = run_single_task(args.task, task_type=args.type)
        display_result(result)
    elif args.dataset:
        run_from_dataset(Path(args.dataset))
    else:
        # default: run sample tasks
        sample_path = TASKS_DIR / "sample_tasks.json"
        if sample_path.exists():
            run_from_dataset(sample_path)
        else:
            console.print("[yellow]No dataset found. Use --task to run a single prompt.[/yellow]")
            console.print("  python -m src.main --task 'What is 2+2?'")


if __name__ == "__main__":
    main()
