import json
import os
import sys

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from retrieval.embeddings import RegintelEmbeddings
from retrieval.vector_store import RegintelVectorStore
from retrieval.bm25 import RegintelBM25Store
from retrieval.metadata_store import MetadataStore

def validate():
    bench_file = os.path.join(os.path.dirname(__file__), "benchmark.json")
    if not os.path.exists(bench_file):
        print("FAIL: benchmark.json not found")
        sys.exit(1)
        
    try:
        with open(bench_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"FAIL: could not load benchmark.json: {e}")
        sys.exit(1)
        
    print(f"Validating benchmark: {len(data)} questions found.")
    
    if len(data) != 50:
        print(f"FAIL: expected exactly 50 questions, found {len(data)}")
        sys.exit(1)
        
    ids = set()
    ood_count = 0
    ans_count = 0
    
    ms = MetadataStore()
    if not ms.load():
        ms.build_store()
    
    for item in data:
        qid = item["id"]
        if qid in ids:
            print(f"FAIL: duplicate question id {qid}")
            sys.exit(1)
        ids.add(qid)
        
        if not item.get("answerable", True):
            ood_count += 1
            if len(item.get("expected_chunk_ids", [])) > 0:
                print(f"FAIL: out of domain question {qid} should not have expected chunks")
                sys.exit(1)
        else:
            ans_count += 1
            chunks = item.get("expected_chunk_ids", [])
            for c in chunks:
                if not ms.get(c):
                    print(f"FAIL: chunk {c} for question {qid} does not exist in corpus")
                    sys.exit(1)
                    
    if ood_count != 5:
        print(f"FAIL: expected exactly 5 out-of-domain questions, found {ood_count}")
        sys.exit(1)
        
    if ans_count != 45:
        print(f"FAIL: expected exactly 45 answerable questions, found {ans_count}")
        sys.exit(1)
        
    print("PASS: benchmark validation passed.")
    sys.exit(0)

if __name__ == "__main__":
    validate()
