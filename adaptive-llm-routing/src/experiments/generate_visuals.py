"""
Visualization Generator — creates publication-quality charts for the research paper.

Generates:
  1. LangGraph workflow diagram
  2. Accuracy comparison (grouped bar)
  3. Latency comparison (grouped bar)
  4. Cost comparison (bar chart)
  5. Efficiency scatter plot
  6. Routing decisions heatmap
  7. Feedback adaptation line chart
  8. Complexity distribution histogram
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from src.config import RESULTS_DIR

FIGURES_DIR = RESULTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# consistent paper style
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'font.size': 12,
    'font.family': 'sans-serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
})

COLORS = {
    'single': '#3498db',
    'multi': '#e74c3c',
    'adaptive': '#2ecc71',
    'bg': '#f8f9fa',
}


def load_results(filename: str) -> list[dict]:
    path = RESULTS_DIR / filename
    if not path.exists():
        print(f"Warning: {path} not found")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_workflow_diagram():
    """Generate the LangGraph workflow diagram as a figure."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_facecolor('#fafafa')
    fig.patch.set_facecolor('#fafafa')

    # node definitions: (x, y, label, color)
    nodes = [
        (1.5, 8, "START", "#95a5a6"),
        (4, 8, "Task Analysis\n& Complexity", "#3498db"),
        (7, 8, "Routing\nDecision", "#f39c12"),
        (5, 5, "Single LLM\n(llama-3.1-8b)", "#3498db"),
        (9, 5, "Multi-Agent\n(Planner→Exec→Verify)", "#e74c3c"),
        (7, 2.5, "Output\nEvaluation", "#9b59b6"),
        (10.5, 2.5, "Feedback\nLogging", "#1abc9c"),
        (13, 2.5, "END", "#95a5a6"),
    ]

    for x, y, label, color in nodes:
        w, h = 2.2, 1.3
        if label in ("START", "END"):
            w, h = 1.2, 0.8
        box = mpatches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.15", facecolor=color, edgecolor='white',
            linewidth=2, alpha=0.9
        )
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color='white')

    # edges
    arrow_style = dict(arrowstyle='->', color='#555', lw=2, mutation_scale=15)
    edges = [
        (2.1, 8, 2.9, 8),       # START → Analysis
        (5.1, 8, 5.9, 8),       # Analysis → Routing
        (6.3, 7.35, 5.3, 5.65), # Routing → Single (down-left)
        (7.7, 7.35, 8.7, 5.65), # Routing → Multi (down-right)
        (5, 4.35, 6.2, 3.15),   # Single → Eval
        (9, 4.35, 7.8, 3.15),   # Multi → Eval
        (8.1, 2.5, 9.4, 2.5),   # Eval → Feedback
        (11.6, 2.5, 12.4, 2.5), # Feedback → END
    ]

    for x1, y1, x2, y2 in edges:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=arrow_style)

    # routing labels
    ax.text(5.4, 6.9, 'complexity\n< 0.6', fontsize=8, color='#3498db',
            ha='center', style='italic')
    ax.text(8.4, 6.9, 'complexity\n≥ 0.6', fontsize=8, color='#e74c3c',
            ha='center', style='italic')

    # feedback loop arrow (dashed)
    ax.annotate('', xy=(7.3, 8.7), xytext=(10.5, 3.2),
                arrowprops=dict(arrowstyle='->', color='#1abc9c',
                               lw=1.5, ls='--', mutation_scale=12))
    ax.text(10.2, 6.2, 'Feedback\nLoop', fontsize=8, color='#1abc9c',
            ha='center', style='italic', fontweight='bold')

    ax.set_title('Adaptive LLM Routing — LangGraph Workflow',
                 fontsize=16, fontweight='bold', pad=20)

    path = FIGURES_DIR / "langgraph_workflow.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"[OK] Saved: {path}")
    return path


