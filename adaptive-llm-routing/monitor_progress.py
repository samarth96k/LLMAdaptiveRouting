"""
Progress Monitor — Real-time experiment status viewer.

Usage:
    python monitor_progress.py                    # Show all experiments
    python monitor_progress.py exp1_single_llm    # Show specific experiment
    python monitor_progress.py --watch            # Auto-refresh every 5s
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout

console = Console()


def find_latest_run_dir():
    """Find the most recent run directory."""
    results_dir = Path(__file__).parent / "data" / "results"

    run_dirs = [d for d in results_dir.iterdir()
                if d.is_dir() and d.name.startswith("run") and d.name.endswith("_result")]

    if not run_dirs:
        return None

    # Sort by run number
    def get_run_num(d):
        try:
            return int(d.name.replace("run", "").replace("_result", ""))
        except ValueError:
            return 0

    return sorted(run_dirs, key=get_run_num)[-1]


def load_progress(checkpoint_dir: Path, exp_name: str):
    """Load progress for a specific experiment."""
    progress_file = checkpoint_dir / f"{exp_name}_progress.json"

    if not progress_file.exists():
        return None

    try:
        with open(progress_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_errors(checkpoint_dir: Path, exp_name: str):
    """Load error log for a specific experiment."""
    error_file = checkpoint_dir / f"{exp_name}_errors.jsonl"

    if not error_file.exists():
        return []

    errors = []
    try:
        with open(error_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    errors.append(json.loads(line))
    except Exception:
        pass

    return errors


def get_status_color(percentage: float) -> str:
    """Get color based on completion percentage."""
    if percentage >= 100:
        return "green"
    elif percentage >= 75:
        return "cyan"
    elif percentage >= 50:
        return "yellow"
    elif percentage >= 25:
        return "magenta"
    else:
        return "red"


def format_time_ago(timestamp_str: str) -> str:
    """Format timestamp as 'X mins ago'."""
    try:
        ts = datetime.fromisoformat(timestamp_str)
        delta = datetime.now() - ts

        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s ago"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)}m ago"
        else:
            return f"{int(delta.total_seconds() / 3600)}h ago"
    except Exception:
        return "Unknown"


def create_progress_table(run_dir: Path):
    """Create a table showing progress of all experiments."""
    checkpoint_dir = run_dir / "checkpoints"

    if not checkpoint_dir.exists():
        return Panel("[yellow]No checkpoints found[/yellow]", title="Status")

    experiments = [
        ("exp1_single_llm", "Single LLM", "cyan"),
        ("exp2_multi_agent", "Multi-Agent", "yellow"),
        ("exp3_adaptive", "Adaptive Router", "green"),
    ]

    table = Table(title=f"Experiment Progress - {run_dir.name}")
    table.add_column("Experiment", style="bold")
    table.add_column("Status")
    table.add_column("Progress", justify="right")
    table.add_column("Completed/Total", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Last Update", justify="right")

    for exp_name, exp_label, color in experiments:
        progress = load_progress(checkpoint_dir, exp_name)
        errors = load_errors(checkpoint_dir, exp_name)

        if progress is None:
            table.add_row(
                f"[{color}]{exp_label}[/{color}]",
                "[dim]Not started[/dim]",
                "[dim]-[/dim]",
                "[dim]-/-[/dim]",
                "[dim]0[/dim]",
                "[dim]-[/dim]"
            )
        else:
            percentage = progress.get("percentage", 0)
            completed = progress.get("completed", 0)
            total = progress.get("total", 0)
            remaining = progress.get("remaining", 0)
            timestamp = progress.get("timestamp", "")

            status_color = get_status_color(percentage)

            if percentage >= 100:
                status = f"[{status_color}][OK] Complete[/{status_color}]"
            else:
                status = f"[{status_color}]* Running[/{status_color}]"

            progress_bar = f"[{status_color}]{percentage:.1f}%[/{status_color}]"

            error_count = len(errors)
            error_str = f"[red]{error_count}[/red]" if error_count > 0 else "[green]0[/green]"

            table.add_row(
                f"[{color}]{exp_label}[/{color}]",
                status,
                progress_bar,
                f"{completed}/{total}",
                error_str,
                f"[dim]{format_time_ago(timestamp)}[/dim]"
            )

    return table


def create_error_summary(run_dir: Path):
    """Create error summary panel."""
    checkpoint_dir = run_dir / "checkpoints"

    if not checkpoint_dir.exists():
        return None

    all_errors = []
    for exp_name in ["exp1_single_llm", "exp2_multi_agent", "exp3_adaptive"]:
        errors = load_errors(checkpoint_dir, exp_name)
        all_errors.extend(errors)

    if not all_errors:
        return Panel("[green][OK] No errors[/green]", title="[WARNING] Errors")

    # Group errors by provider
    provider_errors = {}
    for err in all_errors:
        provider = err.get("provider", "unknown")
        provider_errors[provider] = provider_errors.get(provider, 0) + 1

    # Format error summary
    lines = [f"[red]Total Errors: {len(all_errors)}[/red]\n"]
    lines.append("[bold]By Provider:[/bold]")
    for provider, count in sorted(provider_errors.items(), key=lambda x: -x[1]):
        lines.append(f"  {provider}: {count}")

    # Show last 3 errors
    lines.append("\n[bold]Recent Errors:[/bold]")
    for err in all_errors[-3:]:
        task_id = err.get("task_id", "?")
        error_msg = err.get("error", "")[:60]
        lines.append(f"  [dim]{task_id}:[/dim] {error_msg}...")

    return Panel("\n".join(lines), title="Errors", border_style="red")


def show_status(run_dir: Path = None, experiment: str = None):
    """Show current status."""
    if run_dir is None:
        run_dir = find_latest_run_dir()

        if run_dir is None:
            console.print("[red]No experiment runs found[/red]")
            return

    # Main progress table
    table = create_progress_table(run_dir)
    console.print(table)

    # Error summary
    error_panel = create_error_summary(run_dir)
    if error_panel:
        console.print("\n")
        console.print(error_panel)

    # Overall stats
    checkpoint_dir = run_dir / "checkpoints"
    if checkpoint_dir.exists():
        console.print("\n[bold]Checkpoint Directory:[/bold]")
        console.print(f"  {checkpoint_dir}")

        # Count checkpoint files
        checkpoints = list(checkpoint_dir.glob("*_checkpoint.json"))
        console.print(f"  Checkpoints: {len(checkpoints)}")


def watch_status(run_dir: Path = None, interval: int = 5):
    """Watch status with auto-refresh."""
    if run_dir is None:
        run_dir = find_latest_run_dir()

        if run_dir is None:
            console.print("[red]No experiment runs found[/red]")
            return

    try:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                # Clear and rebuild display
                layout = Layout()

                # Progress table
                progress_table = create_progress_table(run_dir)

                # Error panel
                error_panel = create_error_summary(run_dir)

                # Combine
                if error_panel:
                    layout.split_column(
                        Layout(progress_table),
                        Layout(error_panel, size=12)
                    )
                else:
                    layout.update(progress_table)

                live.update(layout)
                time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped[/yellow]")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    # Parse arguments
    watch = "--watch" in args or "-w" in args

    # Remove flags
    args = [a for a in args if not a.startswith("-")]

    # Get run directory
    run_dir = find_latest_run_dir()

    if run_dir is None:
        console.print("[red]No experiment runs found[/red]")
        console.print("[dim]Start an experiment first:[/dim]")
        console.print("  python run.py resilient")
        return

    console.print(f"[bold]Monitoring: {run_dir.name}[/bold]\n")

    if watch:
        console.print("[dim]Auto-refreshing every 5s (Press Ctrl+C to stop)[/dim]\n")
        watch_status(run_dir)
    else:
        show_status(run_dir)
        console.print("\n[dim]Tip: Use --watch for auto-refresh[/dim]")


if __name__ == "__main__":
    main()
