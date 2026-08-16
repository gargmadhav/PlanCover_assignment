from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.schemas.policy import (
    InsurerDetails, PreviousPolicyDetails, PolicyStructure, 
    DemographicsDetails, PolicyMetadata
)
from app.schemas.benefits import (
    HospitalizationDetails, MaternityDetails, WaitingPeriodDetails,
    OtherBenefitsDetails, InfertilitySurrogacyDetails, AmbulanceDetails,
    BufferWaiverDetails
)

class ValidationWarning(BaseModel):
    rule_name: str
    message: str
    severity: str = "warning"  # "warning" or "error"

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    page_count: int
    file_size_bytes: int
    ocr_pages_count: int = 0
    pages_processed: List[int] = Field(default_factory=list)

class ExtractionMetadata(BaseModel):
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    pipeline_version: str = "1.0.0"
    provider_used: str
    model_used: str
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    processing_duration_seconds: float = 0.0

class QMSPolicyOutput(BaseModel):
    document_metadata: DocumentMetadata
    insurer_details: InsurerDetails
    policy_metadata: PolicyMetadata
    previous_policy_details: PreviousPolicyDetails
    policy_structure: PolicyStructure
    demographics: DemographicsDetails
    hospitalization: HospitalizationDetails
    maternity: MaternityDetails
    waiting_periods: WaitingPeriodDetails
    other_benefits: OtherBenefitsDetails
    infertility_surrogacy: InfertilitySurrogacyDetails
    ambulance: AmbulanceDetails
    buffer_waivers: BufferWaiverDetails
    validation_warnings: List[ValidationWarning] = Field(default_factory=list)
    extraction_metadata: ExtractionMetadata