def generate_accuracy_comparison(single, multi, adaptive):
    """Grouped bar chart: accuracy by difficulty level."""
    difficulties = ['simple', 'medium', 'complex']

    def avg_acc_by_diff(results, diff):
        vals = [r.get("accuracy_score", r.get("feedback", {}).get("accuracy", 0))
                for r in results if _get_difficulty(r) == diff]
        return np.mean(vals) if vals else 0

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(difficulties))
    w = 0.25

    s_vals = [avg_acc_by_diff(single, d) for d in difficulties]
    m_vals = [avg_acc_by_diff(multi, d) for d in difficulties]
    a_vals = [avg_acc_by_diff(adaptive, d) for d in difficulties]

    bars1 = ax.bar(x - w, s_vals, w, label='Single LLM', color=COLORS['single'], alpha=0.85)
    bars2 = ax.bar(x, m_vals, w, label='Multi-Agent', color=COLORS['multi'], alpha=0.85)
    bars3 = ax.bar(x + w, a_vals, w, label='Adaptive', color=COLORS['adaptive'], alpha=0.85)

    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.01,
                        f'{h:.2f}', ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Task Difficulty')
    ax.set_ylabel('Average Accuracy')
    ax.set_title('Accuracy Comparison by Task Difficulty')
    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in difficulties])
    ax.set_ylim(0, 1.15)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    path = FIGURES_DIR / "accuracy_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_latency_comparison(single, multi, adaptive):
    """Grouped bar chart: latency by difficulty."""
    difficulties = ['simple', 'medium', 'complex']

    def avg_lat_by_diff(results, diff):
        vals = [r.get("latency_seconds", r.get("feedback", {}).get("latency", 0))
                for r in results if _get_difficulty(r) == diff]
        return np.mean(vals) if vals else 0

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(difficulties))
    w = 0.25

    s_vals = [avg_lat_by_diff(single, d) for d in difficulties]
    m_vals = [avg_lat_by_diff(multi, d) for d in difficulties]
    a_vals = [avg_lat_by_diff(adaptive, d) for d in difficulties]

    ax.bar(x - w, s_vals, w, label='Single LLM', color=COLORS['single'], alpha=0.85)
    ax.bar(x, m_vals, w, label='Multi-Agent', color=COLORS['multi'], alpha=0.85)
    ax.bar(x + w, a_vals, w, label='Adaptive', color=COLORS['adaptive'], alpha=0.85)

    ax.set_xlabel('Task Difficulty')
    ax.set_ylabel('Average Latency (seconds)')
    ax.set_title('Latency Comparison by Task Difficulty')
    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in difficulties])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    path = FIGURES_DIR / "latency_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_cost_comparison(single, multi, adaptive):
    """Bar chart: total cost per system."""
    def total_cost(results):
        return sum(r.get("estimated_cost", r.get("feedback", {}).get("cost", 0))
                   for r in results)

    fig, ax = plt.subplots(figsize=(8, 5))
    systems = ['Single LLM', 'Multi-Agent', 'Adaptive']
    costs = [total_cost(single), total_cost(multi), total_cost(adaptive)]
    colors = [COLORS['single'], COLORS['multi'], COLORS['adaptive']]

    bars = ax.bar(systems, costs, color=colors, alpha=0.85, width=0.5)
    for bar, cost in zip(bars, costs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'${cost:.5f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('Total Estimated Cost ($)')
    ax.set_title('Total Cost Comparison')
    ax.grid(axis='y', alpha=0.3)

    path = FIGURES_DIR / "cost_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_efficiency_scatter(single, multi, adaptive):
    """Scatter: accuracy vs cost per task, colored by system."""
    fig, ax = plt.subplots(figsize=(10, 7))

    for results, label, color in [
        (single, 'Single LLM', COLORS['single']),
        (multi, 'Multi-Agent', COLORS['multi']),
        (adaptive, 'Adaptive', COLORS['adaptive']),
    ]:
        accs = [r.get("accuracy_score", r.get("feedback", {}).get("accuracy", 0)) for r in results]
        costs = [max(r.get("estimated_cost", r.get("feedback", {}).get("cost", 0)), 1e-7) for r in results]
        ax.scatter(costs, accs, label=label, color=color, alpha=0.6, s=80, edgecolors='white')

    ax.set_xlabel('Estimated Cost ($)')
    ax.set_ylabel('Accuracy')
    ax.set_title('Accuracy vs Cost — Efficiency Frontier')
    ax.legend()
    ax.grid(alpha=0.3)

    path = FIGURES_DIR / "efficiency_scatter.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_routing_distribution(adaptive):
    """Pie chart showing routing decisions."""
    single_count = sum(1 for r in adaptive if r.get("route") == "single_llm")
    multi_count = sum(1 for r in adaptive if r.get("route") == "multi_agent")

    fig, ax = plt.subplots(figsize=(8, 6))
    sizes = [single_count, multi_count]
    labels = [f'Single LLM\n({single_count} tasks)', f'Multi-Agent\n({multi_count} tasks)']
    colors = [COLORS['single'], COLORS['multi']]
    explode = (0.05, 0.05)

    ax.pie(sizes, labels=labels, colors=colors, explode=explode,
           autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
    ax.set_title('Adaptive Router — Routing Distribution')

    path = FIGURES_DIR / "routing_distribution.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_feedback_adaptation():
    """Line chart showing threshold adaptation over rounds."""
    fb_path = RESULTS_DIR / "exp4_feedback_loop.json"
    if not fb_path.exists():
        print("[WARNING] No feedback data yet")
        return

    with open(fb_path) as f:
        data = json.load(f)

    if not data:
        return

    thresholds = data[0].get("threshold_history", [])
    if not thresholds:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    rounds = list(range(len(thresholds)))
    ax.plot(rounds, thresholds, 'o-', color='#8e44ad', linewidth=2,
            markersize=10, markerfacecolor='white', markeredgewidth=2)

    for i, t in enumerate(thresholds):
        ax.annotate(f'{t:.3f}', (i, t), textcoords="offset points",
                    xytext=(0, 12), ha='center', fontsize=10)

    ax.set_xlabel('Round')
    ax.set_ylabel('Complexity Threshold')
    ax.set_title('Feedback Loop — Threshold Adaptation Over Rounds')
    ax.set_xticks(rounds)
    ax.set_xticklabels(['Initial'] + [f'Round {i}' for i in range(1, len(rounds))])
    ax.grid(alpha=0.3)

    path = FIGURES_DIR / "feedback_adaptation.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_complexity_histogram():
    """Histogram of complexity scores across all tasks."""
    from src.experiments.dataset_generator import BENCHMARK_TASKS
    from src.utils.complexity import estimate_complexity

    scores = []
    diffs = []
    for t in BENCHMARK_TASKS:
        s, _ = estimate_complexity(t["prompt"])
        scores.append(s)
        diffs.append(t["difficulty"])

    fig, ax = plt.subplots(figsize=(10, 6))

    for diff, color in [('simple', '#3498db'), ('medium', '#f39c12'), ('complex', '#e74c3c')]:
        vals = [s for s, d in zip(scores, diffs) if d == diff]
        ax.hist(vals, bins=10, alpha=0.6, label=diff.capitalize(), color=color, edgecolor='white')

    ax.axvline(x=0.6, color='red', linestyle='--', linewidth=2, label='Routing Threshold (0.6)')
    ax.set_xlabel('Complexity Score')
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Task Complexity Score Distribution')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    path = FIGURES_DIR / "complexity_distribution.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def _get_difficulty(result: dict) -> str:
    """Map task_id back to difficulty level."""
    tid = result.get("task_id", "")
    if "simple" in tid:
        return "simple"
    elif "medium" in tid:
        return "medium"
    elif "complex" in tid:
        return "complex"
    return "unknown"


def _get_task_type(result: dict) -> str:
    """Map task_id back to task type."""
    tid = result.get("task_id", "")
    if "math" in tid:
        return "math"
    elif "code" in tid:
        return "code"
    elif "reas" in tid:
        return "reasoning"
    elif "creative" in tid:
        return "creative"
    return "general"


def generate_radar_chart(single, multi, adaptive):
    """Radar chart: 5-axis comparison (accuracy, quality, latency_inv, cost_inv, efficiency)."""
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    categories = ['Accuracy', 'Quality', 'Speed\n(1/latency)', 'Cost\nEfficiency', 'Token\nEfficiency']
    N = len(categories)

    def compute_axes(results):
        accs = [r.get("accuracy_score", r.get("feedback", {}).get("accuracy", 0)) for r in results]
        quals = [r.get("quality_score", r.get("feedback", {}).get("quality", 0)) for r in results]
        lats = [r.get("latency_seconds", r.get("feedback", {}).get("latency", 1)) for r in results]
        costs = [max(r.get("estimated_cost", r.get("feedback", {}).get("cost", 0)), 1e-7) for r in results]
        tokens = [r.get("token_usage", {}).get("total", 0) if isinstance(r.get("token_usage"), dict) else 0 for r in results]

        avg_acc = np.mean(accs) if accs else 0
        avg_qual = np.mean(quals) if quals else 0
        avg_speed = 1.0 / max(np.mean(lats), 0.01)
        avg_cost_eff = 1.0 / max(sum(costs), 1e-7)
        avg_token_eff = 1.0 / max(sum(tokens) / max(len(tokens), 1), 1)
        return [avg_acc, avg_qual, avg_speed, avg_cost_eff, avg_token_eff]

    s_vals = compute_axes(single)
    m_vals = compute_axes(multi)
    a_vals = compute_axes(adaptive)

    # Normalize all to [0, 1] relative to max across systems
    all_vals = np.array([s_vals, m_vals, a_vals])
    maxima = all_vals.max(axis=0)
    maxima[maxima == 0] = 1
    s_norm = (np.array(s_vals) / maxima).tolist()
    m_norm = (np.array(m_vals) / maxima).tolist()
    a_norm = (np.array(a_vals) / maxima).tolist()

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    for vals, label, color in [
        (s_norm, 'Single LLM', COLORS['single']),
        (m_norm, 'Multi-Agent', COLORS['multi']),
        (a_norm, 'Adaptive', COLORS['adaptive']),
    ]:
        vals_plot = vals + vals[:1]
        ax.plot(angles, vals_plot, 'o-', linewidth=2, label=label, color=color)
        ax.fill(angles, vals_plot, alpha=0.15, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 1.1)
    ax.set_title('System Comparison — Radar Chart', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

    path = FIGURES_DIR / "radar_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_category_heatmap(single, multi, adaptive):
    """Heatmap: accuracy by task category × system."""
    categories = ['math', 'code', 'reasoning', 'general', 'creative']
    systems = ['Single LLM', 'Multi-Agent', 'Adaptive']
    all_results = [single, multi, adaptive]

    matrix = np.zeros((len(categories), len(systems)))
    for j, results in enumerate(all_results):
        for i, cat in enumerate(categories):
            vals = [r.get("accuracy_score", r.get("feedback", {}).get("accuracy", 0))
                    for r in results if _get_task_type(r) == cat]
            matrix[i, j] = np.mean(vals) if vals else 0

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(range(len(systems)))
    ax.set_xticklabels(systems, fontsize=11)
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels([c.capitalize() for c in categories], fontsize=11)

    # annotate cells
    for i in range(len(categories)):
        for j in range(len(systems)):
            color = 'white' if matrix[i, j] < 0.5 else 'black'
            ax.text(j, i, f'{matrix[i, j]:.2f}', ha='center', va='center',
                    fontsize=12, fontweight='bold', color=color)

    fig.colorbar(im, ax=ax, label='Accuracy')
    ax.set_title('Accuracy by Task Category × System', fontsize=14, fontweight='bold')

    path = FIGURES_DIR / "category_heatmap.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_pareto_frontier(single, multi, adaptive):
    """Scatter with Pareto-optimal points highlighted."""
    fig, ax = plt.subplots(figsize=(10, 7))

    all_points = []
    for results, label, color in [
        (single, 'Single LLM', COLORS['single']),
        (multi, 'Multi-Agent', COLORS['multi']),
        (adaptive, 'Adaptive', COLORS['adaptive']),
    ]:
        accs = [r.get("accuracy_score", r.get("feedback", {}).get("accuracy", 0)) for r in results]
        costs = [max(r.get("estimated_cost", r.get("feedback", {}).get("cost", 0)), 1e-7) for r in results]
        ax.scatter(costs, accs, label=label, color=color, alpha=0.5, s=60, edgecolors='white')
        for a, c in zip(accs, costs):
            all_points.append((c, a))

    # compute Pareto frontier (maximize accuracy, minimize cost)
    points = sorted(all_points, key=lambda p: p[0])
    pareto = []
    max_acc = -1
    for cost, acc in points:
        if acc > max_acc:
            pareto.append((cost, acc))
            max_acc = acc

    if pareto:
        p_costs, p_accs = zip(*pareto)
        ax.plot(p_costs, p_accs, 'k--', linewidth=2, alpha=0.7, label='Pareto Frontier')
        ax.scatter(p_costs, p_accs, color='gold', s=120, zorder=5,
                   edgecolors='black', linewidth=1.5, label='Pareto Optimal')

    ax.set_xlabel('Estimated Cost ($)')
    ax.set_ylabel('Accuracy')
    ax.set_title('Pareto Frontier — Accuracy vs Cost')
    ax.legend()
    ax.grid(alpha=0.3)

    path = FIGURES_DIR / "pareto_frontier.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[OK] Saved: {path}")


def generate_all():
    """Generate all visualizations."""
    print("\nGenerating visualizations...\n")

    # always generate these
    generate_workflow_diagram()
    generate_complexity_histogram()

    # load experiment results
    single = load_results("exp1_single_llm.json")
    multi = load_results("exp2_multi_agent.json")
    adaptive = load_results("exp3_adaptive.json")

    if single and multi and adaptive:
        generate_accuracy_comparison(single, multi, adaptive)
        generate_latency_comparison(single, multi, adaptive)
        generate_cost_comparison(single, multi, adaptive)
        generate_efficiency_scatter(single, multi, adaptive)
        generate_routing_distribution(adaptive)
        generate_feedback_adaptation()
        # Phase 2 charts
        generate_radar_chart(single, multi, adaptive)
        generate_category_heatmap(single, multi, adaptive)
        generate_pareto_frontier(single, multi, adaptive)
        print("\n[OK] All charts generated!")
    else:
        print("\n[WARNING] Run experiments first to generate comparison charts")
        print("  Run: python src/experiments/run_experiments.py")


if __name__ == "__main__":
    generate_all()

