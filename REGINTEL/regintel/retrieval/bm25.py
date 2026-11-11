import os
import json
import pickle
from rank_bm25 import BM25Okapi

_DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

class RegintelBM25Store:
    def __init__(self,
                 index_path: str = "",
                 meta_path: str = ""):
        if not index_path:
            index_path = os.path.join(_DEFAULT_DATA_DIR, "bm25_index.pkl")
        if not meta_path:
            meta_path = os.path.join(_DEFAULT_DATA_DIR, "bm25_meta.json")
        self.index_path = index_path
        self.meta_path = meta_path
        self.bm25 = None
        self.chunk_ids = []

    def _tokenize(self, text):
        import re
        # Remove common repetitive boilerplate words to prevent them from dominating BM25
        t = str(text).lower()
        t = re.sub(r'\b(tel|email|website|reserve bank of india|sebi|master direction|master circular|website|http|www)\b', '', t)
        
        # Keep alphanumeric, filter out noisy punctuation standalone tokens
        tokens = [word for word in t.split() if re.match(r'^[a-z0-9]', word)]
        return tokens

    def build_index(self, texts, chunk_ids):
        tokenized_corpus = [self._tokenize(doc) for doc in texts]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.chunk_ids = chunk_ids
        self.save()

    def save(self):
        with open(self.index_path, 'wb') as f:
            pickle.dump(self.bm25, f)
        with open(self.meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunk_ids, f)

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            with open(self.index_path, 'rb') as f:
                self.bm25 = pickle.load(f)
            with open(self.meta_path, 'r', encoding='utf-8') as f:
                self.chunk_ids = json.load(f)
            return True
        return False
        
    def search(self, query, k=25):
        if not self.bm25: raise Exception("BM25 not loaded.")
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        top_k_idx = scores.argsort()[::-1][:k]
        results = []
        for idx in top_k_idx:
            if scores[idx] > 0:
                results.append((self.chunk_ids[idx], float(scores[idx])))
        return results
