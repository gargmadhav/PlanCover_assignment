import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.schemas.policy import PolicyMetadata, DemographicsDetails
from backend.app.schemas.benefits import HospitalizationDetails
from backend.app.validation.validator import ValidationEngine

def test_date_order_validation():
    meta = PolicyMetadata(start_date="2023-08-18", end_date="2022-08-18")
    warnings = ValidationEngine.validate_policy_dates(meta)
    assert len(warnings) == 1
    assert warnings[0].rule_name == "DATE_ORDER_CHECK"

def test_demographics_validation():
    demo = DemographicsDetails(
        employees_count=10,
        spouses_count=5,
        children_count=5,
        total_lives_covered=25
    )
    warnings = ValidationEngine.validate_demographics(demo)
    assert len(warnings) == 1
    assert warnings[0].rule_name == "DEMOGRAPHIC_SUM_CHECK"
