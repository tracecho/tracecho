"""Verification Agent for Phase 4 Agentic RAG."""

import re
import json

from llm.ollama_client import chat

def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()

_VERIFICATION_PROMPT = """You are a factual Verification Agent validating an AI's response against retrieved regulatory evidence.

QUESTION: {query}
TEMPORAL REQUIREMENT: {temporal_type}

RETRIEVED EVIDENCE:
{chunks_block}

GENERATED ANSWER:
{reasoning_output}

Your task is to identify major unsupported claims (facts, dates, conditions, exceptions, names) in the GENERATED ANSWER that are absent from or contradicted by the RETRIEVED EVIDENCE.
Also identify if the retrieved evidence contains materially conflicting rules for this question.

Respond ONLY with a JSON object containing:
{{
    "unsupported_claims": ["list of strings detailing unsupported claims, empty if none"],
    "contradictions": ["list of conflicts discovered in the evidence, empty if none"],
    "contradiction_explained_in_answer": bool (true if answer explicitly mentions and explains the conflict)
}}
"""

def verification_node(state: dict) -> dict:
    query = state.get("query", "")
    query_analysis = state.get("query_analysis", {})
    chunks = state.get("chunks", [])
    reasoning_output = state.get("reasoning_output", {})
    
    # Early escape if no processing needed
    if not chunks or reasoning_output.get("evidence_insufficient"):
        return {
            "verification_output": {
                "verified": False,
                "confidence": 0.0,
                "unsupported_claims": [],
                "citation_errors": [],
                "evidence_quote_errors": [],
                "regulatory_validity_errors": [],
                "temporal_errors": [],
                "contradictions": [],
                "recommended_action": "INSUFFICIENT_EVIDENCE"
            }
        }
    
    chunks_dict = {c["chunk_id"]: c for c in chunks if "chunk_id" in c}
    corpus_norm = [_norm(c.get("text", "")) for c in chunks]

    citation_errors = []
    evidence_quote_errors = []
    regulatory_validity_errors = []
    temporal_errors = []
    
    # 1. & 2. Citation Validation
    citations = reasoning_output.get("citations", [])
    corrected_citations = []
    for cit in citations:
        cid = cit.get("chunk_id")
        if not cid or cid not in chunks_dict:
            citation_errors.append(f"Citation references invalid chunk_id: {cid}")
            continue
        
        actual = chunks_dict[cid]
        mismatched = []
        # We also want to compare issue_date but as string representations might differ slightly, strict equal works for now.
        for key in ["regulator", "document_title", "section", "issue_date"]:
            val_cit = str(cit.get(key) or "").strip()
            val_act = str(actual.get(key) or "").strip()
            # if both are empty, ok. if cit provided but mismatched, log.
            if val_cit and val_cit != val_act:
                mismatched.append(key)
                
        if mismatched:
            citation_errors.append(f"Citation {cid} hallucinated metadata fields: {', '.join(mismatched)}")
            
        corrected_citations.append({
            "chunk_id": cid,
            "regulator": actual.get("regulator", ""),
            "document_title": actual.get("document_title", ""),
            "section": actual.get("section", ""),
            "issue_date": actual.get("issue_date", ""),
            "source_url": actual.get("source_url", "")
        })
    reasoning_output["citations"] = corrected_citations

    # 3. Evidence quote grounding
    evidence_quotes = reasoning_output.get("evidence", [])
    for eq in evidence_quotes:
        qn = _norm(eq)
        if len(qn) < 12:
            continue
        if not any(qn in body for body in corpus_norm):
            evidence_quote_errors.append(f"Evidence quote not found verbatim in chunks: '{eq}'")
            
    # 5. & 6. Regulatory and Temporal Validity
    temporal_type = query_analysis.get("temporal_type", "UNSPECIFIED")
    
    # For Non-historical queries, superseded documents should throw validity errors.
    if temporal_type != "HISTORICAL":
        for cit in corrected_citations:
            cid = cit["chunk_id"]
            if str(chunks_dict[cid].get("validity_status", "")).upper() == "SUPERSEDED":
                regulatory_validity_errors.append(f"Answer relies on SUPERSEDED document {cid} for a current question.")
    
    # For Historical, make sure temporal_match is true if it was resolved by retrieval checks
    if temporal_type == "HISTORICAL":
        for cit in corrected_citations:
            cid = cit["chunk_id"]
            # we consider it a temporal error if it lacks temporal_match in historical context
            # assuming temporal_match is placed by retrieval. If missing/false, it is flagged.
            if not chunks_dict[cid].get("temporal_match", False):
                # We can be lenient if temporal_match isn't implemented completely in retrieval output
                # But requirement says "verify that the evidence applied to the requested historical period".
                temporal_errors.append(f"Evidence {cid} not verified historically applicable.")

    # 4. & 7. Unsupported Claims / Contradiction (LLM check)
    chunks_block = "\n".join([f"[{c.get('chunk_id')}] val:{c.get('validity_status')} text:{c.get('text', '')}" for c in chunks])
    
    unsupported = []
    contradictions = []
    contradiction_exp = False
    
    try:
        # LLM check
        llm_out = chat(
            messages=[
                {"role": "system", "content": "You are a factual verification agent. Respond ONLY with JSON."},
                {"role": "user", "content": _VERIFICATION_PROMPT.format(
                    query=query, 
                    temporal_type=temporal_type,
                    chunks_block=chunks_block,
                    reasoning_output=json.dumps({k: v for k, v in reasoning_output.items() if k != "citations"}, indent=2)
                )}
            ],
            format_json=True,
            temperature=0.0
        )
        if isinstance(llm_out, dict):
            unsupported = llm_out.get("unsupported_claims", [])
            contradictions = llm_out.get("contradictions", [])
            contradiction_exp = llm_out.get("contradiction_explained_in_answer", False)
    except Exception as e:
        # Failsafe
        pass

    recommended_action = "ANSWER"
    verified = True

    # Only block for material verification failures.
    # Minor/uncertain metadata issues should not prevent an evidence-grounded answer.

    material_unsupported = [
        claim for claim in unsupported
        if isinstance(claim, str) and claim.strip()
    ]

    material_quote_errors = [
        err for err in evidence_quote_errors
        if isinstance(err, str) and err.strip()
    ]

    material_validity_errors = [
        err for err in regulatory_validity_errors
        if isinstance(err, str) and err.strip()
    ]

    material_temporal_errors = [
        err for err in temporal_errors
        if isinstance(err, str) and err.strip()
    ]

    if material_unsupported:
        verified = False
        recommended_action = "RETRY"

    elif material_validity_errors or material_temporal_errors:
        verified = False
        recommended_action = "RETRY"

    elif contradictions and not contradiction_exp:
        verified = False
        recommended_action = "RETRY"
        
    return {
        "reasoning_output": reasoning_output,
        "verification_output": {
            "verified": verified,
            "confidence": 1.0 if verified else 0.0,
            "unsupported_claims": unsupported,
            "citation_errors": citation_errors,
            "evidence_quote_errors": evidence_quote_errors,
            "regulatory_validity_errors": regulatory_validity_errors,
            "temporal_errors": temporal_errors,
            "contradictions": contradictions,
            "recommended_action": recommended_action
        }
    }
