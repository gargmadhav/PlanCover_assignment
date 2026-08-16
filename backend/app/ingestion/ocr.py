import os
import io
from typing import Optional
from PIL import Image
import fitz # PyMuPDF
import pytesseract
from backend.app.utils.logging import logger

class TesseractOCREngine:
    def __init__(self):
        self._configured = False
        self._configure_tesseract_path()

    def _configure_tesseract_path(self):
        """Locate Tesseract OCR binary executable if on Windows."""
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract binary configured at '{path}'")
                self._configured = True
                return

        # Default fallback (assumes 'tesseract' is on system PATH)
        self._configured = True

    def ocr_page_image(self, pixmap: fitz.Pixmap) -> str:
        """
        Run Tesseract OCR on a PyMuPDF Pixmap object and return extracted text.
        """
        try:
            # Convert PyMuPDF Pixmap to PIL Image
            img_bytes = pixmap.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            
            # Execute Tesseract OCR
            text = pytesseract.image_to_string(image)
            return text.strip()
            
        except Exception as e:
            logger.warning(f"Tesseract OCR execution notice: {e}. Returning empty string for scanned page.")
            return ""

ocr_engine = TesseractOCREngine()
