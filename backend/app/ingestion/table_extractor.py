from typing import List, Dict, Any, Optional
import pdfplumber
from backend.app.utils.logging import logger

class TableExtractor:
    @staticmethod
    def extract_tables_from_page(pdf_path: str, page_number: int) -> List[Dict[str, Any]]:
        """
        Extract tables from a specific page (1-indexed) using pdfplumber.
        Returns a list of table dictionaries with markdown representations and raw grid data.
        """
        extracted = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_number <= len(pdf.pages):
                    page = pdf.pages[page_number - 1]
                    tables = page.extract_tables()
                    for idx, table in enumerate(tables):
                        if not table or len(table) == 0:
                            continue
                        
                        # Clean cells
                        cleaned_table = []
                        for row in table:
                            cleaned_row = [(cell.replace('\n', ' ').strip() if cell else '') for cell in row]
                            # Only keep non-completely-empty rows
                            if any(cleaned_row):
                                cleaned_table.append(cleaned_row)
                        
                        if not cleaned_table:
                            continue
                            
                        # Format as Markdown
                        markdown_str = TableExtractor._table_to_markdown(cleaned_table)
                        extracted.append({
                            "table_index": idx + 1,
                            "page_number": page_number,
                            "rows": cleaned_table,
                            "markdown": markdown_str
                        })
        except Exception as e:
            logger.error(f"Table extraction error on page {page_number} of {pdf_path}: {e}")
            
        return extracted

    @staticmethod
    def _table_to_markdown(table: List[List[str]]) -> str:
        if not table:
            return ""
        
        # Max columns
        num_cols = max(len(row) for row in table)
        
        # Pad rows
        padded_table = []
        for row in table:
            padded_row = row + [''] * (num_cols - len(row))
            padded_table.append(padded_row)
            
        header = padded_table[0]
        header_str = "| " + " | ".join(header) + " |"
        sep_str = "| " + " | ".join(["---"] * num_cols) + " |"
        
        body_rows = []
        for row in padded_table[1:]:
            body_rows.append("| " + " | ".join(row) + " |")
            
        return "\n".join([header_str, sep_str] + body_rows)
