"""
evaluation.py — Evaluation data service for the TRACECHO System/Evaluation module.

Responsibilities:
- Discover persisted evaluation result files (timestamped JSON pairs).
- Load and parse summary + detailed results without reimplementing logic.
- Compute Recall@K and MRR@K for configurable K values from the detailed
  per-question data (which carries retrieved_chunk_ids + expected_chunk_ids).
- Expose benchmark metadata (size, category breakdown, difficulty).
- Never invent or hardcode metric values.

The expensive evaluation run itself is delegated to evaluation_runner.py via
a subprocess call in the API layer — this module only reads persisted files.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PKG_ROOT   = Path(__file__).resolve().parent.parent  # regintel/
_RESULTS_DIR = _PKG_ROOT.parent / "data" / "evaluation" / "results"
_BENCH_FILE  = _PKG_ROOT / "evaluation" / "benchmark.json"

METHOD_LABELS = {
    "vector":           "Vector",
    "bm25":             "BM25",
    "hybrid":           "Hybrid",
    "hybrid_reranking": "Hybrid + Reranking",
    "agentic":          "Agentic RAG",
}


# ---------------------------------------------------------------------------
# Metric helpers (computed from per-question detail — no runtime retrieval)
# ---------------------------------------------------------------------------

def _recall_at_k(entries: list[dict], k: int) -> float:
    """Average Recall@K across answerable questions only."""
    answerable = [e for e in entries if e.get("answerable") and e.get("expected_chunk_ids")]
    if not answerable:
        return 0.0
    total = 0.0
    for e in answerable:
        retrieved_k = set((e.get("retrieved_chunk_ids") or [])[:k])
        expected    = set(e.get("expected_chunk_ids") or [])
        total += len(retrieved_k & expected) / len(expected)
    return round(total / len(answerable), 4)


def _mrr_at_k(entries: list[dict], k: int) -> float:
    """Mean Reciprocal Rank@K across answerable questions only."""
    answerable = [e for e in entries if e.get("answerable") and e.get("expected_chunk_ids")]
    if not answerable:
        return 0.0
    mrr_sum = 0.0
    for e in answerable:
        retrieved_k = (e.get("retrieved_chunk_ids") or [])[:k]
        expected    = set(e.get("expected_chunk_ids") or [])
        for idx, chunk_id in enumerate(retrieved_k):
            if chunk_id in expected:
                mrr_sum += 1.0 / (idx + 1)
                break
    return round(mrr_sum / len(answerable), 4)


def _hit_rate_at_k(entries: list[dict], k: int) -> float:
    answerable = [e for e in entries if e.get("answerable") and e.get("expected_chunk_ids")]
    if not answerable:
        return 0.0
    hits = sum(
        1 for e in answerable
        if any(c in set(e.get("expected_chunk_ids") or [])
               for c in (e.get("retrieved_chunk_ids") or [])[:k])
    )
    return round(hits / len(answerable), 4)


def _compute_multi_k(entries: list[dict], ks: tuple[int, ...] = (3, 5, 10)) -> dict[str, Any]:
    return {
        **{f"Recall@{k}":  _recall_at_k(entries, k)   for k in ks},
        **{f"MRR@{k}":     _mrr_at_k(entries, k)      for k in ks},
        **{f"HitRate@{k}": _hit_rate_at_k(entries, k) for k in ks},
    }


# ---------------------------------------------------------------------------
# Result file discovery
# ---------------------------------------------------------------------------

def _ts_from_filename(name: str) -> str | None:
    m = re.search(r"(\d{8}_\d{6})", name)
    return m.group(1) if m else None


def list_result_timestamps() -> list[str]:
    """Return available result timestamps (most recent first)."""
    if not _RESULTS_DIR.exists():
        return []
    seen: set[str] = set()
    for f in _RESULTS_DIR.glob("evaluation_summary_*.json"):
        ts = _ts_from_filename(f.name)
        if ts:
            seen.add(ts)
    return sorted(seen, reverse=True)


def _latest_timestamp() -> str | None:
    ts_list = list_result_timestamps()
    return ts_list[0] if ts_list else None


# ---------------------------------------------------------------------------
# Load persisted results
# ---------------------------------------------------------------------------

def load_summary(timestamp: str | None = None) -> dict[str, Any] | None:
    """Load a summary JSON for the given (or latest) timestamp."""
    ts = timestamp or _latest_timestamp()
    if not ts:
        return None
    path = _RESULTS_DIR / f"evaluation_summary_{ts}.json"
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def load_detailed(timestamp: str | None = None) -> dict[str, list[dict]] | None:
    """Load per-question detail JSON for the given (or latest) timestamp."""
    ts = timestamp or _latest_timestamp()
    if not ts:
        return None
    path = _RESULTS_DIR / f"evaluation_detailed_{ts}.json"
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Benchmark metadata
# ---------------------------------------------------------------------------

def load_benchmark_meta() -> dict[str, Any]:
    """Return benchmark overview: size, categories, difficulty, regulators."""
    if not _BENCH_FILE.exists():
        return {"available": False}
    try:
        with open(_BENCH_FILE, encoding="utf-8") as fh:
            items: list[dict] = json.load(fh)
    except Exception:
        return {"available": False}

    total      = len(items)
    answerable = sum(1 for q in items if q.get("answerable", True))
    ood        = total - answerable

    categories: dict[str, int] = {}
    difficulties: dict[str, int] = {}
    regulators: dict[str, int] = {}

    for q in items:
        cat  = q.get("category", "Unknown") or "Unknown"
        diff = q.get("difficulty", "Unknown") or "Unknown"
        reg  = q.get("regulator", "Unknown") or "Unknown"
        categories[cat]   = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1
        regulators[reg]   = regulators.get(reg, 0) + 1

    return {
        "available":    True,
        "total":        total,
        "answerable":   answerable,
        "out_of_domain": ood,
        "categories":   categories,
        "difficulties": difficulties,
        "regulators":   regulators,
    }


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def get_evaluation_results(
    timestamp: str | None = None,
    ks: tuple[int, ...] = (3, 5, 10),
) -> dict[str, Any]:
    """
    Return a fully assembled evaluation result dict ready for the API/UI.

    Contains:
      - timestamp
      - benchmark meta
      - per-method metrics at multiple K values (derived from detailed data)
      - per-question detail for the question table
      - available timestamps (for history selector)
    """
    ts = timestamp or _latest_timestamp()
    timestamps_available = list_result_timestamps()

    if not ts:
        return {
            "available": False,
            "message": "No evaluation results found. Run the evaluation pipeline first.",
            "timestamps": timestamps_available,
            "benchmark": load_benchmark_meta(),
        }

    summary  = load_summary(ts)
    detailed = load_detailed(ts)

    if summary is None and detailed is None:
        return {
            "available": False,
            "message": f"Result files for timestamp {ts} could not be loaded.",
            "timestamps": timestamps_available,
            "benchmark": load_benchmark_meta(),
        }

    # --- Compute multi-K metrics from per-question detail ---
    method_metrics: dict[str, dict] = {}

    if detailed:
        for method, entries in detailed.items():
            method_metrics[method] = {
                "label": METHOD_LABELS.get(method, method),
                **_compute_multi_k(entries, ks=ks),
                "answerable_count": sum(1 for e in entries if e.get("answerable") and e.get("expected_chunk_ids")),
                "ood_count": sum(1 for e in entries if not e.get("answerable") or not e.get("expected_chunk_ids")),
            }

    elif summary:
        # Detailed file missing but summary exists — use recall_at_5 / mrr as-is
        for method, vals in summary.get("methods", {}).items():
            method_metrics[method] = {
                "label":    METHOD_LABELS.get(method, method),
                "Recall@5": round(vals.get("recall_at_5", 0), 4),
                "MRR@5":    round(vals.get("mrr", 0), 4),
                "_partial": True,
            }

    # --- Per-question table (use hybrid_reranking as reference method) ---
    per_question: list[dict] = []
    if detailed:
        ref_method = "hybrid_reranking" if "hybrid_reranking" in detailed else next(iter(detailed), None)
        if ref_method:
            for entry in detailed[ref_method]:
                per_question.append({
                    "question_id":    entry.get("question_id", ""),
                    "question":       entry.get("question", ""),
                    "answerable":     entry.get("answerable", True),
                    "hit_at_5":       entry.get("hit_at_5"),
                    "first_rank":     entry.get("first_relevant_rank"),
                    "reciprocal_rank": entry.get("reciprocal_rank"),
                })

    # --- Parse timestamp for display ---
    display_ts = ts
    try:
        display_ts = datetime.strptime(ts, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    bench = load_benchmark_meta()

    return {
        "available":     True,
        "timestamp":     ts,
        "display_ts":    display_ts,
        "timestamps":    timestamps_available,
        "benchmark":     bench,
        "methods":       method_metrics,
        "per_question":  per_question[:50],   # cap at 50 rows
        "k_values":      list(ks),
    }

