"""LangGraph state definition for the Phase 4 Agentic RAG pipeline.

Single TypedDict so we can add nodes (Verification, Guardrails)
later without breaking existing ones.
"""

from typing import Any, Dict, List, TypedDict


class AgentState(TypedDict, total=False):
    # Input
    query: str

    # Query Analysis node output
    query_analysis: Dict[str, Any]
    # Expected shape:
    #   {
    #     "regulator": "SEBI" | "RBI" | "BOTH" | "UNKNOWN",
    #     "intent": str,
    #     "temporal_context": str,
    #     "optimized_search_query": str,
    #   }

    # Retrieval node output: list of chunk dicts as produced by
    # RegintelHybridRetriever.search()
    chunks: List[Dict[str, Any]]
    retrieval_iterations: int

    # Evidence sufficiency check output
    evidence_sufficiency_output: Dict[str, Any]
    # Expected shape: { "status": "SUPPORTED" | "RETRY" | "INSUFFICIENT_EVIDENCE" | "CLARIFY", "reason": str }

    # Reasoning node output: structured answer derived ONLY from chunks
    reasoning_output: Dict[str, Any]
    # Expected shape:
    #   {
    #     "answer": str,
    #     "regulatory_requirement": str,
    #     "applicability": str,
    #     "conditions": List[str],
    #     "exceptions": List[str],
    #     "evidence": List[str],
    #     "citations": List[Dict[str, Any]],
    #     "evidence_insufficient": bool,
    #   }

    # Guardrails node output + final response after validation
    guardrails_output: Dict[str, Any]
    # Expected shape:
    #   {
    #     "passed": bool,
    #     "checks": Dict[str, bool],
    #     "failures": List[str],
    #     "blocked": bool,
    #     "modified": bool,
    #   }
    final_output: Dict[str, Any]
    verification_output: Dict[str, Any]

    # Error surface for any node
    error: str
