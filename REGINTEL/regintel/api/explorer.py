"""
explorer.py — FastAPI router for the Document Explorer module.

Endpoints
---------
GET /api/explorer/filters                      — Available filter options
GET /api/explorer/catalog                      — Paginated document list
GET /api/explorer/document/{document_id:path}  — Full metadata + text chunks

Does not touch the RAG pipeline or any existing endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from services.corpus import CorpusError, get_catalog, get_document_detail, get_filter_options

router = APIRouter(prefix="/api/explorer", tags=["explorer"])


@router.get("/filters")
async def explorer_filters():
    """Return available document types and validity statuses per regulator."""
    try:
        return get_filter_options()
    except CorpusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")


@router.get("/catalog")
async def explorer_catalog(
    regulator: str = Query(default="Both", pattern="^(RBI|SEBI|Both)$"),
    doc_type: str = Query(default=""),
    validity: str = Query(default=""),
    search: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """
    Paginated document catalog.

    - **regulator**: RBI | SEBI | Both
    - **doc_type**: filter by document_type (empty = all)
    - **validity**: filter by validity_status (empty = all)
    - **search**: keyword search across subject and circular number
    - **page** / **page_size**: pagination
    """
    try:
        return get_catalog(
            regulator=regulator,
            doc_type=doc_type,
            validity=validity,
            search=search,
            page=page,
            page_size=page_size,
        )
    except CorpusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")


@router.get("/document/{document_id:path}")
async def explorer_document(document_id: str):
    """
    Full document detail: metadata + all text chunks.

    Use the `document_id` returned by /catalog.
    SEBI document_ids contain slashes (e.g. SEBI/HO/CFD/…) — the
    `{document_id:path}` route captures them correctly.
    """
    if not document_id or len(document_id) > 300:
        raise HTTPException(status_code=400, detail="Invalid document_id.")
    try:
        detail = get_document_detail(document_id)
    except CorpusError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

    if not detail:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id!r}")

    return detail

