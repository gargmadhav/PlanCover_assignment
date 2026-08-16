from typing import Optional, List
from pydantic import BaseModel, Field
from backend.app.schemas.evidence import EvidenceItem, MoneyLimit

class InsurerDetails(BaseModel):
    insurer_name: Optional[str] = Field(default=None, description="Inferred name of the Insurance Company")
    tpa_name: Optional[str] = Field(default=None, description="Inferred Third Party Administrator (TPA) name if present")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)

class PreviousPolicyDetails(BaseModel):
    previous_inception_date: Optional[str] = Field(default=None, description="Previous policy start date YYYY-MM-DD")
    policy_tenure_years: Optional[float] = Field(default=None, description="Policy tenure in years")
    previous_inception_premium: Optional[MoneyLimit] = Field(default=None, description="Previous year premium")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)

class PolicyStructure(BaseModel):
    employee_covered: bool = Field(default=True)
    spouse_covered: bool = Field(default=False)
    children_covered: bool = Field(default=False)
    parents_covered: bool = Field(default=False)
    parents_in_law_covered: bool = Field(default=False)
    sum_insured_tiers: List[float] = Field(default_factory=list, description="Available Sum Insured levels")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)

class DemographicsDetails(BaseModel):
    employees_count: Optional[int] = Field(default=None)
    spouses_count: Optional[int] = Field(default=None)
    children_count: Optional[int] = Field(default=None)
    parents_count: Optional[int] = Field(default=None)
    parents_in_law_count: Optional[int] = Field(default=None)
    total_lives_covered: Optional[int] = Field(default=None)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)

class PolicyMetadata(BaseModel):
    policy_number: Optional[str] = Field(default=None)
    policyholder_name: Optional[str] = Field(default=None)
    start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    premium_amount: Optional[MoneyLimit] = Field(default=None)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)
