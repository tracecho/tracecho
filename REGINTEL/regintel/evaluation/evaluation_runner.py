"""
Tracecho / RegIntel evaluation runner.

Evaluates five retrieval strategies:
  vector, bm25, hybrid, hybrid_reranking, agentic

Metrics computed over answerable questions only:
  HitRate@5, Recall@5, Precision@5, MRR@5, nDCG@5

OOD questions are tracked separately (hallucination rate for agentic).

Results are saved as timestamped JSON and a Markdown report under
data/evaluation/results/ (relative to the repository root).
"""

import os
import json
import time
import sys
from datetime import datetime

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from evaluation.benchmark_loader import BenchmarkLoader
from evaluation.retrieval_metrics import evaluate_retrieval
from evaluation.answer_metrics import (
    calculate_citation_accuracy,
    calculate_hallucination_rate,
    evaluate_verification_agent,
)

from retrieval.embeddings import RegintelEmbeddings
from retrieval.vector_store import RegintelVectorStore
from retrieval.bm25 import RegintelBM25Store
from retrieval.metadata_store import MetadataStore
from retrieval.hybrid_search import RegintelHybridRetriever


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _build_log_entry(dataset, i, ret_ch, k=5):
    """Build per-question log dict with honest hit/rank fields."""
    item = dataset[i]
    exp_ch = item.get("expected_chunk_ids", [])
    is_ans = item.get("answerable", True)
    entry = {
        "question_id": item["id"],
        "question": item["question"],
        "answerable": is_ans,
        "expected_chunk_ids": exp_ch,
        "retrieved_chunk_ids": ret_ch,
        "hit_at_5": None,
        "first_relevant_rank": None,
        "reciprocal_rank": None,
    }
    if is_ans and exp_ch:
        top_k = ret_ch[:k]
        entry["hit_at_5"] = any(c in top_k for c in exp_ch)
        rank = None
        for idx, c in enumerate(top_k):
            if c in exp_ch:
                rank = idx + 1
                break
        entry["first_relevant_rank"] = rank
        entry["reciprocal_rank"] = (1.0 / rank) if rank else 0.0
    return entry


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    bench_file = os.path.join(os.path.dirname(__file__), "benchmark.json")
    if not os.path.exists(bench_file):
        print(f"Benchmark file {bench_file} not found. Run generate_benchmark.py first.")
        return

    loader = BenchmarkLoader(bench_file)
    dataset = loader.get_all()

    total_q = len(dataset)
    ans_count = sum(1 for q in dataset if q.get("answerable", True))
    ood_count = total_q - ans_count

    expected_retrieval = [item["expected_chunk_ids"] for item in dataset]
    answerable = [item.get("answerable", True) for item in dataset]
    questions = [item["question"] for item in dataset]

    print("Loading retrieval indexes …")
    emb_model = RegintelEmbeddings()
    vs = RegintelVectorStore()
    if not vs.load():
        print("FAIL: FAISS index not found. Build it first.")
        return
    bs = RegintelBM25Store()
    if not bs.load():
        print("FAIL: BM25 index not found. Build it first.")
        return
    ms = MetadataStore()
    if not ms.load():
        ms.build_store()
    retriever = RegintelHybridRetriever(emb_model, vs, bs, ms)

    # ------------------------------------------------------------------
    # Try importing the agentic workflow — skip gracefully if unavailable
    # ------------------------------------------------------------------
    try:
        from graph.workflow import app as agentic_app
        _agentic_available = True
    except Exception as e:
        print(f"[INFO] Agentic workflow not importable ({e}); skipping agentic mode.")
        _agentic_available = False

    modes = ["vector", "bm25", "hybrid", "hybrid_reranking"]
    if _agentic_available:
        modes.append("agentic")

    results_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "evaluation", "results")
    )
    os.makedirs(results_dir, exist_ok=True)

    comparisons = []
    agentic_metrics = {}
    per_q_logs = {}

    report = {
        "run_timestamp": datetime.now().isoformat(),
        "benchmark_size": total_q,
        "answerable_questions": ans_count,
        "out_of_domain_questions": ood_count,
        "methods": {},
    }

    # Category distribution
    cats = {}
    for d in dataset:
        c = d.get("category", "Unknown")
        cats[c] = cats.get(c, 0) + 1

    # -----------------------------------------------------------------------
    # Evaluate each mode
    # -----------------------------------------------------------------------
    for mode in modes:
        print(f"\n{'=' * 62}")
        print(f"  RETRIEVAL EVALUATION: {mode.upper()}")
        print(f"{'=' * 62}")

        actual_retrieval = []
        actual_answers = []
        errors = []
        start = time.time()
        per_q_logs[mode] = []

        if mode == "agentic":
            for i, q in enumerate(questions):
                try:
                    out = agentic_app.invoke({"query": q})
                    chunks = out.get("chunks", [])
                    verif = out.get("verification_output", {})
                    final = out.get("final_output", {}) or {}
                    retrieved = [c["chunk_id"] for c in chunks if "chunk_id" in c]
                    ans = {
                        "answer": final.get("answer", ""),
                        "citations": final.get("citations", []),
                        "evidence_insufficient": final.get("evidence_insufficient", False),
                        "_verification_output": verif,
                    }
                except Exception as e:
                    err_msg = f"q[{i}] {e}"
                    print(f"  [ERROR] agentic {err_msg}")
                    errors.append(err_msg)
                    retrieved = []
                    ans = {"answer": "", "citations": [], "evidence_insufficient": True,
                           "_verification_output": {}}
                actual_retrieval.append(retrieved)
                actual_answers.append(ans)
                entry = _build_log_entry(dataset, i, retrieved)
                entry["agentic_answer"] = ans.get("answer", "")
                entry["citations"] = ans.get("citations", [])
                entry["evidence_insufficient"] = ans.get("evidence_insufficient", False)
                entry["verification_output"] = ans.get("_verification_output", {})
                per_q_logs[mode].append(entry)
        else:
            for i, q in enumerate(questions):
                temp_type = dataset[i].get("temporal_type", "UNSPECIFIED")
                t_year = "2020" if temp_type == "HISTORICAL" else ""
                retrieved = []
                try:
                    if mode == "vector":
                        q_emb = emb_model.embed_query(q)
                        res = vs.search(q_emb, k=15)
                        retrieved = [x[0] for x in res]
                    elif mode == "bm25":
                        res = bs.search(q, k=15)
                        retrieved = [x[0] for x in res]
                    elif mode == "hybrid":
                        res = retriever.search(
                            q, alpha=0.6, k=15,
                            skip_rerank=True,
                            temporal_type=temp_type,
                            temporal_year=t_year,
                        )
                        retrieved = [c["chunk_id"] for c in res]
                    elif mode == "hybrid_reranking":
                        res = retriever.search(
                            q, alpha=0.6, k=15,
                            skip_rerank=False,
                            temporal_type=temp_type,
                            temporal_year=t_year,
                        )
                        retrieved = [c["chunk_id"] for c in res]
                except Exception as e:
                    err_msg = f"q[{i}] {e}"
                    print(f"  [ERROR] {mode}: {err_msg}")
                    errors.append(err_msg)
                actual_retrieval.append(retrieved)
                actual_answers.append({})
                per_q_logs[mode].append(_build_log_entry(dataset, i, retrieved))

        dur = time.time() - start

        # Split actual_retrieval into answerable vs OOD for separate reporting
        ans_actual = [r for r, a in zip(actual_retrieval, answerable) if a]
        ans_expected = [e for e, a in zip(expected_retrieval, answerable) if a]
        ood_actual = [r for r, a in zip(actual_retrieval, answerable) if not a]

        # Compute metrics over answerable questions only
        metrics = evaluate_retrieval(ans_actual, ans_expected, k=5)
        metrics["answerable_count"] = len(ans_actual)
        metrics["ood_count"] = ood_count
        metrics["duration_sec"] = round(dur, 2)
        metrics["errors"] = len(errors)

        report["methods"][mode] = metrics

        print(f"  Questions evaluated (answerable): {len(ans_actual)}")
        for name, val in metrics.items():
            if isinstance(val, float):
                print(f"  {name}: {val:.4f}")

        row = {
            "Method": mode,
            "HitRate@5": f"{metrics['HitRate@5']:.4f}",
            "Recall@5": f"{metrics['Recall@5']:.4f}",
            "Precision@5": f"{metrics['Precision@5']:.4f}",
            "MRR@5": f"{metrics['MRR@5']:.4f}",
            "nDCG@5": f"{metrics['nDCG@5']:.4f}",
        }
        comparisons.append(row)

        # Agentic answer-quality metrics
        if mode == "agentic":
            cit_acc = calculate_citation_accuracy(actual_answers, dataset)
            hall_rate = calculate_hallucination_rate(actual_answers, dataset)
            ver = evaluate_verification_agent(actual_answers, dataset)
            agentic_metrics = {
                "citation_accuracy": round(cit_acc, 4),
                "hallucination_rate": round(hall_rate, 4),
                "avg_latency_sec": round(dur / total_q, 2),
                "verification_metrics": ver,
            }
            report["agentic_answer_metrics"] = agentic_metrics

    # -----------------------------------------------------------------------
    # Save outputs
    # -----------------------------------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary_file = os.path.join(results_dir, f"evaluation_summary_{timestamp}.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    detail_file = os.path.join(results_dir, f"evaluation_detailed_{timestamp}.json")
    with open(detail_file, "w", encoding="utf-8") as f:
        json.dump(per_q_logs, f, indent=2)

    # -----------------------------------------------------------------------
    # Markdown report (timestamped filename)
    # -----------------------------------------------------------------------
    col_w = 22
    header = (
        f"{'Method':<{col_w}} {'HitRate@5':<12} {'Recall@5':<12} "
        f"{'Precision@5':<14} {'MRR@5':<10} {'nDCG@5':<10}"
    )
    sep = "-" * len(header)
    table_rows = []
    for c in comparisons:
        label = {
            "hybrid_reranking": "Hybrid + Reranking",
            "agentic": "Agentic RAG",
            "bm25": "BM25",
            "hybrid": "Hybrid",
            "vector": "Vector",
        }.get(c["Method"], c["Method"])
        table_rows.append(
            f"{label:<{col_w}} {c['HitRate@5']:<12} {c['Recall@5']:<12} "
            f"{c['Precision@5']:<14} {c['MRR@5']:<10} {c['nDCG@5']:<10}"
        )

    cat_lines = "\n".join(f"| {k} | {v} |" for k, v in sorted(cats.items()))
    method_rows_md = "\n".join(
        f"| {r['Method']} | {r['HitRate@5']} | {r['Recall@5']} | "
        f"{r['Precision@5']} | {r['MRR@5']} | {r['nDCG@5']} |"
        for r in comparisons
    )

    agentic_section = ""
    if agentic_metrics:
        agentic_section = f"""
## 6. Agentic Answer Quality

| Metric | Value |
|--------|-------|
| Citation Accuracy | {agentic_metrics.get('citation_accuracy', 'N/A')} |
| Hallucination Rate (OOD) | {agentic_metrics.get('hallucination_rate', 'N/A')} |
| Avg Latency (sec) | {agentic_metrics.get('avg_latency_sec', 'N/A')} |

### Verification Agent Confusion Matrix
```
{json.dumps(agentic_metrics.get('verification_metrics', {}), indent=2)}
```
"""

    report_md = f"""# RegIntel Evaluation Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 1. Benchmark Overview

| Field | Count |
|-------|-------|
| Total questions | {total_q} |
| Answerable | {ans_count} |
| Out-of-domain | {ood_count} |

## 2. Question Distribution

| Category | Count |
|----------|-------|
{cat_lines}

## 3. Retrieval Metrics (answerable questions only, K=5)

> Metrics are computed **only over questions with at least one expected chunk ID**.
> OOD/unanswerable questions ({ood_count}) are excluded from all metric denominators.

| Method | HitRate@5 | Recall@5 | Precision@5 | MRR@5 | nDCG@5 |
|--------|-----------|----------|-------------|-------|--------|
{method_rows_md}

## 4. Method Definitions

- **HitRate@5** – ≥1 expected chunk in top-5 retrieved
- **Recall@5** – |expected ∩ retrieved@5| / |expected|
- **Precision@5** – |expected ∩ retrieved@5| / 5
- **MRR@5** – 1/rank of first relevant chunk in top-5
- **nDCG@5** – normalised discounted cumulative gain, binary relevance
{agentic_section}
## 5. Files

| File | Path |
|------|------|
| Summary JSON | `{os.path.basename(summary_file)}` |
| Per-question JSON | `{os.path.basename(detail_file)}` |

## 6. Reproduction

```bash
cd REGINTEL/regintel
python evaluation/validate_benchmark.py && python evaluation/evaluation_runner.py
```
"""

    report_md_file = os.path.join(results_dir, f"evaluation_report_{timestamp}.md")
    with open(report_md_file, "w", encoding="utf-8") as f:
        f.write(report_md)

    # -----------------------------------------------------------------------
    # Final console summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  REGINTEL EVALUATION COMPLETE")
    print("=" * 70)
    print(f"\nBenchmark: {total_q} total ({ans_count} answerable, {ood_count} OOD)")
    print("\nCategory distribution:")
    for ct, ct_count in sorted(cats.items()):
        print(f"  {ct}: {ct_count}")

    print(f"\n{header}")
    print(sep)
    for row in table_rows:
        print(row)
    print(sep)

    if agentic_metrics:
        print(f"\nCitation Accuracy:   {agentic_metrics.get('citation_accuracy', 'N/A')}")
        print(f"Hallucination Rate:  {agentic_metrics.get('hallucination_rate', 'N/A')}")
        print(f"Avg Agentic Latency: {agentic_metrics.get('avg_latency_sec', 'N/A')} sec")

    print(f"\nResults saved to: {results_dir}")
    print(f"  {os.path.basename(summary_file)}")
    print(f"  {os.path.basename(detail_file)}")
    print(f"  {os.path.basename(report_md_file)}")
    print(f"\nReproduce with:")
    print(f"  cd REGINTEL/regintel && python evaluation/evaluation_runner.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
