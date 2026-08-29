import os
import re
import sys

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from graph.workflow import run as run_workflow

app = FastAPI(title="RegIntel API", description="Agentic Regulatory Intelligence Platform API")


class QueryRequest(BaseModel):
    query: str


class Citation(BaseModel):
    chunk_id: str = ""
    regulator: str = ""
    document_title: str = ""
    section: str = ""
    issue_date: str = ""
    source_url: str = ""


class QueryAnalysis(BaseModel):
    regulator: str = "UNKNOWN"
    intent: str = ""
    temporal_context: str = ""
    optimized_search_query: str = ""


class RetrievedChunk(BaseModel):
    chunk_id: str = ""
    regulator: str = ""
    document_title: str = ""
    document_type: str = ""
    section: str = ""
    issue_date: str = ""
    validity_status: str = ""
    source_url: str = ""
    text: str = ""
    hybrid_score: float | None = None


class GuardrailsSummary(BaseModel):
    passed: bool = False
    blocked: bool = False
    modified: bool = False
    failures: list[str] = Field(default_factory=list)
    checks: dict[str, bool] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    query_analysis: QueryAnalysis | None = None
    answer: str
    regulatory_requirement: str = ""
    applicability: str = ""
    conditions: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    evidence_insufficient: bool = False
    verification_status: str
    guardrails: GuardrailsSummary | None = None
    regulator: str = "UNKNOWN"
    error: str | None = None


_EMPTY_META = {"", "unknown", "nan", "none", "null", "n/a"}


def _clean_meta_value(value) -> str:
    text = str(value or "").strip()
    if text.lower() in _EMPTY_META:
        return ""
    return text


def _clean_document_title(title) -> str:
    text = _clean_meta_value(title)
    if not text:
        return ""
    text = re.sub(r"\s+section\s*=.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+validity\s*=.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+issue_date\s*=.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+source_url\s*=.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+chunk_id\s*=.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+regulator\s*=.*$", "", text, flags=re.IGNORECASE)
    
    # Sometimes it returns arbitrary malformed AI properties appended to title
    text = re.sub(r"(?i)\b(validity|section|issue_date|source_url|chunk_id|regulator)\b.*$", "", text)
    
    return text.strip(" \t\n\r|,-=").strip()


def _enrich_citation(citation: dict, chunk_by_id: dict[str, dict]) -> Citation:
    chunk = chunk_by_id.get(str(citation.get("chunk_id", "")), {})
    chunk_id = _clean_meta_value(citation.get("chunk_id") or chunk.get("chunk_id"))
    title = _clean_document_title(chunk.get("document_title") or citation.get("document_title"))
    if not title and chunk.get("document_id"):
        title = _clean_document_title(chunk.get("document_id"))
    return Citation(
        chunk_id=chunk_id,
        regulator=_clean_meta_value(chunk.get("regulator") or citation.get("regulator")),
        document_title=title,
        section=_clean_meta_value(chunk.get("section") or citation.get("section")),
        issue_date=_clean_meta_value(chunk.get("issue_date") or citation.get("issue_date")),
        source_url=_clean_meta_value(chunk.get("source_url") or citation.get("source_url")),
    )


def _verification_status(result: dict, final_output: dict) -> str:
    guardrails = result.get("guardrails_output") or {}
    answer = str(final_output.get("answer") or "")
    if answer.startswith("Reasoning step failed:"):
        return "error"
    if guardrails.get("blocked"):
        return "blocked"
    if final_output.get("evidence_insufficient"):
        return "insufficient_evidence"
    if result.get("error"):
        return "error"
    if guardrails.get("passed"):
        return "verified"
    return "unknown"


