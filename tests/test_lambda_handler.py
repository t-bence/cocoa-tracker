import json
from unittest.mock import MagicMock, patch

import pytest

from lambda_function import lambda_handler


@pytest.fixture
def mock_config():
    with patch("lambda_function.get_config") as mock_get:
        mock_settings = MagicMock()
        mock_settings.telegram_chat_id = "456"
        mock_get.return_value = mock_settings
        yield mock_settings


@pytest.fixture
def mock_concert_service():
    with patch("src.common.commands.create_concert_service") as mock_create:
        mock_instance = MagicMock()
        mock_create.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_home_service():
    with patch("src.common.commands.create_home_service") as mock_create:
        mock_instance = MagicMock()
        mock_create.return_value = mock_instance
        yield mock_instance


def test_lambda_handler_scheduled_event(mock_config, mock_concert_service):
    # Simulate a scheduled event (no update body)
    event = {"source": "aws.events"}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    # Behavior: Should trigger concert service run
    mock_concert_service.run.assert_called_once()


def test_lambda_handler_telegram_query(mock_config, mock_concert_service):
    event = {"body": json.dumps({"message": {"text": "/query", "chat": {"id": 456}}})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    # Behavior: Should trigger concert service with force=True (via QueryCommand logic)
    mock_concert_service.run.assert_called_once_with(force=True)


def test_lambda_handler_telegram_home(mock_config, mock_home_service):
    event = {"body": json.dumps({"message": {"text": "/home", "chat": {"id": 456}}})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    # Behavior: Should trigger home service run
    mock_home_service.run.assert_called_once()


def test_lambda_handler_unauthorized(mock_config, mock_concert_service):
    event = {"body": json.dumps({"message": {"text": "/home", "chat": {"id": 999}}})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    # Behavior: Should ignore unauthorized command and fall back to default behavior
    mock_concert_service.run.assert_called_once()
