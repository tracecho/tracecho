import os
import faiss
import json
import numpy as np

class RegintelVectorStore:
    def __init__(self, index_path="d:/REGINTEL/regintel/data/processed/faiss_index.bin", meta_path="d:/REGINTEL/regintel/data/processed/faiss_meta.json"):
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = None
        self.chunk_ids = []

    def build_index(self, embeddings, chunk_ids):
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.chunk_ids = chunk_ids
        self.save()

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunk_ids, f)

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, 'r', encoding='utf-8') as f:
                self.chunk_ids = json.load(f)
            return True
        return False
        
    def search(self, query_embedding, k=25):
        if not self.index: raise Exception("Index not loaded.")
        D, I = self.index.search(np.array([query_embedding]), k)
        results = []
        for i, idx in enumerate(I[0]):
            if idx != -1:
                # Convert L2 distance to slightly more interpretable score (inverse/negative)
                score = 1.0 / (1.0 + float(D[0][i]))
                results.append((self.chunk_ids[idx], score))
        return results
