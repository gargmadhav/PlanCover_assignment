import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import fitz # PyMuPDF
from app.ingestion.text_extractor import TextExtractor
from app.ingestion.table_extractor import TableExtractor
from app.utils.file_utils import compute_file_hash
from app.utils.logging import logger

class TableData(BaseModel):
    table_index: int
    page_number: int
    rows: List[List[str]]
    markdown: str

class InternalPage(BaseModel):
    page_number: int
    text: str
    source_type: str  # "native_pdf" or "ocr"
    tables: List[TableData] = Field(default_factory=list)

class InternalDoc(BaseModel):
    document_id: str
    filename: str
    page_count: int
    file_size_bytes: int
    pages: List[InternalPage]
    raw_hash: str

class DocumentIngestor:
    @staticmethod
    def process_pdf(filepath: str, filename: Optional[str] = None) -> InternalDoc:
        """
        Ingests a PDF file, extracts text, tables, handles OCR fallback where needed,
        and constructs an InternalDoc representation.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        file_size = os.path.getsize(filepath)
        with open(filepath, "rb") as f:
            file_bytes = f.read()
            
        doc_hash = compute_file_hash(file_bytes)
        display_name = filename or os.path.basename(filepath)
        
        logger.info(f"Ingesting PDF '{display_name}' ({file_size} bytes, hash={doc_hash[:8]})...")
        
        fitz_doc = fitz.open(filepath)
        page_count = len(fitz_doc)
        
        pages: List[InternalPage] = []
        
        for i in range(1, page_count + 1):
            # Extract text & OCR fallback
            content = TextExtractor.extract_page_content(fitz_doc, page_num=i)
            
            # Extract tables
            table_dicts = TableExtractor.extract_tables_from_page(filepath, page_number=i)
            tables = [TableData(**t) for t in table_dicts]
            
            internal_page = InternalPage(
                page_number=i,
                text=content["text"],
                source_type=content["source_type"],
                tables=tables
            )
            pages.append(internal_page)
            
        fitz_doc.close()
        
        internal_doc = InternalDoc(
            document_id=f"doc_{doc_hash[:12]}",
            filename=display_name,
            page_count=page_count,
            file_size_bytes=file_size,
            pages=pages,
            raw_hash=doc_hash
        )
        
        logger.info(f"Ingestion complete for '{display_name}': {page_count} pages processed.")
        return internal_doc
