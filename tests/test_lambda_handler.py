import json
from unittest.mock import MagicMock, patch

import pytest

from lambda_function import lambda_handler


@pytest.fixture
def mock_service():
    with patch("lambda_function.create_service") as mock_create:
        mock_instance = MagicMock()
        mock_create.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_config():
    with patch("lambda_function.get_config") as mock_get:
        mock_settings = MagicMock()
        mock_get.return_value = mock_settings
        yield mock_settings


def test_lambda_handler_scheduled_event(mock_service, mock_config):
    mock_config.telegram_chat_id = "456"
    # Simulate a scheduled event (no force, no Telegram update)
    event = {"source": "aws.events"}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_service.run.assert_called_once_with(force=False)


def test_lambda_handler_force_event(mock_service, mock_config):
    mock_config.telegram_chat_id = "456"
    # Simulate an event with force=True
    event = {"force": True}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_service.run.assert_called_once_with(force=True)


def test_lambda_handler_telegram_webhook_query_authorized(mock_service, mock_config):
    mock_config.telegram_chat_id = "456"
    # Simulate an authorized Telegram webhook event
    telegram_update = {
        "update_id": 123,
        "message": {"text": "/query", "chat": {"id": 456}},
    }
    event = {"body": json.dumps(telegram_update), "httpMethod": "POST"}

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_service.run.assert_called_once_with(force=True)


def test_lambda_handler_telegram_webhook_query_unauthorized(mock_service, mock_config):
    mock_config.telegram_chat_id = "456"
    # Simulate an UNAUTHORIZED Telegram webhook event
    telegram_update = {
        "update_id": 123,
        "message": {"text": "/query", "chat": {"id": 999}},
    }
    event = {"body": json.dumps(telegram_update), "httpMethod": "POST"}

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    # Should NOT be forced because chat ID doesn't match
    mock_service.run.assert_called_once_with(force=False)


def test_lambda_handler_telegram_direct_query(mock_service, mock_config):
    mock_config.telegram_chat_id = "456"
    # Simulate a direct Telegram update event
    event = {"update_id": 123, "message": {"text": "/query", "chat": {"id": 456}}}

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_service.run.assert_called_once_with(force=True)


def test_lambda_handler_telegram_other_command(mock_service, mock_config):
    # Simulate a Telegram update with a different command
    event = {"update_id": 123, "message": {"text": "/help", "chat": {"id": 456}}}

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_service.run.assert_called_once_with(force=False)


def test_lambda_handler_exception(mock_service, mock_config):
    # Simulate an exception in the service
    mock_service.run.side_effect = Exception("Test error")

    event = {"force": True}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 500
    assert "Test error" in response["body"]