def _build_query_response(result: dict) -> QueryResponse:
    analysis_raw = result.get("query_analysis") or {}
    final_output = result.get("final_output") or result.get("reasoning_output") or {}
    guardrails_raw = result.get("guardrails_output") or {}
    chunks = result.get("chunks") or []

    query_analysis = QueryAnalysis(
        regulator=str(analysis_raw.get("regulator", "UNKNOWN")),
        intent=str(analysis_raw.get("intent", "")),
        temporal_context=str(analysis_raw.get("temporal_context", "")),
        optimized_search_query=str(analysis_raw.get("optimized_search_query", "")),
    )

    chunk_by_id = {str(c.get("chunk_id", "")): c for c in chunks if c.get("chunk_id")}
    citations = [
        _enrich_citation(c, chunk_by_id)
        for c in (final_output.get("citations") or [])
    ]

    retrieved_chunks = [
        RetrievedChunk(
            chunk_id=_clean_meta_value(c.get("chunk_id")),
            regulator=_clean_meta_value(c.get("regulator")),
            document_title=_clean_document_title(c.get("document_title")),
            document_type=_clean_meta_value(c.get("document_type")),
            section=_clean_meta_value(c.get("section")),
            issue_date=_clean_meta_value(c.get("issue_date")),
            validity_status=_clean_meta_value(c.get("validity_status")),
            source_url=_clean_meta_value(c.get("source_url")),
            text=str(c.get("text", "")),
            hybrid_score=c.get("hybrid_score"),
        )
        for c in chunks
    ]

    guardrails = GuardrailsSummary(
        passed=bool(guardrails_raw.get("passed")),
        blocked=bool(guardrails_raw.get("blocked")),
        modified=bool(guardrails_raw.get("modified")),
        failures=list(guardrails_raw.get("failures") or []),
        checks=dict(guardrails_raw.get("checks") or {}),
    )

    return QueryResponse(
        query_analysis=query_analysis,
        answer=str(final_output.get("answer") or ""),
        regulatory_requirement=str(final_output.get("regulatory_requirement") or ""),
        applicability=str(final_output.get("applicability") or ""),
        conditions=list(final_output.get("conditions") or []),
        exceptions=list(final_output.get("exceptions") or []),
        evidence=list(final_output.get("evidence") or []),
        citations=citations,
        retrieved_chunks=retrieved_chunks,
        evidence_insufficient=bool(final_output.get("evidence_insufficient")),
        verification_status=_verification_status(result, final_output),
        guardrails=guardrails,
        regulator=query_analysis.regulator,
        error=result.get("error"),
    )


@app.post("/api/ask", response_model=QueryResponse)
async def ask_assistant(request: QueryRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    try:
        result = run_workflow(query)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Backend pipeline unavailable: {exc}",
        ) from exc

    response = _build_query_response(result)
    if not response.answer and response.error:
        raise HTTPException(status_code=503, detail=response.error)

    return response


@app.get("/api/dashboard")
async def get_dashboard_data():
    import json, os, requests
    
    # Find .env by traversing upwards from _PKG_ROOT
    alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not alpha_vantage_key:
        current_dir = _PKG_ROOT
        while current_dir and current_dir != os.path.dirname(current_dir):
            env_path = os.path.join(current_dir, ".env")
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("ALPHA_VANTAGE_API_KEY="):
                            alpha_vantage_key = line.split("=", 1)[1].strip(' "\'')
                if alpha_vantage_key:
                    break
            current_dir = os.path.dirname(current_dir)
    
    market_overview = {}
    market_error = None
    if alpha_vantage_key:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey={alpha_vantage_key}"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if "Global Quote" in data and data["Global Quote"]:
                    q = data["Global Quote"]
                    market_overview["IBM Price"] = f"${float(q.get('05. price', 0)):.2f}"
                    market_overview["IBM Change"] = q.get("10. change percent", "0%")
                else:
                    market_error = "API error: Check rate limit or format"
        except Exception as e:
            market_error = str(e)
    else:
        market_error = "Alpha Vantage API key not found in .env"
        
    doc_stats = {"total": 0, "total_chunks": 0, "rbi_count": 0, "sebi_count": 0}
    recent_documents = []
    categories = {}
    
    meta_path = os.path.join(_PKG_ROOT, "data", "processed", "faiss_meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                faiss_meta = json.load(f)
                doc_stats["total_chunks"] = len(faiss_meta)
                
                unique_docs = {}
                for m in faiss_meta:
                    doc_id = m.get("document_id") or m.get("chunk_id")
                    if doc_id and doc_id not in unique_docs:
                        unique_docs[doc_id] = m

                doc_stats["total"] = len(unique_docs)
                
                for m in unique_docs.values():
                    reg = m.get("regulator", "").upper()
                    if reg == "RBI":
                        doc_stats["rbi_count"] += 1
                    elif reg == "SEBI":
                        doc_stats["sebi_count"] += 1
                    
                    cat = m.get("document_type", "Other")
                    if cat:
                        categories[cat] = categories.get(cat, 0) + 1

                docs_list = list(unique_docs.values())
                docs_list.sort(key=lambda x: str(x.get("issue_date", "")), reverse=True)
                
                recent_documents = [
                    {
                        "regulator": d.get("regulator", "Unknown"),
                        "document_title": _clean_document_title(d.get("document_title")),
                        "issue_date": d.get("issue_date", "N/A"),
                    }
                    for d in docs_list[:5]
                ]
                
                sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                categories = dict(sorted_cats[:5])
                
        except Exception:
            pass

    return {
        "market_overview": market_overview,
        "market_error": market_error if market_error and not market_overview else None,
        "document_stats": doc_stats,
        "recent_documents": recent_documents,
        "categories": categories,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
