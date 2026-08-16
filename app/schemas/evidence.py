from typing import Optional, List
from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    page: int = Field(..., description="Page number where evidence quote was found (1-indexed)")
    text: str = Field(..., description="Exact textual excerpt or table row from document")

class MoneyLimit(BaseModel):
    amount: Optional[float] = Field(default=None, description="Numeric monetary value")
    currency: str = Field(default="INR", description="Currency code (e.g. INR)")

class BenefitDetail(BaseModel):
    status: str = Field(
        default="NOT_FOUND", 
        description="Coverage status: COVERED | NOT_COVERED | WAIVED_OFF | NOT_FOUND | UNKNOWN"
    )
    limit: Optional[MoneyLimit] = Field(default=None, description="Monetary limit if applicable")
    percentage: Optional[float] = Field(default=None, description="Percentage of Sum Insured or cap if applicable")
    days: Optional[int] = Field(default=None, description="Number of days or waiting period in days")
    conditions: Optional[str] = Field(default=None, description="Specific terms, limits, or room categories")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score [0.0 - 1.0]")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Source document attribution quotes")
