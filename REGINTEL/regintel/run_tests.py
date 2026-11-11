import sys
import os
import json

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from graph.workflow import run

tests = [
    "What are the KYC requirements applicable to NBFCs?",
    "What SEBI regulations apply to listed entities?",
    "What were the KYC requirements in 2022?",
    "What SEBI regulations apply to coffee shops on Mars?",
    "What RBI regulation governs cryptocurrency mining?",
    "What is customer due diligence?",
    "What are the reporting requirements for Investment Advisers?"
]

for test in tests:
    print("-" * 40)
    print("QUERY")
    print("-" * 40)
    print(f"\nQuery:\n{test}\n")
    
    res = run(test)
    qa = res.get("query_analysis", {})
    print(f"Detected regulator: {qa.get('regulator')}")
    print(f"Intent: {qa.get('intent')}\n")
    
    print("-" * 40)
    print("TOP RETRIEVED EVIDENCE")
    print("-" * 40)
    
    chunks = res.get("chunks", [])
    for idx, c in enumerate(chunks, 1):
        print(f"\n{idx}.")
        print(f"Chunk: {c.get('chunk_id')}")
        print(f"Document: {c.get('document_title')}")
        print(f"Section: {c.get('section')}")
        print(f"Dense: {c.get('raw_dense_score'):.2f}")
        print(f"BM25: {c.get('raw_bm25_score'):.2f}")
        print(f"Hybrid: {c.get('hybrid_score'):.2f}")
        print(f"Reranker: {c.get('reranker_score', 0):.2f}")
        print(f"Final: {c.get('final_score', c.get('hybrid_score')):.2f}")

    print("\n" + "-" * 40)
    print("EVIDENCE SUFFICIENCY")
    print("-" * 40)
    ev = res.get("evidence_sufficiency_output", {})
    status = ev.get("status", "UNKNOWN")
    print(f"\n{status} - {ev.get('reason', '')}\n")
    
    print("-" * 40)
    print("ANSWER")
    print("-" * 40)
    
    if status == "INSUFFICIENT_EVIDENCE":
        print("\nINSUFFICIENT_EVIDENCE. The reasoning LLM was bypassed.\n")
    else:
        reasoning = res.get("reasoning_output", {})
        print(f"\n{reasoning.get('answer', '')}\n")
