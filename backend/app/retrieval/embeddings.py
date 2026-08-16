import numpy as np
from typing import List
from backend.app.utils.logging import logger

class EmbeddingEngine:
    def __init__(self):
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"SentenceTransformer initialization failed: {e}. Falling back to tf-idf/keyword matching.")
                self._model = False
        return self._model

    def encode(self, texts: List[str]) -> np.ndarray:
        model = self._get_model()
        if model:
            try:
                embeddings = model.encode(texts, convert_to_numpy=True)
                return embeddings.astype(np.float32)
            except Exception as e:
                logger.error(f"Embedding error: {e}")
        
        # Fallback simple bag-of-words pseudo-embedding
        dim = 384
        result = np.zeros((len(texts), dim), dtype=np.float32)
        for idx, text in enumerate(texts):
            words = text.lower().split()
            for w in words:
                h = hash(w) % dim
                result[idx, h] += 1.0
            norm = np.linalg.norm(result[idx])
            if norm > 0:
                result[idx] /= norm
        return result

embedding_engine = EmbeddingEngine()
