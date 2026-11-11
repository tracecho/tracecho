# RegIntel Evaluation Framework (Phase 5)

This directory contains the reproducible benchmark and evaluation scripts for RegIntel.

## Directory Structure
- `benchmark.json`: Ground-truth benchmark containing 30 regulatory queries categorized by complexity.
- `benchmark_loader.py`: Class to load and filter the benchmark.
- `retrieval_metrics.py`: Computes Recall@k, MRR, Precision@K, nDCG deterministically.
- `answer_metrics.py`: Evaluates answers for hallucination rate, citation accuracy, and verification success.
- `evaluation_runner.py`: Standardized runner script that evaluates the system against the benchmark.
- `generate_benchmark.py`: One-off script to generate the synthetic benchmark from real corpus data.

## Running the Evaluation
To evaluate the current `agentic` capabilities of the pipeline, simply execute:
```bash
python regintel/evaluation/generate_benchmark.py 
python regintel/evaluation/evaluation_runner.py
```

## Methodology
The framework strictly tests against a subset of real RBI and SEBI questions. It prevents chain-of-thought contamination and leverages Pythonic implementations for standard retrieval measurements.

Results are persisted directly to `data/evaluation/results/`.
