"""
Smoke tests — verify the system components work correctly.

Phase 2: Added tests for semantic similarity, enhanced complexity features, and statistics.
"""

import sys
import os
import warnings

# Suppress TensorFlow/transformers warnings that contaminate test output
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_complexity_estimation():
    """Test that complexity scoring produces sensible results."""
    from src.utils.complexity import estimate_complexity

    # simple task
    simple = "What is 2 + 2?"
    score_s, features_s = estimate_complexity(simple)
    assert 0.0 <= score_s <= 0.4, f"Simple task scored too high: {score_s}"

    # complex task
    complex_task = (
        "Design a distributed system for real-time data processing. "
        "Compare and contrast Apache Kafka vs RabbitMQ. "
        "Then implement a Python class that handles message queuing "
        "with step 1: connection setup, step 2: producer, step 3: consumer. "
        "Analyze the time complexity of each operation."
    )
    score_c, features_c = estimate_complexity(complex_task)
    assert score_c > score_s, f"Complex task ({score_c}) should score higher than simple ({score_s})"

    print(f"  ✓ Simple: {score_s:.3f}, Complex: {score_c:.3f}")


def test_complexity_new_features():
    """Test the Phase 2 complexity features (entropy, TF-IDF, clauses)."""
    from src.utils.complexity import compute_complexity_features

    prompt = (
        "Because the algorithm is slow, although it is correct, "
        "we should optimize it. However, if the input is small, "
        "then the current approach is acceptable."
    )
    features = compute_complexity_features(prompt)

    # Check new features exist
    assert "information_entropy" in features, "Missing information_entropy feature"
    assert "tfidf_richness" in features, "Missing tfidf_richness feature"
    assert "clause_count" in features, "Missing clause_count feature"
    assert "has_nested_clauses" in features, "Missing has_nested_clauses feature"

    # Entropy should be between 0 and 1
    assert 0.0 <= features["information_entropy"] <= 1.0, f"Entropy out of range: {features['information_entropy']}"

    # This prompt has many subordinating conjunctions
    assert features["clause_count"] >= 2, f"Expected ≥2 clause markers, got {features['clause_count']}"
    assert features["has_nested_clauses"] is True, "Should detect nested clauses"

    print(f"  ✓ Entropy: {features['information_entropy']:.3f}, Clauses: {features['clause_count']}, "
          f"TF-IDF: {features['tfidf_richness']:.3f}")


def test_config_loads():
    """Test that config loads environment variables."""
    from src.config import GROQ_API_KEY, HUGGINGFACE_API_KEY, COST_PER_1M_TOKENS

    assert GROQ_API_KEY is not None, "GROQ_API_KEY not loaded"
    assert HUGGINGFACE_API_KEY is not None, "HUGGINGFACE_API_KEY not loaded"
    assert "groq" in COST_PER_1M_TOKENS, "Missing groq in cost model"
    assert "mistral" in COST_PER_1M_TOKENS, "Missing mistral in cost model"
    print(f"  ✓ Groq key: {GROQ_API_KEY[:8]}...")
    print(f"  ✓ HF key:   {HUGGINGFACE_API_KEY[:8]}...")
    print(f"  ✓ Cost model: {len(COST_PER_1M_TOKENS)} providers")


def test_graph_builds():
    """Test that the LangGraph compiles without errors."""
    from src.graph.builder import adaptive_router

    assert adaptive_router is not None, "Graph failed to compile"
    print("  ✓ Graph compiled successfully")


def test_feedback_store():
    """Test feedback storage and retrieval."""
    from src.evaluation.feedback import FeedbackStore
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        store = FeedbackStore(store_path=Path(tmpdir) / "test_feedback.jsonl")

        store.log({
            "task_id": "test_1",
            "route": "single_llm",
            "complexity_score": 0.3,
            "accuracy": 0.9,
            "quality": 0.85,
            "latency": 1.2,
            "tokens": 500,
            "cost": 0.00005,
            "efficiency": 18000,
            "routing_correct": True,
        })

        history = store.get_history()
        assert len(history) == 1, f"Expected 1 entry, got {len(history)}"
        assert history[0]["task_id"] == "test_1"

        stats = store.get_stats()
        assert stats["total_runs"] == 1
        print(f"  ✓ Feedback store works (1 entry logged)")


