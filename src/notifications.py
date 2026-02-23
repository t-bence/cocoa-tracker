import datetime as dt
import logging
from abc import ABC, abstractmethod

import requests

logger = logging.getLogger()


class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, dates: list[dt.date]) -> None:
        pass

    def _format_message(self, dates: list[dt.date]) -> str:
        formatted_dates: str = "\n".join(
            [f"- {date.strftime('%Y-%m-%d')}" for date in dates]
        )
        return f"""**Van hely kakaókoncertre!** 🚀
Dátumok:
{formatted_dates}"""


class TelegramNotificationService(NotificationService):
    def __init__(self, token: str, chat_id: str):
        self.token: str = token
        self.chat_id: str = chat_id

    def send_notification(self, dates: list[dt.date]) -> None:
        logger.info(f"Preparing to send Telegram message for {len(dates)} dates")
        message = self._format_message(dates)
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        try:
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
            )
            logger.info(f"Telegram response status: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
