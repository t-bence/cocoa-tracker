import json
from unittest.mock import MagicMock, patch

import pytest

from src.common.config import Settings
from src.modules.home.service import HomeService


@pytest.fixture
def mock_config():
    return Settings(
        telegram_token="test_token",
        telegram_chat_id="test_chat",
        bucket="test_bucket",
        iot_thing_name="test-thing",
        iot_shadow_name="test-shadow",
    )


@patch("src.modules.home.service.boto3.client")
def test_home_service_run_success(mock_iot_client_factory, mock_config):
    # Setup
    mock_iot_client = MagicMock()
    mock_iot_client_factory.return_value = mock_iot_client

    # Mock IoT shadow response
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
    service = HomeService(mock_config, mock_notification)

    # Execution
    service.run()

    # Validation
    mock_iot_client.get_thing_shadow.assert_called_once_with(
        thingName="test-thing", shadowName="test-shadow"
    )
    mock_notification.send_message.assert_called_once()
    message = mock_notification.send_message.call_args[0][0]

    assert "22.5°C" in message
    assert "45%" in message
    assert "2023-11-14" in message  # 1700000000 is 2023-11-14
