import pytest
from app.preprocessing.normalizer import DataNormalizer

def test_normalize_money():
    amt, curr = DataNormalizer.normalize_money("₹ 5,00,000")
    assert amt == 500000.0
    assert curr == "INR"

    amt2, curr2 = DataNormalizer.normalize_money("5 Lakhs")
    assert amt2 == 500000.0

    amt3, curr3 = DataNormalizer.normalize_money("Rs. 9600.00")
    assert amt3 == 9600.0

def test_normalize_date():
    assert DataNormalizer.normalize_date("02/06/2022") == "2022-06-02"
    assert DataNormalizer.normalize_date("18-08-2023") == "2023-08-18"

def test_normalize_status():
    assert DataNormalizer.normalize_status("Waived") == "WAIVED_OFF"
    assert DataNormalizer.normalize_status("Nil waiting period") == "WAIVED_OFF"
    assert DataNormalizer.normalize_status("Not Covered") == "NOT_COVERED"
    assert DataNormalizer.normalize_status("Covered") == "COVERED"
    assert DataNormalizer.normalize_status(None) == "NOT_FOUND"
    assert DataNormalizer.normalize_status("") == "NOT_FOUND"
