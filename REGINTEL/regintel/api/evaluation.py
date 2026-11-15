"""
evaluation.py — FastAPI router for the System/Evaluation module.

Endpoints
---------
GET  /api/eval/results                        — Latest evaluation results
GET  /api/eval/results/{timestamp}            — Specific run results
POST /api/eval/run                            — Trigger the evaluation pipeline
GET  /api/eval/benchmark                      — Benchmark dataset metadata only

Does not touch the RAG workflow, dashboard, or explorer routers.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from services.evaluation import (
    get_evaluation_results,
    list_result_timestamps,
    load_benchmark_meta,
)

router = APIRouter(prefix="/api/eval", tags=["evaluation"])

# Track background run state in process memory
_run_state: dict[str, str] = {"status": "idle", "message": ""}

_PKG_ROOT   = Path(__file__).resolve().parent.parent  # regintel/
_RUNNER     = _PKG_ROOT / "evaluation" / "evaluation_runner.py"
_VENV_PY    = _PKG_ROOT.parent / ".venv" / "Scripts" / "python.exe"


# ---------------------------------------------------------------------------
# Results endpoints
# ---------------------------------------------------------------------------

@router.get("/results")
async def latest_results(
    k: list[int] = Query(default=[3, 5, 10], description="Recall/MRR@K values to include")
):
    """Return metrics from the most recent evaluation run."""
    try:
        return get_evaluation_results(timestamp=None, ks=tuple(sorted(set(k))))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error loading results: {exc}")


@router.get("/results/{timestamp}")
async def results_by_timestamp(
    timestamp: str,
    k: list[int] = Query(default=[3, 5, 10])
):
    """Return metrics for a specific evaluation run timestamp (YYYYMMDD_HHMMSS)."""
    available = list_result_timestamps()
    if timestamp not in available:
        raise HTTPException(
            status_code=404,
            detail=f"Timestamp {timestamp!r} not found. Available: {available}"
        )
    try:
        return get_evaluation_results(timestamp=timestamp, ks=tuple(sorted(set(k))))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error loading results: {exc}")


@router.get("/benchmark")
async def benchmark_meta():
    """Return benchmark dataset overview (questions, categories, difficulty)."""
    try:
        return load_benchmark_meta()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Evaluation run endpoint
# ---------------------------------------------------------------------------

@router.get("/run/status")
async def run_status():
    """Check whether an evaluation run is in progress."""
    return {"status": _run_state["status"], "message": _run_state["message"]}


def _do_run():
    """Blocking function executed in a background thread via BackgroundTasks."""
    global _run_state
    _run_state = {"status": "running", "message": "Evaluation pipeline started…"}
    try:
        python_exe = str(_VENV_PY) if _VENV_PY.exists() else sys.executable
        runner_path = str(_RUNNER)
        if not Path(runner_path).exists():
            _run_state = {"status": "error", "message": f"Runner not found: {runner_path}"}
            return

        result = subprocess.run(
            [python_exe, runner_path],
            cwd=str(_PKG_ROOT),
            capture_output=True,
            text=True,
            timeout=600,  # 10-minute cap
        )
        if result.returncode == 0:
            _run_state = {
                "status": "done",
                "message": "Evaluation completed. Refresh results.",
            }
        else:
            stderr_tail = result.stderr[-800:] if result.stderr else "(no stderr)"
            _run_state = {
                "status": "error",
                "message": f"Runner exited with code {result.returncode}. {stderr_tail}",
            }
    except subprocess.TimeoutExpired:
        _run_state = {"status": "error", "message": "Evaluation timed out (>10 min)."}
    except Exception as exc:
        _run_state = {"status": "error", "message": str(exc)}


@router.post("/run")
async def trigger_run(background_tasks: BackgroundTasks):
    """
    Trigger the evaluation pipeline in the background.

    Returns immediately; poll GET /api/eval/run/status for progress.
    Only one run can be active at a time.
    """
    if _run_state.get("status") == "running":
        raise HTTPException(status_code=409, detail="An evaluation run is already in progress.")
    background_tasks.add_task(_do_run)
    _run_state["status"] = "starting"
    _run_state["message"] = "Queued."
    return {"status": "starting", "message": "Evaluation pipeline queued."}

