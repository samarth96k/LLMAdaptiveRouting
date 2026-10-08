"""
Statistical Significance Testing — Wilcoxon signed-rank test + Bootstrap CI.

Phase 2: Provides rigorous statistical comparison between system variants.
"""

import numpy as np
from scipy import stats as scipy_stats
from typing import Optional


def paired_significance_test(scores_a: list[float], scores_b: list[float],
                             metric_name: str = "metric",
                             alpha: float = 0.05) -> dict:
    """
    Wilcoxon signed-rank test (non-parametric, paired).

    Appropriate when:
      - Comparing two systems on the same set of tasks
      - Small sample sizes (N < 50)
      - No assumption of normal distribution

    Args:
        scores_a: metric scores from system A
        scores_b: metric scores from system B
        metric_name: label for the metric
        alpha: significance level

    Returns:
        dict with statistic, p_value, significant, effect_size
    """
    a = np.array(scores_a, dtype=float)
    b = np.array(scores_b, dtype=float)

    # filter out pairs where both are equal (zero differences)
    diffs = a - b
    nonzero = diffs != 0.0

    if nonzero.sum() < 3:
        return {
            "metric": metric_name,
            "test": "wilcoxon",
            "statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "effect_size": 0.0,
            "note": "Too few non-zero differences for Wilcoxon test",
            "mean_diff": float(np.mean(diffs)),
        }

    try:
        stat, p_value = scipy_stats.wilcoxon(a[nonzero], b[nonzero])
    except ValueError:
        return {
            "metric": metric_name,
            "test": "wilcoxon",
            "statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "effect_size": 0.0,
            "note": "Wilcoxon test failed (possibly all equal values)",
            "mean_diff": float(np.mean(diffs)),
        }

    # effect size: r = Z / sqrt(N)
    n = nonzero.sum()
    z_score = scipy_stats.norm.ppf(1 - p_value / 2) if p_value < 1.0 else 0.0
    effect_size = abs(z_score) / np.sqrt(n) if n > 0 else 0.0

    return {
        "metric": metric_name,
        "test": "wilcoxon",
        "statistic": round(float(stat), 4),
        "p_value": round(float(p_value), 6),
        "significant": p_value < alpha,
        "effect_size": round(float(effect_size), 4),
        "n_pairs": int(n),
        "mean_a": round(float(np.mean(a)), 4),
        "mean_b": round(float(np.mean(b)), 4),
        "mean_diff": round(float(np.mean(diffs)), 4),
    }


def compute_confidence_intervals(scores: list[float], confidence: float = 0.95,
                                 n_bootstrap: int = 1000) -> dict:
    """
    Bootstrap confidence interval for a metric.

    Args:
        scores: list of metric values
        confidence: confidence level (default 0.95)
        n_bootstrap: number of bootstrap resamples

    Returns:
        dict with mean, ci_lower, ci_upper, std
    """
    arr = np.array(scores, dtype=float)
    n = len(arr)

    if n < 2:
        mean_val = float(arr.mean()) if n > 0 else 0.0
        return {
            "mean": mean_val,
            "ci_lower": mean_val,
            "ci_upper": mean_val,
            "std": 0.0,
            "n": n,
        }

    # bootstrap resampling
    rng = np.random.default_rng(42)
    boot_means = np.array([
        rng.choice(arr, size=n, replace=True).mean()
        for _ in range(n_bootstrap)
    ])

    alpha = 1 - confidence
    ci_lower = float(np.percentile(boot_means, 100 * alpha / 2))
    ci_upper = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))

    return {
        "mean": round(float(arr.mean()), 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "std": round(float(arr.std()), 4),
        "n": n,
    }


def generate_significance_report(single_results: list[dict],
                                 multi_results: list[dict],
                                 adaptive_results: list[dict]) -> dict:
    """
    Generate a full statistical comparison report.

    Runs Wilcoxon tests between all pairs of systems for each metric
    and computes bootstrap CIs.

    Returns:
        dict with pairwise tests and per-system CIs
    """
    def extract_metric(results: list[dict], key: str,
                       fallback_key: str = None) -> list[float]:
        vals = []
        for r in results:
            v = r.get(key)
            if v is None and fallback_key:
                fb = r.get("feedback", {})
                v = fb.get(fallback_key, 0)
            vals.append(float(v) if v is not None else 0.0)
        return vals

    metrics = [
        ("accuracy", "accuracy_score", "accuracy"),
        ("quality", "quality_score", "quality"),
        ("latency", "latency_seconds", "latency"),
    ]

    systems = {
        "single_llm": single_results,
        "multi_agent": multi_results,
        "adaptive": adaptive_results,
    }

    # Pairwise significance tests
    pairwise_tests = []
    pairs = [
        ("adaptive", "single_llm"),
        ("adaptive", "multi_agent"),
        ("single_llm", "multi_agent"),
    ]

    for metric_name, key, fb_key in metrics:
        for sys_a, sys_b in pairs:
            scores_a = extract_metric(systems[sys_a], key, fb_key)
            scores_b = extract_metric(systems[sys_b], key, fb_key)
            min_len = min(len(scores_a), len(scores_b))
            if min_len > 0:
                result = paired_significance_test(
                    scores_a[:min_len], scores_b[:min_len],
                    metric_name=f"{metric_name} ({sys_a} vs {sys_b})"
                )
                pairwise_tests.append(result)

    # Per-system confidence intervals
    confidence_intervals = {}
    for sys_name, results in systems.items():
        confidence_intervals[sys_name] = {}
        for metric_name, key, fb_key in metrics:
            scores = extract_metric(results, key, fb_key)
            confidence_intervals[sys_name][metric_name] = compute_confidence_intervals(scores)

    return {
        "pairwise_tests": pairwise_tests,
        "confidence_intervals": confidence_intervals,
    }
