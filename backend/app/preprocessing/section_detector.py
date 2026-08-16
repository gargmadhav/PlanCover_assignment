import re
from typing import List, Dict, Any

SECTION_KEYWORDS = {
    "POLICY_METADATA": [
        "policy certificate", "policy schedule", "policy number", "name of policyholder", 
        "period of insurance", "insurer name", "intermediary", "customer id", "policy copy"
    ],
    "DEMOGRAPHICS": [
        "employee", "spouse", "children", "parents", "total lives", "cover type", 
        "no of insured", "insured person", "main floater", "dependent"
    ],
    "HOSPITALIZATION": [
        "in-patient", "room rent", "icu", "pre-hospitalization", "post-hospitalization", 
        "hospitalisation", "day care", "cashless", "normal hospitalization"
    ],
    "MATERNITY": [
        "maternity", "normal delivery", "c-section", "caesarean", "baby day one", 
        "vaccination", "new born", "9 month", "obstetric"
    ],
    "WAITING_PERIODS": [
        "waiting period", "initial waiting", "30 day", "ped", "pre-existing", 
        "1st year", "2nd year", "specific illness", "exclusion"
    ],
    "OTHER_BENEFITS": [
        "opd", "teleconsultation", "pharmacy", "health check", "modern treatment", 
        "bariatric", "psychiatric", "ayush", "lgbtq", "live-in", "organ donor", "domiciliary"
    ],
    "INFERTILITY_SURROGACY": [
        "infertility", "surrogacy", "assisted reproduction", "ivf"
    ],
    "AMBULANCE": [
        "ambulance", "air ambulance", "emergency transportation"
    ],
    "BUFFER_WAIVERS": [
        "buffer", "corporate buffer", "disease-wise capping", "disease cap", "waiver"
    ],
    "PREMIUM_ANNEXURE": [
        "premium", "taxable value", "gst", "annexure", "rate chart", "age band"
    ]
}

class SectionDetector:
    @staticmethod
    def detect_sections(text: str) -> List[str]:
        """
        Generic semantic section detection using keyword density & structural cues.
        Returns list of matching section categories.
        """
        if not text:
            return ["GENERAL"]
            
        lower_text = text.lower()
        matched_sections = []
        
        for section, keywords in SECTION_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in lower_text)
            if count > 0:
                matched_sections.append((section, count))
                
        if not matched_sections:
            return ["GENERAL"]
            
        # Sort by match count descending
        matched_sections.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in matched_sections]
