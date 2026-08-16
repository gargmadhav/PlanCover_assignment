from typing import List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.ingestion.document_processor import InternalDoc, InternalPage
from backend.app.preprocessing.cleaner import TextCleaner
from backend.app.preprocessing.section_detector import SectionDetector

class DocChunk(BaseModel):
    chunk_id: str
    document_id: str
    section: str
    pages: List[int]
    content: str
    tables_markdown: List[str] = Field(default_factory=list)

class DocumentChunker:
    @staticmethod
    def chunk_document(doc: InternalDoc) -> List[DocChunk]:
        """
        Creates section and page-aware chunks from InternalDoc.
        Combines page text with extracted tables into unified structured chunks.
        """
        chunks: List[DocChunk] = []
        
        for page in doc.pages:
            cleaned_text = TextCleaner.clean_page_text(page.text)
            tables_md = [t.markdown for t in page.tables if t.markdown]
            
            # Combine text and tables
            full_page_content_blocks = []
            if cleaned_text:
                full_page_content_blocks.append(cleaned_text)
            if tables_md:
                full_page_content_blocks.append("\n\n-- TABLES ON THIS PAGE --\n" + "\n\n".join(tables_md))
                
            combined_content = "\n\n".join(full_page_content_blocks)
            
            # Detect section categories
            sections = SectionDetector.detect_sections(combined_content)
            primary_section = sections[0] if sections else "GENERAL"
            
            chunk = DocChunk(
                chunk_id=f"{doc.document_id}_p{page.page_number}",
                document_id=doc.document_id,
                section=primary_section,
                pages=[page.page_number],
                content=combined_content,
                tables_markdown=tables_md
            )
            chunks.append(chunk)
            
        return chunks
