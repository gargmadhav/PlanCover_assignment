import numpy as np
from typing import List, Tuple
from backend.app.preprocessing.chunker import DocChunk
from backend.app.retrieval.embeddings import embedding_engine
from backend.app.utils.logging import logger

class VectorStore:
    def __init__(self):
        self.chunks: List[DocChunk] = []
        self.embeddings: np.ndarray = np.array([])

    def index_chunks(self, chunks: List[DocChunk]):
        self.chunks = chunks
        if not chunks:
            return
            
        texts = [f"{c.section}\n{c.content}" for c in chunks]
        self.embeddings = embedding_engine.encode(texts)
        logger.info(f"Indexed {len(chunks)} document chunks in VectorStore.")

    def search(self, query: str, top_k: int = 4) -> List[Tuple[DocChunk, float]]:
        if not self.chunks or len(self.embeddings) == 0:
            return []
            
        query_emb = embedding_engine.encode([query])
        
        # Cosine similarity
        norm_query = query_emb / (np.linalg.norm(query_emb, axis=1, keepdims=True) + 1e-9)
        norm_doc = self.embeddings / (np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-9)
        scores = np.dot(norm_doc, norm_query.T).flatten()
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(scores[idx])))
            
        return results
