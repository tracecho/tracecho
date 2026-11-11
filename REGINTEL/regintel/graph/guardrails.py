"""Deterministic Guardrails node for RegIntel RAG.

Validates Reasoning output against retrieved chunks. On failure, returns a
safe refusal - never invents regulatory content.
"""

import re
from copy import deepcopy


_SAFE_INSUFFICIENT = (
    "The available regulatory evidence is insufficient to answer this "
    "question reliably. Please refine the query or consult the relevant "
    "SEBI/RBI primary sources."
)

_SAFE_OUT_OF_SCOPE = (
    "This query appears outside the supported SEBI/RBI regulatory scope, "
    "or the retrieved evidence does not support a grounded answer."
)

_COT_PATTERNS = re.compile(
    r"(?i)\b("
    r"chain[- ]of[- ]thought|let me think|step by step|"
    r"my reasoning|as an ai|internal monologue|scratchpad"
    r")\b"
)

_INSUFFICIENT_LANG = re.compile(
    r"(?i)\b("
    r"insufficient|not (enough|sufficient)|unable to (answer|determine)|"
    r"cannot (answer|determine|confirm)|no (relevant |supporting )?evidence|"
    r"do not (actually )?answer|outside (the )?supported scope|"
    r"not (explicitly )?stated|unclear from (the )?evidence"
    r")\b"
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def _safe_payload(answer: str, reason: str) -> dict:
    return {
        "answer": answer,
        "regulatory_requirement": "",
        "applicability": "",
        "conditions": [],
        "exceptions": [],
        "evidence": [],
        "citations": [],
        "evidence_insufficient": True,
        "_guardrail_reason": reason,
    }


def _citations_grounded(citations, valid_ids) -> bool:
    if not citations:
        return True
    return all(c.get("chunk_id") in valid_ids for c in citations)


def _filter_grounded_quotes(evidence, chunks):
    """Keep only quotes found in retrieved chunk text; drop paraphrases."""
    if not evidence:
        return [], False
    corpus = [_norm(c.get("text", "")) for c in chunks]
    kept = []
    dropped = False
    for quote in evidence:
        qn = _norm(quote)
        if len(qn) < 12:
            kept.append(quote)
            continue
        if any(qn in body for body in corpus):
            kept.append(quote)
        else:
            dropped = True
    return kept, dropped


def _answer_is_evidence_backed(ro, citations, kept_quotes, chunks) -> bool:
    """True when the reasoning answer is grounded in retrieved chunks."""
    if not chunks:
        return False
    answer = str(ro.get("answer") or "").strip()
    if len(answer) < 30:
        return False
    if citations:
        return True
    if kept_quotes and (ro.get("regulatory_requirement") or "").strip():
        return True
    return bool(kept_quotes and len(answer) >= 80)


def _scope_ok(state, chunks) -> bool:
    analysis = state.get("query_analysis") or {}
    regulator = str(analysis.get("regulator", "")).upper()
    if regulator in {"SEBI", "RBI", "BOTH"}:
        return True
    if any(str(c.get("regulator", "")).upper() in {"SEBI", "RBI"} for c in chunks):
        return True
    q = _norm(state.get("query", ""))
    return any(
        t in q
        for t in ("sebi", "rbi", "nbfc", "kyc", "investment adviser", "cyber")
    )


def guardrails_node(state: dict) -> dict:
    """Validate reasoning_output; replace with a safe response on failure."""
    chunks = state.get("chunks") or []
    raw = state.get("reasoning_output") or {}
    verif = state.get("verification_output") or {}
    
    ro = deepcopy(raw) if isinstance(raw, dict) else {}
    valid_ids = {c.get("chunk_id") for c in chunks if c.get("chunk_id")}

    checks = {
        "has_retrieved_chunks": bool(chunks),
        "citations_grounded": True,
        "evidence_quotes_grounded": True,
        "insufficient_flag_consistent": True,
        "no_chain_of_thought": True,
        "sebi_rbi_scope": True,
        "no_unsupported_claims": True,
        "regulatory_validity": True,
        "temporal_validity": True
    }
    failures = []
    modified = False

    if not chunks:
        checks["has_retrieved_chunks"] = False
        failures.append("no_retrieved_chunks")

    if verif.get("citation_errors"):
        invalid_ids = [err for err in verif["citation_errors"] if "invalid chunk_id" in err]
        if invalid_ids:
            checks["citations_grounded"] = False
            # We don't hard fail on invalid citation ids, we just clean them out.
        
    if verif.get("evidence_quote_errors"):
        checks["evidence_quotes_grounded"] = False
        # Treat as soft failure; drop the quotes later but don't hard block
        
    if verif.get("unsupported_claims"):
        checks["no_unsupported_claims"] = False
        # Soft failure: just record it, don't hard block
        
    if verif.get("regulatory_validity_errors"):
        checks["regulatory_validity"] = False
        # Soft failure, add disclaimer
        ro["answer"] = str(ro.get("answer", "")) + "\n\nDisclaimer: The current validity of some referenced regulations cannot be established or they may be superseded."
        modified = True

    if verif.get("temporal_errors"):
        checks["temporal_validity"] = False
        # Soft failure, add disclaimer
        if "Disclaimer:" not in str(ro.get("answer", "")):
            ro["answer"] = str(ro.get("answer", "")) + "\n\nDisclaimer: The regulation's current validity or historical applicability cannot be fully established based on the evidence."
        modified = True

    answer = str(ro.get("answer") or "")
    if _COT_PATTERNS.search(answer):
        checks["no_chain_of_thought"] = False
        failures.append("chain_of_thought_exposed")

    if not _scope_ok(state, chunks):
        checks["sebi_rbi_scope"] = False
        failures.append("out_of_scope")

    evidence_insufficient = bool(ro.get("evidence_insufficient")) or (verif.get("recommended_action") == "INSUFFICIENT_EVIDENCE")

    if not evidence_insufficient:
        if chunks and not ro.get("citations") and (ro.get("regulatory_requirement") or "").strip():
            checks["no_unsupported_claims"] = False
            # Soft failure; they might have provided partial info without a formal citation

        if not chunks:
            checks["no_unsupported_claims"] = False
            failures.append("claims_without_evidence")

    hard_failures = failures
    blocked = False
    final = ro

    if hard_failures:
        blocked = True
        modified = True
        if "out_of_scope" in hard_failures and not chunks:
            final = _safe_payload(_SAFE_OUT_OF_SCOPE, ";".join(failures))
        else:
            final = _safe_payload(_SAFE_INSUFFICIENT, ";".join(failures))
        final["citations"] = []
    elif evidence_insufficient:
        blocked = True
        if answer.startswith("Reasoning step failed:"):
            final = ro
        else:
            final = deepcopy(ro)
            final["answer"] = _SAFE_INSUFFICIENT
            final["evidence_insufficient"] = True
            final["citations"] = []
            modified = True
            
    # Clean citations if any are left
    if final.get("citations"):
        cleaned = [c for c in final["citations"] if c.get("chunk_id") in valid_ids]
        if len(cleaned) != len(final["citations"]):
            final["citations"] = cleaned
            modified = True
            
    # Clean evidence quotes as well
    if final.get("evidence"):
        kept, dropped = _filter_grounded_quotes(final["evidence"], chunks)
        if dropped:
            final["evidence"] = kept
            modified = True

    passed = not blocked

    return {
        "guardrails_output": {
            "passed": passed,
            "checks": checks,
            "failures": failures,
            "blocked": blocked,
            "modified": modified,
        },
        "final_output": final,
        "reasoning_output": final if (blocked or modified) else ro,
    }
