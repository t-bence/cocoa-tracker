from src.functions import get_month_number, get_year


def test_get_month_number():
    assert get_month_number("january") == 1
    assert get_month_number("february") == 2


def test_get_year():
    assert get_year("2024") == 2024
    assert get_year("2023.") == 2023
