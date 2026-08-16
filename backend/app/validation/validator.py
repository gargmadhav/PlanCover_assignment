from typing import List
from datetime import datetime
from backend.app.schemas.response import ValidationWarning
from backend.app.schemas.policy import PolicyMetadata, DemographicsDetails
from backend.app.schemas.benefits import HospitalizationDetails, MaternityDetails, WaitingPeriodDetails
from backend.app.utils.logging import logger

class ValidationEngine:
    @staticmethod
    def validate_policy_dates(metadata: PolicyMetadata) -> List[ValidationWarning]:
        warnings = []
        if metadata.start_date and metadata.end_date:
            try:
                dt_start = datetime.strptime(metadata.start_date, "%Y-%m-%d")
                dt_end = datetime.strptime(metadata.end_date, "%Y-%m-%d")
                if dt_start >= dt_end:
                    warnings.append(ValidationWarning(
                        rule_name="DATE_ORDER_CHECK",
                        message=f"Policy start date ({metadata.start_date}) is not earlier than end date ({metadata.end_date}).",
                        severity="warning"
                    ))
            except ValueError:
                warnings.append(ValidationWarning(
                    rule_name="DATE_FORMAT_CHECK",
                    message="Policy dates could not be parsed as YYYY-MM-DD.",
                    severity="warning"
                ))
        return warnings

    @staticmethod
    def validate_demographics(demographics: DemographicsDetails) -> List[ValidationWarning]:
        warnings = []
        emp = demographics.employees_count or 0
        sp = demographics.spouses_count or 0
        ch = demographics.children_count or 0
        pa = demographics.parents_count or 0
        pil = demographics.parents_in_law_count or 0
        total = demographics.total_lives_covered
        
        sum_deps = emp + sp + ch + pa + pil
        if total is not None and sum_deps > 0:
            if sum_deps != total:
                warnings.append(ValidationWarning(
                    rule_name="DEMOGRAPHIC_SUM_CHECK",
                    message=f"Sum of demographic breakdown ({sum_deps}) does not equal stated total lives ({total}).",
                    severity="warning"
                ))
        return warnings

    @staticmethod
    def validate_percentages(hospitalization: HospitalizationDetails) -> List[ValidationWarning]:
        warnings = []
        for name, benefit in [("Room Rent", hospitalization.room_rent), ("ICU", hospitalization.icu)]:
            if benefit.percentage is not None:
                if benefit.percentage < 0.0 or benefit.percentage > 100.0:
                    warnings.append(ValidationWarning(
                        rule_name="PERCENTAGE_RANGE_CHECK",
                        message=f"{name} percentage ({benefit.percentage}%) is outside valid range [0, 100].",
                        severity="error"
                    ))
        return warnings

    @staticmethod
    def run_all_validations(
        metadata: PolicyMetadata, 
        demographics: DemographicsDetails,
        hospitalization: HospitalizationDetails
    ) -> List[ValidationWarning]:
        all_warnings = []
        all_warnings.extend(ValidationEngine.validate_policy_dates(metadata))
        all_warnings.extend(ValidationEngine.validate_demographics(demographics))
        all_warnings.extend(ValidationEngine.validate_percentages(hospitalization))
        return all_warnings
