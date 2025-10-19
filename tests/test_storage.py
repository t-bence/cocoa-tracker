import datetime as dt

from src.storage import DateCache, _dates_to_strings, _strings_to_dates


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


def test_finding_new_dates_empty_cache():
    cache = DateCache(old_dates=[])
    assert cache.find_new_dates([dt.date(2025, 10, 1)]) == [dt.date(2025, 10, 1)]


def test_finding_new_dates_with_existing_dates():
    old_dates = [dt.date(2025, 10, 1), dt.date(2025, 10, 15)]
    cache = DateCache(old_dates=old_dates)

    current_dates = [dt.date(2025, 10, 1), dt.date(2025, 10, 15), dt.date(2025, 11, 1)]
    new_dates = cache.find_new_dates(current_dates)

    assert new_dates == [dt.date(2025, 11, 1)]


def test_finding_no_new_dates():
    old_dates = [dt.date(2025, 10, 1), dt.date(2025, 10, 15)]
    cache = DateCache(old_dates=old_dates)

    current_dates = [dt.date(2025, 10, 1), dt.date(2025, 10, 15)]
    new_dates = cache.find_new_dates(current_dates)

    assert new_dates == []


def test_finding_multiple_new_dates():
    old_dates = [dt.date(2025, 10, 1)]
    cache = DateCache(old_dates=old_dates)

    current_dates = [
        dt.date(2025, 10, 1),
        dt.date(2025, 10, 15),
        dt.date(2025, 11, 1),
        dt.date(2025, 12, 1),
    ]
    new_dates = cache.find_new_dates(current_dates)

    assert set(new_dates) == {
        dt.date(2025, 10, 15),
        dt.date(2025, 11, 1),
        dt.date(2025, 12, 1),
    }


def test_all_dates_are_new():
    old_dates = [dt.date(2025, 10, 1)]
    cache = DateCache(old_dates=old_dates)

    current_dates = [dt.date(2025, 11, 1), dt.date(2025, 12, 1)]
    new_dates = cache.find_new_dates(current_dates)

    assert set(new_dates) == {dt.date(2025, 11, 1), dt.date(2025, 12, 1)}
