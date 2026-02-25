"""Tests for LocalStorage and DateCache."""

import datetime as dt

import pytest

from src.storage import DateCache, LocalStorage

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_storage(tmp_path):
    """Return a LocalStorage rooted in a fresh temp directory."""
    return LocalStorage(base_dir=str(tmp_path))


@pytest.fixture
def cache(tmp_storage):
    """Return a DateCache backed by LocalStorage with a fixed key."""
    return DateCache(storage=tmp_storage, key="dates.json")


# ---------------------------------------------------------------------------
# LocalStorage – read / write
# ---------------------------------------------------------------------------


class TestLocalStorage:
    def test_read_missing_key_returns_none(self, tmp_storage):
        assert tmp_storage.read("nonexistent.json") is None

    def test_write_then_read_roundtrip(self, tmp_storage):
        tmp_storage.write("hello.bin", b"world")
        assert tmp_storage.read("hello.bin") == b"world"

    def test_write_creates_nested_directories(self, tmp_storage, tmp_path):
        tmp_storage.write("a/b/c.bin", b"deep")
        assert (tmp_path / "a" / "b" / "c.bin").read_bytes() == b"deep"

    def test_overwrite_replaces_content(self, tmp_storage):
        tmp_storage.write("file.bin", b"first")
        tmp_storage.write("file.bin", b"second")
        assert tmp_storage.read("file.bin") == b"second"


# ---------------------------------------------------------------------------
# DateCache – initial state
# ---------------------------------------------------------------------------


class TestDateCacheInitialState:
    def test_empty_on_first_load(self, cache):
        assert cache.dates == []

    def test_dates_property_returns_a_copy(self, cache):
        """Mutating the returned list must not affect internal state."""
        dates = cache.dates
        dates.append(dt.date(2025, 1, 1))
        assert cache.dates == []


# ---------------------------------------------------------------------------
# DateCache – adding and retrieving dates
# ---------------------------------------------------------------------------


class TestDateCacheAddAndRetrieve:
    def test_update_stores_dates(self, cache):
        dates = [dt.date(2025, 1, 1), dt.date(2025, 6, 15), dt.date(2025, 12, 31)]
        cache.update(dates)
        assert sorted(cache.dates) == sorted(dates)

    def test_update_persists_across_instances(self, tmp_storage):
        """A new DateCache pointed at the same storage should see saved dates."""
        dates = [dt.date(2025, 3, 10), dt.date(2025, 9, 22)]
        cache1 = DateCache(storage=tmp_storage, key="dates.json")
        cache1.update(dates)

        cache2 = DateCache(storage=tmp_storage, key="dates.json")
        assert sorted(cache2.dates) == sorted(dates)

    def test_update_with_many_dates(self, cache):
        dates = [dt.date(2020 + i, (i % 12) + 1, 1) for i in range(20)]
        cache.update(dates)
        assert sorted(cache.dates) == sorted(dates)

    def test_update_with_empty_list(self, cache):
        cache.update([dt.date(2025, 1, 1)])
        cache.update([])
        assert cache.dates == []


# ---------------------------------------------------------------------------
# DateCache – updating / replacing dates
# ---------------------------------------------------------------------------


class TestDateCacheUpdate:
    def test_update_replaces_previous_dates(self, cache):
        cache.update([dt.date(2024, 1, 1)])
        cache.update([dt.date(2025, 6, 1), dt.date(2025, 7, 1)])
        assert sorted(cache.dates) == [dt.date(2025, 6, 1), dt.date(2025, 7, 1)]

    def test_update_is_idempotent(self, cache):
        dates = [dt.date(2025, 4, 4)]
        cache.update(dates)
        cache.update(dates)
        assert cache.dates == dates

    def test_second_update_persisted(self, tmp_storage):
        cache1 = DateCache(storage=tmp_storage, key="dates.json")
        cache1.update([dt.date(2024, 1, 1)])
        cache1.update([dt.date(2025, 5, 5)])

        cache2 = DateCache(storage=tmp_storage, key="dates.json")
        assert cache2.dates == [dt.date(2025, 5, 5)]


# ---------------------------------------------------------------------------
# DateCache – find_new_dates
# ---------------------------------------------------------------------------


class TestDateCacheFindNewDates:
    def test_all_new_when_cache_empty(self, cache):
        incoming = [dt.date(2025, 11, 1), dt.date(2025, 10, 1)]
        assert cache.find_new_dates(incoming) == [
            dt.date(2025, 10, 1),
            dt.date(2025, 11, 1),
        ]

    def test_no_new_when_all_cached(self, cache):
        dates = [dt.date(2025, 10, 1), dt.date(2025, 10, 15)]
        cache.update(dates)
        assert cache.find_new_dates(dates) == []

    def test_detects_single_new_date(self, cache):
        cached = [dt.date(2025, 10, 1), dt.date(2025, 10, 15)]
        cache.update(cached)
        incoming = cached + [dt.date(2025, 11, 1)]
        assert cache.find_new_dates(incoming) == [dt.date(2025, 11, 1)]

    def test_detects_multiple_new_dates(self, cache):
        cache.update([dt.date(2025, 1, 1)])
        incoming = [
            dt.date(2025, 1, 1),
            dt.date(2025, 8, 1),
            dt.date(2025, 6, 1),
            dt.date(2025, 7, 1),
        ]
        assert cache.find_new_dates(incoming) == [
            dt.date(2025, 6, 1),
            dt.date(2025, 7, 1),
            dt.date(2025, 8, 1),
        ]

    def test_empty_incoming_returns_empty(self, cache):
        cache.update([dt.date(2025, 1, 1)])
        assert cache.find_new_dates([]) == []
