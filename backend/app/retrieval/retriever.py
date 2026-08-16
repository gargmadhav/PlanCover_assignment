from typing import List
from backend.app.preprocessing.chunker import DocChunk
from backend.app.retrieval.vector_store import VectorStore

class SemanticRetriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def retrieve_chunks_for_section(self, section_name: str, query: str, top_k: int = 4) -> List[DocChunk]:
        """
        Retrieves top relevant chunks prioritizing matching section types
        followed by vector search.
        """
        # First filter by section if available
        section_matched = [c for c in self.vector_store.chunks if c.section == section_name]
        if section_matched:
            return section_matched[:top_k]
            
        results = self.vector_store.search(query, top_k=top_k)
        return [res[0] for res in results]
