"""
Focused unit tests for retrieval_metrics.py

Run with:
  cd REGINTEL/regintel
  python -m pytest evaluation/test_retrieval_metrics.py -v
or
  python evaluation/test_retrieval_metrics.py
"""

import sys
import os
import math

# Make sure the package root is in sys.path
_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from evaluation.retrieval_metrics import (
    hit_rate_at_k,
    recall_at_k,
    precision_at_k,
    mrr_at_k,
    ndcg_at_k,
    evaluate_retrieval,
)

EPS = 1e-6

# ---------------------------------------------------------------------------
# hit_rate_at_k
# ---------------------------------------------------------------------------

def test_hit_rate_perfect():
    actual   = [["a", "b", "c", "d", "e"]]
    expected = [["a"]]
    assert abs(hit_rate_at_k(actual, expected, k=5) - 1.0) < EPS

def test_hit_rate_miss():
    actual   = [["x", "y", "z"]]
    expected = [["a"]]
    assert hit_rate_at_k(actual, expected, k=5) == 0.0

def test_hit_rate_skips_ood():
    # Second question is OOD (empty expected) – should not count at all
    actual   = [["x"], []]
    expected = [["a"], []]
    assert hit_rate_at_k(actual, expected, k=5) == 0.0

def test_hit_rate_partial():
    actual   = [["a"], ["x"]]
    expected = [["a"], ["b"]]
    # 1 hit out of 2 answerable
    assert abs(hit_rate_at_k(actual, expected, k=5) - 0.5) < EPS

def test_hit_rate_ood_excluded():
    # First question OOD, second answerable and a hit
    actual   = [["junk"], ["b", "a"]]
    expected = [[], ["a"]]
    assert abs(hit_rate_at_k(actual, expected, k=5) - 1.0) < EPS

# ---------------------------------------------------------------------------
# recall_at_k
# ---------------------------------------------------------------------------

def test_recall_full():
    actual   = [["a", "b"]]
    expected = [["a", "b"]]
    assert abs(recall_at_k(actual, expected, k=5) - 1.0) < EPS

def test_recall_half():
    actual   = [["a", "x"]]
    expected = [["a", "b"]]
    assert abs(recall_at_k(actual, expected, k=5) - 0.5) < EPS

def test_recall_zero():
    actual   = [["x"]]
    expected = [["a"]]
    assert recall_at_k(actual, expected, k=5) == 0.0

def test_recall_ood_excluded():
    actual   = [["x"], ["a"]]
    expected = [[], ["a"]]
    # Only second question counts; it's a full recall
    assert abs(recall_at_k(actual, expected, k=5) - 1.0) < EPS

# ---------------------------------------------------------------------------
# precision_at_k
# ---------------------------------------------------------------------------

def test_precision_k5_one_relevant():
    # 1 relevant in top-5 retrieved of 5 => 1/5
    actual   = [["a", "x", "y", "z", "w"]]
    expected = [["a"]]
    assert abs(precision_at_k(actual, expected, k=5) - 0.2) < EPS

def test_precision_k5_all_relevant():
    actual   = [["a", "b", "c", "d", "e"]]
    expected = [["a", "b", "c", "d", "e"]]
    assert abs(precision_at_k(actual, expected, k=5) - 1.0) < EPS

def test_precision_zero():
    actual   = [["x", "y"]]
    expected = [["a"]]
    assert precision_at_k(actual, expected, k=5) == 0.0

# ---------------------------------------------------------------------------
# mrr_at_k
# ---------------------------------------------------------------------------

def test_mrr_first_position():
    actual   = [["a", "b", "c"]]
    expected = [["a"]]
    assert abs(mrr_at_k(actual, expected, k=5) - 1.0) < EPS

def test_mrr_second_position():
    actual   = [["x", "a", "b"]]
    expected = [["a"]]
    assert abs(mrr_at_k(actual, expected, k=5) - 0.5) < EPS

def test_mrr_not_in_top_k():
    actual   = [["x", "y", "z", "w", "v", "a"]]
    expected = [["a"]]
    # "a" is at position 6, beyond k=5 → 0
    assert mrr_at_k(actual, expected, k=5) == 0.0

def test_mrr_two_questions_avg():
    actual   = [["a"], ["x", "b"]]
    expected = [["a"], ["b"]]
    # RR1 = 1.0, RR2 = 0.5 → mean = 0.75
    assert abs(mrr_at_k(actual, expected, k=5) - 0.75) < EPS

def test_mrr_ood_excluded():
    actual   = [[], ["a"]]
    expected = [[], ["a"]]
    # first is OOD, second has rr=1
    assert abs(mrr_at_k(actual, expected, k=5) - 1.0) < EPS

# ---------------------------------------------------------------------------
# ndcg_at_k
# ---------------------------------------------------------------------------

def test_ndcg_perfect():
    actual   = [["a"]]
    expected = [["a"]]
    assert abs(ndcg_at_k(actual, expected, k=5) - 1.0) < EPS

def test_ndcg_zero():
    actual   = [["x"]]
    expected = [["a"]]
    assert ndcg_at_k(actual, expected, k=5) == 0.0

def test_ndcg_second_position():
    actual   = [["x", "a"]]
    expected = [["a"]]
    dcg = 1.0 / math.log2(3)   # position 2 → log2(2+1)=log2(3)
    idcg = 1.0 / math.log2(2)  # ideal: position 1 → log2(1+1)=log2(2)
    expected_ndcg = dcg / idcg
    assert abs(ndcg_at_k(actual, expected, k=5) - expected_ndcg) < EPS

# ---------------------------------------------------------------------------
# evaluate_retrieval (smoke test)
# ---------------------------------------------------------------------------

def test_evaluate_retrieval_keys():
    actual   = [["a", "b", "c", "d", "e"], ["x"]]
    expected = [["a"], ["y"]]
    result = evaluate_retrieval(actual, expected, k=5)
    assert "HitRate@5"   in result
    assert "Recall@5"    in result
    assert "Precision@5" in result
    assert "MRR@5"       in result
    assert "nDCG@5"      in result

def test_evaluate_retrieval_empty_lists():
    result = evaluate_retrieval([], [], k=5)
    for v in result.values():
        assert v == 0.0

# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
