import os
from sentence_transformers import SentenceTransformer

class RegintelEmbeddings:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            local_files_only=True
        return self._model

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        
    def embed_query(self, text):
        return self.model.encode([text], convert_to_numpy=True)[0]
