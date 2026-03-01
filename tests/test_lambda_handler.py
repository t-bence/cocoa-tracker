import json
from unittest.mock import MagicMock, patch

import pytest

from lambda_function import lambda_handler


@pytest.fixture
def mock_concert_service():
    with patch("lambda_function.create_concert_service") as mock_create:
        mock_instance = MagicMock()
        mock_create.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_home_service():
    with patch("lambda_function.create_home_service") as mock_create:
        mock_instance = MagicMock()
        mock_create.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_config():
    with patch("lambda_function.get_config") as mock_get:
        mock_settings = MagicMock()
        mock_get.return_value = mock_settings
        yield mock_settings


def test_lambda_handler_scheduled_event(
    mock_concert_service, mock_home_service, mock_config
):
    mock_config.telegram_chat_id = "456"
    # Simulate a scheduled event
    event = {"source": "aws.events"}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_concert_service.run.assert_called_once_with(force=False)
    mock_home_service.run.assert_not_called()


def test_lambda_handler_telegram_query(
    mock_concert_service, mock_home_service, mock_config
):
    mock_config.telegram_chat_id = "456"
    event = {"body": json.dumps({"message": {"text": "/query", "chat": {"id": 456}}})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_concert_service.run.assert_called_once_with(force=True)
    mock_home_service.run.assert_not_called()


def test_lambda_handler_telegram_home(
    mock_concert_service, mock_home_service, mock_config
):
    mock_config.telegram_chat_id = "456"
    event = {"body": json.dumps({"message": {"text": "/home", "chat": {"id": 456}}})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_home_service.run.assert_called_once()
    mock_concert_service.run.assert_not_called()


def test_lambda_handler_unauthorized(
    mock_concert_service, mock_home_service, mock_config
):
    mock_config.telegram_chat_id = "456"
    event = {"body": json.dumps({"message": {"text": "/home", "chat": {"id": 999}}})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    # Should fall back to default (concert service scheduled run)
    mock_concert_service.run.assert_called_once_with(force=False)
    mock_home_service.run.assert_not_called()
