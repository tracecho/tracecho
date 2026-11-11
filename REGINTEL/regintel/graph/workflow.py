"""LangGraph workflow for Phase 4 Agentic RAG.

START -> query_analysis -> retrieval -> reasoning -> guardrails -> END

Verification Agent is intentionally NOT wired.
"""

import sys
import os

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from langgraph.graph import StateGraph, START, END

from graph.state import AgentState
from graph.nodes import query_analysis_node, retrieval_node, reasoning_node, evidence_sufficiency_node
from graph.guardrails import guardrails_node
from graph.verification_agent import verification_node

def route_evidence_sufficiency(state: dict) -> str:
    status = state.get("evidence_sufficiency_output", {}).get("status", "SUPPORTED")
    if status == "RETRY":
        return "retrieval"
    return "reasoning"


def build_workflow():
    """Construct (but do not compile) the StateGraph. Kept separate
    from `compile_workflow` so tests can introspect the graph."""
    g = StateGraph(AgentState)

    g.add_node("query_analysis", query_analysis_node)
    g.add_node("retrieval", retrieval_node)
    g.add_node("evidence_sufficiency", evidence_sufficiency_node)
    g.add_node("reasoning", reasoning_node)
    g.add_node("verification", verification_node)
    g.add_node("guardrails", guardrails_node)

    g.add_edge(START, "query_analysis")
    g.add_edge("query_analysis", "retrieval")
    g.add_edge("retrieval", "evidence_sufficiency")
    g.add_conditional_edges("evidence_sufficiency", route_evidence_sufficiency, {"retrieval": "retrieval", "reasoning": "reasoning"})
    g.add_edge("reasoning", "guardrails")
    g.add_edge("guardrails", END)

    return g


def compile_workflow():
    """Compiled, runnable LangGraph app."""
    return build_workflow().compile()


# Module-level singleton so callers can do:
#   from graph.workflow import app
#   app.invoke({"query": "..."})
app = compile_workflow()


def run(query: str) -> dict:
    """Convenience runner. Returns the final state dict."""
    return app.invoke({"query": query})


if __name__ == "__main__":
    import json as _json

    questions = [
        "What are the KYC requirements for NBFCs?",
        "What is customer due diligence under RBI KYC rules?",
        "What is V-CIP?",
        "What are the four key elements of a bank's KYC policy?",
        "What is the capital of France?",
    ]

    for q in questions:
        print("\n" + "=" * 80)
        print(f"QUERY: {q}")
        print("=" * 80)

        result = run(q)
        
        print("\n--- QUERY ANALYSIS ---")
        print(_json.dumps(result.get("query_analysis", {}), indent=2))
        
        print("\n--- RETRIEVAL SUMMARY ---")
        chunks = result.get("chunks", [])
        print(f"Retrieved {len(chunks)} chunks")
        
        print("\n--- EVIDENCE SUFFICIENCY ---")
        print(_json.dumps(result.get("evidence_sufficiency_output", {}), indent=2))
        
        print("\n--- REASONING OUTPUT ---")
        ro = result.get("reasoning_output", {})
        # Omit chunks/citations for brevity if huge, or just print keys
        print(_json.dumps({k: v for k, v in ro.items() if k != "citations"}, indent=2))
        
        print("\n--- VERIFICATION OUTPUT ---")
        print(_json.dumps(result.get("verification_output", {}), indent=2))

        go = result.get("guardrails_output") or {}
        print("\n--- GUARDRAILS OUTPUT ---")
        print(_json.dumps({
            "passed": go.get("passed"),
            "blocked": go.get("blocked"),
            "modified": go.get("modified"),
            "failures": go.get("failures", []),
            "checks": go.get("checks", {}),
        }, indent=2))

        fo = result.get("final_output") or result.get("reasoning_output") or {}
        print("\n--- FINAL OUTPUT ---")
        print(fo.get("answer", ""))

        print("\n--- Citations ---")
        for cit in fo.get("citations", []) or []:
            print(
                f"  [{cit.get('chunk_id')}] {cit.get('regulator')} | "
                f"{cit.get('document_title')}"
            )

        if result.get("error"):
            print(f"\n[error] {result['error']}")