def test_semantic_similarity():
    """Test that semantic similarity produces reasonable scores."""
    from src.evaluation.metrics import semantic_similarity, composite_accuracy

    # identical strings should have high similarity
    sim1 = semantic_similarity("Paris", "Paris")
    assert sim1 > 0.9, f"Identical strings should have sim > 0.9, got {sim1}"

    # related strings should have moderate similarity
    sim2 = semantic_similarity("The capital of France is Paris", "Paris is the capital of France")
    assert sim2 > 0.7, f"Paraphrased strings should have sim > 0.7, got {sim2}"

    # unrelated strings should have low similarity
    sim3 = semantic_similarity("The sky is blue", "I love pizza")
    assert sim3 < sim2, f"Unrelated should score lower than related"

    # empty/None cases
    sim4 = semantic_similarity("hello", "")
    assert sim4 == 0.0, "Empty ground truth should return 0.0"

    # composite accuracy
    comp = composite_accuracy("Paris", "Paris", llm_judge_score=1.0)
    assert comp > 0.8, f"Composite accuracy for exact match should be > 0.8, got {comp}"

    print(f"  ✓ Identical: {sim1:.3f}, Paraphrased: {sim2:.3f}, Unrelated: {sim3:.3f}")
    print(f"  ✓ Composite accuracy (exact match): {comp:.3f}")


def test_statistics():
    """Test statistical significance functions."""
    import time
    from src.evaluation.statistics import (
        paired_significance_test,
        compute_confidence_intervals,
    )
    # Brief pause to let any TF warnings from import flush through
    time.sleep(0.3)

    # significantly different distributions
    a = [0.8, 0.9, 0.85, 0.95, 0.88, 0.92, 0.87, 0.91, 0.86, 0.93]
    b = [0.5, 0.6, 0.55, 0.65, 0.58, 0.62, 0.57, 0.61, 0.56, 0.63]
    result = paired_significance_test(a, b, "test_metric")
    assert result["p_value"] < 0.05, f"Should be significant, got p={result['p_value']}"
    assert result["significant"] is True
    print(f"  \u2713 Wilcoxon: p={result['p_value']:.6f}, significant={result['significant']}")

    # CI test
    ci = compute_confidence_intervals(a)
    assert ci["ci_lower"] < ci["mean"] < ci["ci_upper"], "CI should bracket the mean"
    print(f"  \u2713 CI: [{ci['ci_lower']:.3f}, {ci['ci_upper']:.3f}] (mean={ci['mean']:.3f})")


def test_dataset_expanded():
    """Test that the dataset was expanded correctly."""
    from src.experiments.dataset_generator import BENCHMARK_TASKS, dataset_summary

    summary = dataset_summary()
    assert summary["total"] >= 70, f"Expected ≥70 tasks, got {summary['total']}"

    # check new creative category exists
    types = summary["by_type"]
    assert "creative" in types, "Missing 'creative' task type"

    # check ground truth coverage improved
    gt_ratio = summary["with_ground_truth"] / summary["total"]
    print(f"  ✓ Total tasks: {summary['total']}")
    print(f"  ✓ Types: {types}")
    print(f"  ✓ Ground truth coverage: {gt_ratio:.0%} ({summary['with_ground_truth']}/{summary['total']})")


if __name__ == "__main__":
    print("\n🧪 Running smoke tests...\n")

    tests = [
        ("Config Loading", test_config_loads),
        ("Complexity Estimation", test_complexity_estimation),
        ("Complexity New Features", test_complexity_new_features),
        ("Graph Compilation", test_graph_builds),
        ("Feedback Store", test_feedback_store),
        ("Statistical Tests", test_statistics),       # before semantic (avoids TF warnings)
        ("Semantic Similarity", test_semantic_similarity),
        ("Dataset Expansion", test_dataset_expanded),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            sys.stdout.flush()
            print(f"[{name}]")
            sys.stdout.flush()
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*40}\n")

