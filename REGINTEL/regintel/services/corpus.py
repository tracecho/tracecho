"""
corpus.py — Document catalog service for the Explorer module.

Loads the RBI and SEBI parquet corpora once at import time (metadata columns
only — text is excluded from the catalog index to keep memory low).
Text chunks are fetched on demand for the detail view.

Source of truth: regintel/data/processed/rbi_chunks.parquet
                 regintel/data/processed/sebi_chunks.parquet

RBI fields (per chunk):
  chunk_id, document_id, regulator, document_origin, document_type,
  circular_number, issue_date, subject, validity_status, version_date,
  version_lineage, superseded_by_id, supersession_edges, text

SEBI fields (per chunk):
  chunk_id, document_id, regulator, document_type, subject,
  validity_status, text
  (no: circular_number, issue_date, version_date, version_lineage, …)
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

# ---------------------------------------------------------------------------
# Columns loaded for the catalog (excludes heavy text column)
# ---------------------------------------------------------------------------
_RBI_META_COLS = [
    "chunk_id", "document_id", "regulator", "document_type",
    "circular_number", "issue_date", "subject", "validity_status",
]
_SEBI_META_COLS = [
    "chunk_id", "document_id", "regulator", "document_type",
    "subject", "validity_status",
]


class CorpusError(RuntimeError):
    """Raised when a corpus file cannot be loaded."""


# ---------------------------------------------------------------------------
# Data loading — cached at process level so parquet is read once
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_rbi_full() -> pd.DataFrame:
    path = _DATA_DIR / "rbi_chunks.parquet"
    if not path.exists():
        raise CorpusError(f"RBI parquet not found: {path}")
    return pd.read_parquet(path)


@lru_cache(maxsize=1)
def _load_sebi_full() -> pd.DataFrame:
    path = _DATA_DIR / "sebi_chunks.parquet"
    if not path.exists():
        raise CorpusError(f"SEBI parquet not found: {path}")
    return pd.read_parquet(path)


@lru_cache(maxsize=1)
def _rbi_catalog() -> pd.DataFrame:
    """One row per unique RBI document (metadata only, no text)."""
    df = _load_rbi_full()
    # Keep only columns that exist
    cols = [c for c in _RBI_META_COLS if c in df.columns]
    meta = df[cols].copy()
    # Coerce array/object columns that made it through to str
    for col in meta.columns:
        if meta[col].dtype == object and col not in ("document_id", "regulator",
                                                       "document_type", "circular_number",
                                                       "issue_date", "subject",
                                                       "validity_status", "chunk_id"):
            meta[col] = meta[col].astype(str)
    return meta.drop_duplicates("document_id").reset_index(drop=True)


@lru_cache(maxsize=1)
def _sebi_catalog() -> pd.DataFrame:
    """One row per unique SEBI document (metadata only, no text)."""
    df = _load_sebi_full()
    cols = [c for c in _SEBI_META_COLS if c in df.columns]
    meta = df[cols].copy()
    return meta.drop_duplicates("document_id").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_str(val) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() in {"nan", "none", "null", "n/a", ""} else s


def _clean_subject(subject: str, max_len: int = 180) -> str:
    """Strip leading addressee boilerplate; truncate."""
    s = _safe_str(subject)
    # Many RBI subjects start with "All Primary..." or "The Chief Executive..."
    # Try to find the actual circular title after a comma or "Master"
    m = re.search(r'(Master (?:Circular|Direction)[^,\n]*)', s)
    if m:
        s = m.group(1).strip()
    elif len(s) > max_len:
        s = s[:max_len] + "…"
    return s or subject[:max_len]


def _doc_to_dict(row: pd.Series, regulator: str) -> dict[str, Any]:
    """Convert a catalog row to a clean JSON-serialisable dict."""
    d: dict[str, Any] = {
        "document_id": _safe_str(row.get("document_id")),
        "regulator": regulator,
        "document_type": _safe_str(row.get("document_type")),
        "subject": _safe_str(row.get("subject", "")),
        "display_title": _clean_subject(_safe_str(row.get("subject", ""))),
        "validity_status": _safe_str(row.get("validity_status")),
    }
    if regulator == "RBI":
        d["circular_number"] = _safe_str(row.get("circular_number", ""))
        d["issue_date"] = _safe_str(row.get("issue_date", ""))
    else:
        # SEBI document_id is the circular number
        d["circular_number"] = _safe_str(row.get("document_id", ""))
        d["issue_date"] = ""
    return d


# ---------------------------------------------------------------------------
# Public API — called by the FastAPI router
# ---------------------------------------------------------------------------

def get_catalog(
    regulator: str = "Both",
    doc_type: str = "",
    validity: str = "",
    search: str = "",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    Return paginated document catalog.

    Parameters
    ----------
    regulator : "RBI" | "SEBI" | "Both"
    doc_type  : filter by document_type (empty = all)
    validity  : filter by validity_status (empty = all)
    search    : substring search across subject + circular_number / document_id
    page      : 1-based page number
    page_size : results per page (max 100)
    """
    page_size = min(page_size, 100)
    frames: list[pd.DataFrame] = []

    if regulator in ("RBI", "Both"):
        frames.append(_rbi_catalog().copy().assign(_reg="RBI"))
    if regulator in ("SEBI", "Both"):
        frames.append(_sebi_catalog().copy().assign(_reg="SEBI"))

    if not frames:
        return {"total": 0, "page": page, "page_size": page_size, "documents": []}

    df = pd.concat(frames, ignore_index=True)

    # --- Filters ---
    if doc_type:
        df = df[df["document_type"].str.upper() == doc_type.upper()]

    if validity:
        df = df[df["validity_status"].str.lower() == validity.lower()]

    if search:
        q = search.lower()
        subject_col = df["subject"].fillna("").str.lower()
        doc_id_col = df["document_id"].fillna("").str.lower()
        circ_col = df.get("circular_number", pd.Series([""] * len(df))).fillna("").str.lower()
        mask = subject_col.str.contains(q, regex=False) | \
               doc_id_col.str.contains(q, regex=False) | \
               circ_col.str.contains(q, regex=False)
        df = df[mask]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    documents = []
    for _, row in page_df.iterrows():
        reg = _safe_str(row.get("_reg") or row.get("regulator", ""))
        documents.append(_doc_to_dict(row, reg))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),  # ceiling division
        "documents": documents,
    }


