import re
from typing import Optional, Tuple, Any
from datetime import datetime

class DataNormalizer:
    @staticmethod
    def normalize_money(text: Optional[str]) -> Tuple[Optional[float], str]:
        """
        Parses strings like:
        - '₹ 5,00,000' -> (500000.0, 'INR')
        - '5 Lakhs' -> (500000.0, 'INR')
        - 'Rs. 9600.00' -> (9600.0, 'INR')
        - '24000000' -> (24000000.0, 'INR')
        """
        if not text:
            return None, "INR"
            
        clean = text.replace(',', '').strip()
        
        # Check Lakh / Cr patterns
        lakh_match = re.search(r'([\d\.]+)\s*(?:lakh|lakhs|lac|lacs)', clean, re.IGNORECASE)
        if lakh_match:
            try:
                val = float(lakh_match.group(1)) * 100000.0
                return val, "INR"
            except ValueError:
                pass
                
        cr_match = re.search(r'([\d\.]+)\s*(?:crore|crores|cr)', clean, re.IGNORECASE)
        if cr_match:
            try:
                val = float(cr_match.group(1)) * 10000000.0
                return val, "INR"
            except ValueError:
                pass

        # Standard numeric extraction
        num_match = re.search(r'(\d+(?:\.\d+)?)', clean)
        if num_match:
            try:
                val = float(num_match.group(1))
                return val, "INR"
            except ValueError:
                pass
                
        return None, "INR"

    @staticmethod
    def normalize_date(text: Optional[str]) -> Optional[str]:
        """
        Parses dates like '02/06/2022', '18-08-2023', '02-Apr-2022', '17-Mar-2022' to 'YYYY-MM-DD'.
        """
        if not text:
            return None
            
        clean = text.strip()
        
        # Regex for '02-Apr-2022' or '02 Apr 2022'
        m_txt = re.search(r'(\d{1,2})[\s/.-]([A-Za-z]{3,9})[\s/.-](\d{4})', clean)
        if m_txt:
            d_str, m_str, y_str = m_txt.group(1), m_txt.group(2)[:3].title(), m_txt.group(3)
            try:
                dt = datetime.strptime(f"{d_str} {m_str} {y_str}", "%d %b %Y")
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass
                
        # Regex for numeric dates '02/06/2022' or '18-08-2023'
        m = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})', clean)
        if m:
            d, m_val, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                dt = datetime(y, m_val, d)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

        m2 = re.search(r'(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})', clean)
        if m2:
            y, m_val, d = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
            try:
                dt = datetime(y, m_val, d)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass
                
        return None

    @staticmethod
    def normalize_percentage(text: Optional[str]) -> Optional[float]:
        """
        Parses strings like '2% of SI', '4%', '10.5%' into float values.
        """
        if not text:
            return None
        m = re.search(r'([\d\.]+)\s*%', text)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return None

    @staticmethod
    def normalize_status(text: Optional[str], default_if_none: str = "NOT_FOUND") -> str:
        """
        Normalizes benefit status string to one of:
        - COVERED
        - NOT_COVERED
        - WAIVED_OFF
        - NOT_FOUND
        - UNKNOWN
        
        CRITICAL REQUIREMENT: Distinguish NOT_FOUND from NOT_COVERED and WAIVED_OFF.
        """
        if not text or text.strip() == "":
            return default_if_none
            
        clean = text.lower().strip()
        
        if clean in ["not found", "not_found", "none", "n/a", "na", "missing", "unknown"]:
            return "NOT_FOUND"
            
        if any(term in clean for term in ["waived", "waiver", "waived off", "nil waiting period", "no waiting period", "0 days"]):
            return "WAIVED_OFF"
            
        if any(term in clean for term in ["not covered", "excluded", "exclusion", "non-covered", "uncovered"]):
            return "NOT_COVERED"
            
        if any(term in clean for term in ["covered", "applicable", "included", "available", "yes", "floater", "graded", "flat"]):
            return "COVERED"
            
        return "UNKNOWN"
