import sys
import os

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "REGINTEL", "regintel"))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from graph.workflow import app
import json

def test():
    query = "What are the KYC requirements for NBFCs?"
    print(f"QUERY: {query}\n")
    
    result = app.invoke({"query": query})
    
    chunks = result.get("chunks", [])
    if chunks:
        top_chunk = chunks[0]
        # Nodes.py prints the overlap, we can't easily fetch it from final state but let's approximate or just grab the fields we can
        print("top chunk:", top_chunk.get("chunk_id", "Unknown"))
        print("final_score:", top_chunk.get("final_score", top_chunk.get("hybrid_score", "Unknown")))
        print("reranker_score:", top_chunk.get("reranker_score", "Unknown"))
    else:
        print("top chunk: None")
        
    print("evidence_sufficiency_output:")
    print(json.dumps(result.get("evidence_sufficiency_output", {}), indent=2))
    
    print("reasoning_output:")
    ro = {k: v for k, v in result.get("reasoning_output", {}).items() if k != "citations"}
    print(json.dumps(ro, indent=2))
    
    print("final_answer:")
    fo = result.get("final_output") or result.get("reasoning_output") or {}
    print(fo.get("answer", ""))

if __name__ == "__main__":
    test()