def get_document_detail(document_id: str) -> dict[str, Any]:
    """
    Return full metadata + all text chunks for a given document_id.
    Loads text from parquet only for the matching document.
    """
    # Try RBI first
    try:
        rbi = _load_rbi_full()
        rows = rbi[rbi["document_id"] == document_id]
        if not rows.empty:
            first = rows.iloc[0]
            chunks = []
            for _, r in rows.iterrows():
                chunks.append({
                    "chunk_id": _safe_str(r.get("chunk_id")),
                    "text": _safe_str(r.get("text", "")),
                })
            return {
                "document_id": document_id,
                "regulator": "RBI",
                "document_type": _safe_str(first.get("document_type")),
                "circular_number": _safe_str(first.get("circular_number", "")),
                "issue_date": _safe_str(first.get("issue_date", "")),
                "subject": _safe_str(first.get("subject", "")),
                "display_title": _clean_subject(_safe_str(first.get("subject", ""))),
                "validity_status": _safe_str(first.get("validity_status")),
                "chunk_count": len(chunks),
                "chunks": chunks,
                "source_url": "",
            }
    except CorpusError:
        pass

    # Try SEBI
    try:
        sebi = _load_sebi_full()
        rows = sebi[sebi["document_id"] == document_id]
        if not rows.empty:
            first = rows.iloc[0]
            chunks = []
            for _, r in rows.iterrows():
                chunks.append({
                    "chunk_id": _safe_str(r.get("chunk_id")),
                    "text": _safe_str(r.get("text", "")),
                })
            return {
                "document_id": document_id,
                "regulator": "SEBI",
                "document_type": _safe_str(first.get("document_type")),
                "circular_number": document_id,  # SEBI doc_id IS the circular number
                "issue_date": "",
                "subject": _safe_str(first.get("subject", "")),
                "display_title": _clean_subject(_safe_str(first.get("subject", ""))),
                "validity_status": _safe_str(first.get("validity_status")),
                "chunk_count": len(chunks),
                "chunks": chunks,
                "source_url": "",
            }
    except CorpusError:
        pass

    return {}


def get_filter_options() -> dict[str, Any]:
    """Return available filter values for the Explorer UI."""
    options: dict[str, Any] = {
        "rbi": {"document_types": [], "validity_statuses": []},
        "sebi": {"document_types": [], "validity_statuses": []},
    }
    try:
        rbi = _rbi_catalog()
        options["rbi"]["document_types"] = sorted(rbi["document_type"].dropna().unique().tolist())
        options["rbi"]["validity_statuses"] = sorted(rbi["validity_status"].dropna().unique().tolist())
        options["rbi"]["total_docs"] = len(rbi)
    except CorpusError:
        pass

    try:
        sebi = _sebi_catalog()
        options["sebi"]["document_types"] = sorted(sebi["document_type"].dropna().unique().tolist())
        options["sebi"]["validity_statuses"] = sorted(sebi["validity_status"].dropna().unique().tolist())
        options["sebi"]["total_docs"] = len(sebi)
    except CorpusError:
        pass

    return options

