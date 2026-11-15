import os
import sys
import time
import pandas as pd
import numpy as np

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from retrieval.embeddings import RegintelEmbeddings
from retrieval.vector_store import RegintelVectorStore

def rebuild_faiss():
    data_dir = os.path.join(_PKG_ROOT, "data", "processed")
    sebi_path = os.path.join(data_dir, "sebi_chunks.parquet")
    rbi_path = os.path.join(data_dir, "rbi_chunks.parquet")
    
    print("Loading parquet files...")
    sebi_df = pd.read_parquet(sebi_path)
    rbi_df = pd.read_parquet(rbi_path)
    df = pd.concat([sebi_df, rbi_df], ignore_index=True)
    
    texts = df['text'].astype(str).tolist()
    chunk_ids = df['chunk_id'].astype(str).tolist()
    total = len(texts)
    print(f"Total chunks to embed: {total}")
    
    t0 = time.time()
    emb_model = RegintelEmbeddings()
    # Batch size 128 for efficient CPU throughput
    embeddings = emb_model.model.encode(
        texts,
        batch_size=128,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    t1 = time.time()
    print(f"Embedding completed in {t1 - t0:.1f}s. Shape: {embeddings.shape}")
    
    vs = RegintelVectorStore(
        index_path=os.path.join(data_dir, "faiss_index.bin"),
        meta_path=os.path.join(data_dir, "faiss_meta.json")
    )
    vs.build_index(embeddings, chunk_ids)
    
    size_bytes = os.path.getsize(vs.index_path)
    print(f"FAISS index saved to: {vs.index_path}")
    print(f"FAISS index size: {size_bytes / (1024 * 1024):.2f} MB ({size_bytes} bytes)")
    
    # Verification
    loaded = vs.load()
    print(f"Verification load(): {loaded}")
    print(f"Total vectors in index: {vs.index.ntotal}")
    assert vs.index.ntotal == total, f"Expected {total} vectors, got {vs.index.ntotal}"
    print("FAISS index rebuild and verification SUCCESSFUL!")

if __name__ == "__main__":
    rebuild_faiss()

