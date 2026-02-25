import datetime as dt
from unittest.mock import MagicMock

import pytest

from src.config import Settings
from src.service import ConcertTrackerService
from src.storage import LocalStorage


@pytest.fixture
def mock_config():
    return Settings(
        telegram_token="test_token",
        telegram_chat_id="test_chat",
        bucket="test_bucket",
        storage_file="test_dates.json",
    )


@pytest.fixture
def temp_storage(tmp_path):
    return LocalStorage(base_dir=str(tmp_path))


def test_service_run_new_dates(mock_config, temp_storage, monkeypatch):
    # Setup
    mock_notification = MagicMock()
    service = ConcertTrackerService(mock_config, temp_storage, mock_notification)

    # Mock scraper to return specific dates
    test_dates = sorted([dt.date(2025, 1, 1), dt.date(2025, 1, 2)])
    monkeypatch.setattr("src.service.fetch_concert_dates", lambda url: test_dates)

    # Execution: First run (all dates are new)
    service.run()

    # Validation
    mock_notification.send_notification.assert_called_once_with(sorted(test_dates))
    assert len(service.cache.dates) == 2

    # Execution: Second run (no new dates)
    mock_notification.reset_mock()
    service.run()

    # Validation: Notification should NOT be sent again
    mock_notification.send_notification.assert_not_called()


def test_service_run_force_mode(mock_config, temp_storage, monkeypatch):
    mock_notification = MagicMock()
    service = ConcertTrackerService(mock_config, temp_storage, mock_notification)

    test_dates = [dt.date(2025, 1, 1)]
    monkeypatch.setattr("src.service.fetch_concert_dates", lambda url: test_dates)

    # First run to populate cache
    service.run()
    mock_notification.reset_mock()

    # Run with force=True
    service.run(force=True)

    # Validation: Should send notification even if dates are already in cache
    mock_notification.send_notification.assert_called_once_with(test_dates)
