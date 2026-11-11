# Evaluation Report

## 1. Benchmark Overview
Total questions: 50
Answerable: 45
Out-of-domain: 5

## 2. Question Distribution
- **Direct regulatory**: 15
- **Out-of-domain**: 5
- **Temporal/historical**: 7
- **Applicability**: 8
- **Exception/condition**: 5
- **Comparison**: 4
- **Multi-hop**: 4
- **Cross-regulator**: 2

## 3. Retrieval Methodology
Evaluating vector, bm25, hybrid, hybrid_reranking, and agentic.

## 4. Recall@5 Results
- **vector**: 0.3778
- **bm25**: 0.3556
- **hybrid**: 0.6444
- **hybrid_reranking**: 1.0000
- **agentic**: 0.8889

## 5. MRR Results
- **vector**: 0.2681
- **bm25**: 0.2307
- **hybrid**: 0.3778
- **hybrid_reranking**: 0.9852
- **agentic**: 0.8741

## 6. Citation Accuracy
0.0000

## 7. Hallucination Rate
0.0000

## 8. Verification Results
{
  "True Positives": 5,
  "False Positives": 45,
  "True Negatives": 0,
  "False Negatives": 0
}

## 9. Latency
10.34 seconds

## 10. Per-question failures
Evaluated 50 questions in per_q logs.

## 11. Error Analysis
(See detailed JSON for error analysis)

## 12. Comparison of Retrieval Methods
Same as table above.
