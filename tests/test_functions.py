import datetime as dt
from pathlib import Path

import pytest

from src.functions import get_month_number, get_year
from src.scraper import parse_html_content


def test_get_month_number():
    assert get_month_number("january") == 1
    assert get_month_number("february") == 2
    assert get_month_number("  MARCH  ") == 3


def test_get_month_number_invalid():
    with pytest.raises(ValueError, match="Unknown month name"):
        get_month_number("invalid")


def test_get_year():
    assert get_year("2024") == 2024
    assert get_year("2023.") == 2023
    assert get_year("  2025  ") == 2025


def test_get_year_invalid():
    with pytest.raises(ValueError, match="Could not parse year"):
        get_year("abc")


def test_parse_html_content():
    sample_html_path = Path(__file__).parent / "assets" / "sample_page.html"
    with open(sample_html_path, "r") as f:
        html_content = f.read()

    dates = parse_html_content(html_content)

    assert len(dates) == 2
    assert all(d == dt.date(2025, 10, 11) for d in dates)
