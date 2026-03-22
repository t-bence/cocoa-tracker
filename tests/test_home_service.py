import json
from unittest.mock import MagicMock

import pytest

from src.common.config import Settings
from src.modules.home.service import HomeService


@pytest.fixture
def mock_config(monkeypatch):
    # Ensure env vars don't override the explicit arguments
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.delenv("BUCKET", raising=False)
    monkeypatch.delenv("IOT_THING_NAME", raising=False)
    monkeypatch.delenv("IOT_SHADOW_NAME", raising=False)

    return Settings(
        telegram_token="test_token",
        telegram_chat_id="test_chat",
        bucket="test_bucket",
        iot_thing_name="test-thing",
        iot_shadow_name="test-shadow",
    )


def test_home_service_behavior_success(mock_config):
    # Setup: Mock IoT client
    mock_iot_client = MagicMock()

    # Behavior: Define what the shadow returns
    payload = {
        "state": {
            "reported": {
                "bedroom_temperature": 22.5,
                "bedroom_humidity": 45,
                "livingroom_temperature": 23.4,
                "livingroom_humidity": 54,
            }
        },
        "metadata": {"reported": {"bedroom_temperature": {"timestamp": 1700000000}}},
    }
    mock_response = {"payload": MagicMock()}
    mock_response["payload"].read.return_value = json.dumps(payload).encode()
    mock_iot_client.get_thing_shadow.return_value = mock_response

    mock_notification = MagicMock()
    service = HomeService(mock_config, mock_notification, iot_client=mock_iot_client)

    # Execution
    service.run()

    # Behavioral Validation:
    # 1. Did we communicate with IoT correctly?
    mock_iot_client.get_thing_shadow.assert_called_once_with(
        thingName="test-thing", shadowName="test-shadow"
    )
    # 2. Was the user notified with the correct information?
    mock_notification.send_message.assert_called_once()
    message = mock_notification.send_message.call_args[0][0]

    assert "22.5°C" in message
    assert "45%" in message
    assert "2023-11-14" in message


def test_home_service_behavior_failure(mock_config):
    # Setup: Mock IoT client to fail
    mock_iot_client = MagicMock()
    mock_iot_client.get_thing_shadow.side_effect = Exception("IoT Connection Error")

    mock_notification = MagicMock()
    service = HomeService(mock_config, mock_notification, iot_client=mock_iot_client)

    # Execution
    service.run()

    # Behavioral Validation: Did the user get an error message?
    mock_notification.send_message.assert_called_once()
    message = mock_notification.send_message.call_args[0][0]
    assert "Error fetching home status" in message
    assert "IoT Connection Error" in message
