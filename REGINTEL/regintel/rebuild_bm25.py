import sys
import os
import pandas as pd

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from retrieval.bm25 import RegintelBM25Store

def rebuild():
    sebi_path = os.path.join(_PKG_ROOT, "data", "processed", "sebi_chunks.parquet")
    rbi_path = os.path.join(_PKG_ROOT, "data", "processed", "rbi_chunks.parquet")
    
    print("Loading data...")
    sebi_df = pd.read_parquet(sebi_path)
    rbi_df = pd.read_parquet(rbi_path)
    df = pd.concat([sebi_df, rbi_df], ignore_index=True)
    
    # Must have 'text' and 'chunk_id'
    texts = df['text'].astype(str).tolist()
    chunk_ids = df['chunk_id'].astype(str).tolist()
    
    print(f"Rebuilding BM25 for {len(texts)} chunks using strictly compliant tokenizer...")
    store = RegintelBM25Store(
        index_path=os.path.join(_PKG_ROOT, "data", "processed", "bm25_index.pkl"),
        meta_path=os.path.join(_PKG_ROOT, "data", "processed", "bm25_meta.json")
    )
    store.build_index(texts, chunk_ids)
    print("BM25 Rebuild Complete! Saved to data/processed/")

if __name__ == "__main__":
    rebuild()
