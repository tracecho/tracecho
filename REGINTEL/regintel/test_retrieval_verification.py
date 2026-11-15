import os
import sys

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from retrieval.metadata_store import MetadataStore
from retrieval.vector_store import RegintelVectorStore
from retrieval.bm25 import RegintelBM25Store
from graph.nodes import _get_retriever, retrieval_node

def run_tests():
    print("=== TEST 1: Metadata Store ===")
    ms = MetadataStore()
    assert ms.load() is True, "MetadataStore failed to load!"
    print(f"Metadata chunks count: {len(ms.metadata)}")
    assert len(ms.metadata) == 10819, f"Expected 10819, got {len(ms.metadata)}"
    print("Test 1 PASSED: Metadata loaded 10,819 chunks.")

    print("\n=== TEST 2: FAISS Vector Store ===")
    vs = RegintelVectorStore()
    assert vs.load() is True, "FAISS VectorStore failed to load!"
    print(f"FAISS vectors count: {vs.index.ntotal}")
    assert vs.index.ntotal == 10819, f"Expected 10819, got {vs.index.ntotal}"
    print("Test 2 PASSED: FAISS loaded 10,819 vectors.")

    print("\n=== TEST 3: BM25 Store ===")
    bs = RegintelBM25Store()
    assert bs.load() is True, "BM25Store failed to load!"
    bm25_res = bs.search("Customer Due Diligence banks", k=5)
    print(f"BM25 returned candidates: {len(bm25_res)}")
    assert len(bm25_res) > 0, "BM25 should return candidates"
    print(f"Top BM25 candidate: {bm25_res[0]}")
    print("Test 3 PASSED: BM25 returns relevant candidates.")

    print("\n=== TEST 4: RBI Customer Due Diligence (CDD) Query ===")
    rbi_query = "What is customer due diligence under RBI KYC rules?"
    retriever = _get_retriever()
    rbi_state = {
        "query": rbi_query,
        "query_analysis": {
            "regulator": "RBI",
            "optimized_search_query": "customer due diligence CDD RBI KYC rules requirements",
            "temporal_type": "UNSPECIFIED"
        }
    }
    rbi_res = retrieval_node(rbi_state)
    rbi_chunks = rbi_res.get("chunks", [])
    print(f"RBI CDD chunks retrieved count: {len(rbi_chunks)}")
    assert len(rbi_chunks) > 0, "RBI CDD query should retrieve relevant chunks"
    for idx, chunk in enumerate(rbi_chunks[:3]):
        cid = chunk.get("chunk_id")
        title = chunk.get("document_title", "")
        ds = chunk.get("dense_score", 0.0)
        ss = chunk.get("bm25_score", 0.0)
        hs = chunk.get("hybrid_score", 0.0)
        print(f"  [{idx+1}] ID: {cid}, Title: {title} | Dense: {ds:.3f} | BM25: {ss:.3f} | Hybrid: {hs:.3f}")
        print(f"      Text excerpt: {chunk.get('text', '')[:120]}...")
    print("Test 4 PASSED: RBI CDD query retrieves relevant documents.")

    print("\n=== TEST 5: SEBI Investment Adviser Query ===")
    sebi_query = "What are the rules and requirements for Investment Advisers under SEBI regulations?"
    sebi_state = {
        "query": sebi_query,
        "query_analysis": {
            "regulator": "SEBI",
            "optimized_search_query": "Investment Advisers rules qualification capital SEBI regulations",
            "temporal_type": "UNSPECIFIED"
        }
    }
    sebi_res = retrieval_node(sebi_state)
    sebi_chunks = sebi_res.get("chunks", [])
    print(f"SEBI Investment Adviser chunks retrieved count: {len(sebi_chunks)}")
    assert len(sebi_chunks) > 0, "SEBI Investment Adviser query should retrieve relevant chunks"
    for idx, chunk in enumerate(sebi_chunks[:3]):
        cid = chunk.get("chunk_id")
        title = chunk.get("document_title", "")
        ds = chunk.get("dense_score", 0.0)
        ss = chunk.get("bm25_score", 0.0)
        hs = chunk.get("hybrid_score", 0.0)
        print(f"  [{idx+1}] ID: {cid}, Title: {title} | Dense: {ds:.3f} | BM25: {ss:.3f} | Hybrid: {hs:.3f}")
        print(f"      Text excerpt: {chunk.get('text', '')[:120]}...")
    print("Test 5 PASSED: SEBI Investment Adviser query retrieves relevant documents.")

    print("\n=== TEST 6: Resilience Test (FAISS index=None fallback to BM25) ===")
    original_index = retriever.vector_store.index
    try:
        retriever.vector_store.index = None
        resilient_chunks = retriever.search("KYC requirements NBFC", alpha=0.6, k=5)
        print(f"Resilient retrieval without FAISS returned {len(resilient_chunks)} chunks.")
        assert len(resilient_chunks) > 0, "BM25 fallback must return chunks when FAISS is unavailable!"
        print(f"Top resilient chunk: {resilient_chunks[0]['chunk_id']} (score: {resilient_chunks[0]['hybrid_score']:.3f})")
        print("Test 6 PASSED: Hybrid retriever cleanly falls back to BM25 when FAISS is unavailable.")
    finally:
        retriever.vector_store.index = original_index

    print("\nALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()

