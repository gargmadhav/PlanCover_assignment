import fitz # PyMuPDF
from typing import Dict, Any, List
from app.ingestion.ocr import ocr_engine
from app.config.settings import settings
from app.utils.logging import logger

class TextExtractor:
    @staticmethod
    def extract_page_content(doc: fitz.Document, page_num: int) -> Dict[str, Any]:
        """
        Extract native text or trigger OCR fallback if text is sparse.
        page_num is 1-indexed.
        """
        page = doc[page_num - 1]
        native_text = page.get_text("text") or ""
        cleaned_native = native_text.strip()
        
        source_type = "native_pdf"
        final_text = cleaned_native
        
        # Check if page is scanned/image-heavy or has low text count
        if len(cleaned_native) < settings.OCR_FALLBACK_MIN_TEXT_CHARS:
            logger.info(f"Page {page_num} has low native text ({len(cleaned_native)} chars). Triggering RapidOCR fallback...")
            try:
                # Render page to high-res image
                pix = page.get_pixmap(dpi=200)
                ocr_text = ocr_engine.ocr_page_image(pix)
                if len(ocr_text.strip()) > len(cleaned_native):
                    final_text = ocr_text.strip()
                    source_type = "ocr"
            except Exception as e:
                logger.error(f"Failed OCR on page {page_num}: {e}")

        return {
            "page_number": page_num,
            "text": final_text,
            "source_type": source_type,
            "char_count": len(final_text)
        }
