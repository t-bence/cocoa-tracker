import datetime as dt
from unittest.mock import MagicMock, patch

from src.notifications import TelegramNotificationService


def test_telegram_notification_service_send_success():
    token = "test_token"
    chat_id = "test_chat_id"
    service = TelegramNotificationService(token, chat_id)
    dates = [dt.date(2023, 10, 27)]

    with patch("src.notifications.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service.send_notification(dates)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == f"https://api.telegram.org/bot{token}/sendMessage"
        assert kwargs["json"]["chat_id"] == chat_id
        assert "2023-10-27" in kwargs["json"]["text"]


def test_telegram_notification_service_send_failure():
    token = "test_token"
    chat_id = "test_chat_id"
    service = TelegramNotificationService(token, chat_id)
    dates = [dt.date(2023, 10, 27)]

    with patch("src.notifications.requests.post") as mock_post:
        mock_post.side_effect = Exception("Network error")

        # Should not raise exception because of try-except block in send_notification
        service.send_notification(dates)

        mock_post.assert_called_once()
