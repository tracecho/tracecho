"""
Retrieval metrics for the RegIntel evaluation pipeline.

Each function accepts a parallel pair of lists:
  actual_results   – list of retrieved chunk-ID lists (one per question)
  expected_results – list of expected chunk-ID lists (one per question)

Questions with an empty expected list are treated as unanswerable / out-of-domain
and are **excluded** from every metric's numerator AND denominator so they do not
dilute the scores.
"""

import math
from typing import List


def _answerable_pairs(
    actual_results: List[List[str]],
    expected_results: List[List[str]],
):
    """Yield (actual, expected) for questions that have at least one expected chunk."""
    for actual, expected in zip(actual_results, expected_results):
        if expected:
            yield actual, expected


def hit_rate_at_k(
    actual_results: List[List[str]],
    expected_results: List[List[str]],
    k: int = 5,
) -> float:
    """Hit Rate@K: fraction of answerable questions where at least one
    expected chunk appears in the top-K retrieved results."""
    pairs = list(_answerable_pairs(actual_results, expected_results))
    if not pairs:
        return 0.0
    hits = sum(
        1
        for actual, expected in pairs
        if any(item in actual[:k] for item in expected)
    )
    return hits / len(pairs)


def recall_at_k(
    actual_results: List[List[str]],
    expected_results: List[List[str]],
    k: int = 5,
) -> float:
    """Average Recall@K across answerable questions.

    Recall = |relevant ∩ retrieved@K| / |relevant|
    """
    pairs = list(_answerable_pairs(actual_results, expected_results))
    if not pairs:
        return 0.0
    total = 0.0
    for actual, expected in pairs:
        hits = sum(1 for item in expected if item in actual[:k])
        total += hits / len(expected)
    return total / len(pairs)


def precision_at_k(
    actual_results: List[List[str]],
    expected_results: List[List[str]],
    k: int = 5,
) -> float:
    """Average Precision@K across answerable questions.

    Precision = |relevant ∩ retrieved@K| / |retrieved@K|
    """
    pairs = list(_answerable_pairs(actual_results, expected_results))
    if not pairs:
        return 0.0
    total = 0.0
    for actual, expected in pairs:
        actual_k = actual[:k]
        if not actual_k:
            continue
        hits = sum(1 for item in actual_k if item in expected)
        total += hits / len(actual_k)
    return total / len(pairs)


def mrr_at_k(
    actual_results: List[List[str]],
    expected_results: List[List[str]],
    k: int = 5,
) -> float:
    """Mean Reciprocal Rank@K across answerable questions."""
    pairs = list(_answerable_pairs(actual_results, expected_results))
    if not pairs:
        return 0.0
    mrr_sum = 0.0
    for actual, expected in pairs:
        for idx, item in enumerate(actual[:k]):
            if item in expected:
                mrr_sum += 1.0 / (idx + 1)
                break
    return mrr_sum / len(pairs)


def ndcg_at_k(
    actual_results: List[List[str]],
    expected_results: List[List[str]],
    k: int = 5,
) -> float:
    """Average nDCG@K across answerable questions.

    Relevance is binary (1 if chunk is expected, 0 otherwise).
    IDCG is computed assuming all expected chunks could appear in the top-K.
    """
    pairs = list(_answerable_pairs(actual_results, expected_results))
    if not pairs:
        return 0.0
    ndcg_sum = 0.0
    for actual, expected in pairs:
        actual_k = actual[:k]
        dcg = sum(
            1.0 / math.log2(idx + 2)
            for idx, item in enumerate(actual_k)
            if item in expected
        )
        # Ideal: place as many relevant docs as possible in the top positions
        ideal_hits = min(len(expected), k)
        idcg = sum(1.0 / math.log2(idx + 2) for idx in range(ideal_hits))
        if idcg > 0:
            ndcg_sum += dcg / idcg
    return ndcg_sum / len(pairs)


def evaluate_retrieval(
    actuals: List[List[str]],
    expecteds: List[List[str]],
    k: int = 5,
) -> dict:
    """Compute all five metrics in one call."""
    return {
        f"HitRate@{k}":   round(hit_rate_at_k(actuals, expecteds, k), 4),
        f"Recall@{k}":    round(recall_at_k(actuals, expecteds, k), 4),
        f"Precision@{k}": round(precision_at_k(actuals, expecteds, k), 4),
        f"MRR@{k}":       round(mrr_at_k(actuals, expecteds, k), 4),
        f"nDCG@{k}":      round(ndcg_at_k(actuals, expecteds, k), 4),
    }
