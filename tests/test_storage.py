import datetime as dt

from src.storage import _dates_to_strings, _strings_to_dates


def test_dates_to_strings_and_back():
    dates = [
        dt.date(2025, 1, 15),
        dt.date(2024, 12, 25),
        dt.date(2023, 6, 30),
    ]

    strings = _dates_to_strings(dates)
    result = _strings_to_dates(strings)

    assert result == dates


def test_dates_to_strings_format():
    dates = [dt.date(2025, 1, 15), dt.date(2024, 12, 25)]
    strings = _dates_to_strings(dates)

    assert strings == ["2025-01-15", "2024-12-25"]


def test_strings_to_dates():
    strings = ["2025-01-15", "2024-12-25", "2023-06-30"]
    dates = _strings_to_dates(strings)

    expected = [
        dt.date(2025, 1, 15),
        dt.date(2024, 12, 25),
        dt.date(2023, 6, 30),
    ]

    assert dates == expected


def test_empty_list():
    assert _dates_to_strings([]) == []
    assert _strings_to_dates([]) == []
