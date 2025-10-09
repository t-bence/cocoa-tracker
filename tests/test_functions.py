import datetime as dt
from pathlib import Path

from lambda_function import parse_html_content
from src.functions import get_month_number, get_year


def test_get_month_number():
    assert get_month_number("january") == 1
    assert get_month_number("february") == 2


def test_get_year():
    assert get_year("2024") == 2024
    assert get_year("2023.") == 2023


def test_parse_html_content():
    sample_html_path = Path(__file__).parent / "assets" / "sample_page.html"
    with open(sample_html_path, "r") as f:
        html_content = f.read()

    dates = parse_html_content(html_content)

    assert len(dates) == 2
    assert all(d == dt.date(2025, 10, 11) for d in dates)
