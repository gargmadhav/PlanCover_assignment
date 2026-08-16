from typing import List, Dict, Any
from backend.app.schemas.evidence import BenefitDetail, EvidenceItem

class ConfidenceEngine:
    @staticmethod
    def calculate_benefit_confidence(benefit: BenefitDetail) -> float:
        """
        Calculates transparent confidence score [0.0 - 1.0] for a benefit:
        - Base confidence from status: COVERED/NOT_COVERED/WAIVED_OFF -> 0.4
        - Evidence quote present & non-empty: +0.4
        - Monetary limit / percentage / conditions parsed cleanly: +0.2
        - NOT_FOUND without evidence: 0.0
        """
        if benefit.status == "NOT_FOUND":
            return 0.0
            
        score = 0.4  # Base status score
        
        # Evidence presence
        if benefit.evidence and len(benefit.evidence) > 0:
            valid_evidence = [e for e in benefit.evidence if e.text and len(e.text.strip()) > 5]
            if valid_evidence:
                score += 0.4
                
        # Structured parameters presence
        if benefit.limit and benefit.limit.amount is not None:
            score += 0.1
        if benefit.percentage is not None or benefit.days is not None:
            score += 0.1
            
        return min(round(score, 2), 1.0)

    @staticmethod
    def calculate_overall_confidence(all_confidences: List[float]) -> float:
        """Calculates weighted average overall confidence for the document extraction."""
        valid_scores = [s for s in all_confidences if s > 0.0]
        if not valid_scores:
            return 0.0
        avg = sum(valid_scores) / len(valid_scores)
        return round(avg, 2)
