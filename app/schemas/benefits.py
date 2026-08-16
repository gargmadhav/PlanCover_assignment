from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.evidence import BenefitDetail

class HospitalizationDetails(BaseModel):
    room_rent: BenefitDetail = Field(default_factory=BenefitDetail)
    icu: BenefitDetail = Field(default_factory=BenefitDetail)
    pre_hospitalization: BenefitDetail = Field(default_factory=BenefitDetail)
    post_hospitalization: BenefitDetail = Field(default_factory=BenefitDetail)

class MaternityDetails(BaseModel):
    waiting_period_9_months: BenefitDetail = Field(default_factory=BenefitDetail)
    baby_day_one_cover: BenefitDetail = Field(default_factory=BenefitDetail)
    vaccination_coverage: BenefitDetail = Field(default_factory=BenefitDetail)
    normal_delivery_metro: BenefitDetail = Field(default_factory=BenefitDetail)
    normal_delivery_non_metro: BenefitDetail = Field(default_factory=BenefitDetail)
    c_section_metro: BenefitDetail = Field(default_factory=BenefitDetail)
    c_section_non_metro: BenefitDetail = Field(default_factory=BenefitDetail)

class WaitingPeriodDetails(BaseModel):
    initial_30_days: BenefitDetail = Field(default_factory=BenefitDetail)
    first_second_year_illness: BenefitDetail = Field(default_factory=BenefitDetail)
    pre_existing_diseases_ped: BenefitDetail = Field(default_factory=BenefitDetail)

class OtherBenefitsDetails(BaseModel):
    day_care_expenses: BenefitDetail = Field(default_factory=BenefitDetail)
    opd_benefit: BenefitDetail = Field(default_factory=BenefitDetail)
    teleconsultation: BenefitDetail = Field(default_factory=BenefitDetail)
    pharmacy_discount: BenefitDetail = Field(default_factory=BenefitDetail)
    domiciliary_hospitalization: BenefitDetail = Field(default_factory=BenefitDetail)
    annual_health_checkup: BenefitDetail = Field(default_factory=BenefitDetail)
    modern_treatment: BenefitDetail = Field(default_factory=BenefitDetail)
    bariatric_treatment: BenefitDetail = Field(default_factory=BenefitDetail)
    psychiatric_treatment: BenefitDetail = Field(default_factory=BenefitDetail)
    ayush_treatment: BenefitDetail = Field(default_factory=BenefitDetail)
    lgbtq_coverage: BenefitDetail = Field(default_factory=BenefitDetail)
    live_in_partner_coverage: BenefitDetail = Field(default_factory=BenefitDetail)
    organ_donor_expenses: BenefitDetail = Field(default_factory=BenefitDetail)

class InfertilitySurrogacyDetails(BaseModel):
    infertility_treatment: BenefitDetail = Field(default_factory=BenefitDetail)
    surrogacy_coverage: BenefitDetail = Field(default_factory=BenefitDetail)

class AmbulanceDetails(BaseModel):
    road_ambulance: BenefitDetail = Field(default_factory=BenefitDetail)
    air_ambulance: BenefitDetail = Field(default_factory=BenefitDetail)

class BufferWaiverDetails(BaseModel):
    corporate_buffer: BenefitDetail = Field(default_factory=BenefitDetail)
    disease_wise_capping: BenefitDetail = Field(default_factory=BenefitDetail)
    waiver_conditions: BenefitDetail = Field(default_factory=BenefitDetail)
