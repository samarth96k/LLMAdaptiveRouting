"""
Task Complexity Estimation — uses heuristics to score task difficulty.

Phase 1: 11 handcrafted features.

The complexity score drives the routing decision:
    - Low complexity (< threshold)  → Single LLM
    - High complexity (>= threshold) → Multi-Agent
"""

import re


def compute_complexity_features(prompt: str) -> dict:
    """
    Extract hand-crafted features that correlate with task difficulty.

    Returns 11 Phase 1 features.
    """

    words = prompt.split()

    sentences = [
        s.strip()
        for s in re.split(r'[.!?]+', prompt)
        if s.strip()
    ]

    # ---------------------------------------------------------
    # Basic text features
    # ---------------------------------------------------------

    word_count = len(words)

    avg_word_len = (
        sum(len(w) for w in words) / max(word_count, 1)
    )

    unique_ratio = (
        len(set(w.lower() for w in words))
        / max(word_count, 1)
    )

    sentence_count = max(len(sentences), 1)

    avg_sentence_len = (
        word_count / sentence_count
    )

    # ---------------------------------------------------------
    # Task-type signals
    # ---------------------------------------------------------

    has_code = bool(
        re.search(
            r'```|def |class |import |function |=>|{|}',
            prompt
        )
    )

    has_math = bool(
        re.search(
            r'[\d]+[\+\-\*/\^=]|equation|solve|calculate|integral|derivative',
            prompt,
            re.I
        )
    )

    has_multi_step = bool(
        re.search(
            r'step[s]?\s*\d|first.*then|after.*next|1\).*2\)',
            prompt,
            re.I
        )
    )

    has_comparison = bool(
        re.search(
            r'compare|contrast|difference|vs\.|versus|pros.*cons',
            prompt,
            re.I
        )
    )

    question_count = prompt.count('?')

    # ---------------------------------------------------------
    # Reasoning signal
    # ---------------------------------------------------------

    reasoning_keywords = [
        'why',
        'how',
        'explain',
        'analyze',
        'evaluate',
        'reason',
        'argue',
        'justify',
        'critique',
        'design',
        'implement',
        'optimize',
        'debug',
        'refactor'
    ]

    reasoning_density = (
        sum(
            1
            for w in words
            if w.lower() in reasoning_keywords
        )
        / max(word_count, 1)
    )

    # ---------------------------------------------------------
    # Phase 1 feature set: exactly 11 features
    # ---------------------------------------------------------

    return {
        "word_count": word_count,
        "avg_word_len": avg_word_len,
        "unique_ratio": unique_ratio,
        "sentence_count": sentence_count,
        "avg_sentence_len": avg_sentence_len,
        "has_code": has_code,
        "has_math": has_math,
        "has_multi_step": has_multi_step,
        "has_comparison": has_comparison,
        "question_count": question_count,
        "reasoning_density": reasoning_density,
    }


def estimate_complexity(prompt: str) -> tuple[float, dict]:
    """
    Estimate task complexity on a 0–1 scale.

    Phase 1 weighted heuristic scoring.

    Returns:
        (complexity_score, features_dict)
    """

    features = compute_complexity_features(prompt)

    score = 0.0

    # ---------------------------------------------------------
    # Length
    # ---------------------------------------------------------

    length_score = (
        min(features["word_count"] / 200, 1.0)
        * 0.12
    )

    score += length_score

    # ---------------------------------------------------------
    # Vocabulary diversity
    # ---------------------------------------------------------

    score += features["unique_ratio"] * 0.08

    # ---------------------------------------------------------
    # Sentence complexity
    # ---------------------------------------------------------

    sent_score = (
        min(features["avg_sentence_len"] / 30, 1.0)
        * 0.08
    )

    score += sent_score

    # ---------------------------------------------------------
    # Code signal
    # ---------------------------------------------------------

    if features["has_code"]:
        score += 0.13

    # ---------------------------------------------------------
    # Mathematical signal
    # ---------------------------------------------------------

    if features["has_math"]:
        score += 0.10

    # ---------------------------------------------------------
    # Multi-step signal
    # ---------------------------------------------------------

    if features["has_multi_step"]:
        score += 0.13

    # ---------------------------------------------------------
    # Comparison signal
    # ---------------------------------------------------------

    if features["has_comparison"]:
        score += 0.07

    # ---------------------------------------------------------
    # Question complexity
    # ---------------------------------------------------------

    q_score = (
        min(features["question_count"] / 3, 1.0)
        * 0.05
    )

    score += q_score

    # ---------------------------------------------------------
    # Reasoning density
    # ---------------------------------------------------------

    score += features["reasoning_density"] * 0.08

    # ---------------------------------------------------------
    # Keep score in [0, 1]
    # ---------------------------------------------------------

    score = max(0.0, min(1.0, score))

    return round(score, 4), features