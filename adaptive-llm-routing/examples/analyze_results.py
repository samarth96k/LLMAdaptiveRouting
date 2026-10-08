"""
Comprehensive analysis of experimental results for research paper.
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

def load_json_utf8(filepath):
    """Load JSON with UTF-8 encoding."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_experiments():
    """Generate comprehensive statistics."""
    results_dir = Path('data/results/run3_result')

    # Load results
    exp1 = load_json_utf8(results_dir / 'exp1_single_llm.json')
    exp2 = load_json_utf8(results_dir / 'exp2_multi_agent.json')
    exp3 = load_json_utf8(results_dir / 'exp3_adaptive.json')

    print("="*70)
    print("COMPREHENSIVE EXPERIMENTAL ANALYSIS")
    print("="*70)
    print()

    # Basic counts
    print("1. DATASET OVERVIEW")
    print("-" * 70)
    print(f"Total tasks per experiment: {len(exp1)}")
    print(f"Total experimental runs: 3")
    print(f"Total task evaluations: {len(exp1) + len(exp2) + len(exp3)}")
    print()

    # Task distribution
    print("2. TASK DISTRIBUTION BY TYPE")
    print("-" * 70)
    types_count = defaultdict(int)
    difficulties_count = defaultdict(int)

    for t in exp1:
        types_count[t.get('task_type', 'unknown')] += 1
        difficulties_count[t.get('difficulty', 'unknown')] += 1

    for task_type, count in sorted(types_count.items()):
        print(f"  {task_type.capitalize():15s}: {count:3d} tasks ({100*count/len(exp1):.1f}%)")
    print()

    for diff, count in sorted(difficulties_count.items()):
        print(f"  {diff.capitalize():15s}: {count:3d} tasks ({100*count/len(exp1):.1f}%)")
    print()

    # Performance metrics
    print("3. PERFORMANCE METRICS (Mean ± Std)")
    print("-" * 70)

    experiments = [
        ("Single LLM", exp1),
        ("Multi-Agent", exp2),
        ("Adaptive Router", exp3)
    ]

    metrics = ['accuracy_score', 'quality_score', 'latency_seconds']

    for metric in metrics:
        print(f"\n{metric.replace('_', ' ').title()}:")
        for name, data in experiments:
            values = [t.get(metric, 0) for t in data if metric in t]
            if values:
                mean = np.mean(values)
                std = np.std(values)
                print(f"  {name:20s}: {mean:.4f} ± {std:.4f}")

    # Cost analysis
    print("\n\nCost Analysis:")
    for name, data in experiments:
        costs = [t.get('estimated_cost', 0) for t in data]
        total_cost = sum(costs)
        print(f"  {name:20s}: ${total_cost:.6f}")

    # Token usage
    print("\n\nToken Usage:")
    for name, data in experiments:
        tokens = [t.get('token_usage', {}).get('total', 0) for t in data]
        total_tokens = sum(tokens)
        print(f"  {name:20s}: {total_tokens:,} tokens")

    # Routing distribution
    print("\n\n4. ADAPTIVE ROUTING DISTRIBUTION")
    print("-" * 70)
    routes = defaultdict(int)
    for t in exp3:
        route = t.get('route', 'unknown')
        routes[route] += 1

    for route, count in sorted(routes.items(), key=lambda x: -x[1]):
        print(f"  {route.replace('_', ' ').title():20s}: {count:3d} ({100*count/len(exp3):.1f}%)")
    print()

    # Performance by difficulty
    print("5. PERFORMANCE BY DIFFICULTY LEVEL")
    print("-" * 70)

    for diff in ['simple', 'medium', 'complex']:
        print(f"\n{diff.capitalize()} Tasks:")
        for name, data in experiments:
            filtered = [t for t in data if t.get('difficulty') == diff]
            if filtered:
                acc_mean = np.mean([t.get('accuracy_score', 0) for t in filtered])
                qual_mean = np.mean([t.get('quality_score', 0) for t in filtered])
                lat_mean = np.mean([t.get('latency_seconds', 0) for t in filtered])
                print(f"  {name:20s}: Acc={acc_mean:.3f}, Qual={qual_mean:.3f}, Lat={lat_mean:.2f}s")

    # Performance by task type
    print("\n\n6. PERFORMANCE BY TASK TYPE")
    print("-" * 70)

    for task_type in sorted(types_count.keys()):
        print(f"\n{task_type.capitalize()} Tasks:")
        for name, data in experiments:
            filtered = [t for t in data if t.get('task_type') == task_type]
            if filtered:
                acc_mean = np.mean([t.get('accuracy_score', 0) for t in filtered])
                qual_mean = np.mean([t.get('quality_score', 0) for t in filtered])
                lat_mean = np.mean([t.get('latency_seconds', 0) for t in filtered])
                print(f"  {name:20s}: Acc={acc_mean:.3f}, Qual={qual_mean:.3f}, Lat={lat_mean:.2f}s")

    # Efficiency metrics
    print("\n\n7. EFFICIENCY METRICS")
    print("-" * 70)
    print("(Quality-per-dollar, Quality-per-second)\n")

    for name, data in experiments:
        costs = [t.get('estimated_cost', 0.000001) for t in data]  # Avoid div by zero
        latencies = [t.get('latency_seconds', 0.001) for t in data]
        qualities = [t.get('quality_score', 0) for t in data]

        total_cost = sum(costs)
        total_latency = sum(latencies)
        avg_quality = np.mean(qualities)

        qual_per_dollar = avg_quality / (total_cost / len(data))
        qual_per_second = avg_quality / (total_latency / len(data))

        print(f"  {name:20s}: QPD={qual_per_dollar:.2f}, QPS={qual_per_second:.4f}")

    print("\n" + "="*70)
    print("Analysis complete. Use these statistics in your research paper.")
    print("="*70)

if __name__ == "__main__":
    analyze_experiments()
