import json
import logging
from datetime import datetime
from typing import Any

import boto3

from src.common.base import BaseService
from src.common.config import Settings
from src.common.notifications import NotificationService, TelegramNotificationService

logger = logging.getLogger(__name__)


class HomeService(BaseService):
    def __init__(
        self,
        config: Settings,
        notification_service: NotificationService,
        iot_client: Any = None,
    ):
        super().__init__(config, notification_service)
        self.iot_client = iot_client or boto3.client("iot-data")

    def run(self, **kwargs: Any) -> None:
        logger.info(f"Fetching shadow for thing: {self.config.iot_thing_name}")
        try:
            shadow_kwargs = {"thingName": self.config.iot_thing_name}
            if self.config.iot_shadow_name:
                shadow_kwargs["shadowName"] = self.config.iot_shadow_name

            response = self.iot_client.get_thing_shadow(**shadow_kwargs)
            streaming_body = response["payload"]
            payload = json.loads(streaming_body.read())

            state = payload.get("state", {}).get("reported", {})
            bedroom_temperature = state.get("bedroom_temperature", "N/A")
            bedroom_humidity = state.get("bedroom_humidity", "N/A")

            livingroom_temperature = state.get("livingroom_temperature", "N/A")
            livingroom_humidity = state.get("livingroom_humidity", "N/A")

            # Metadata for timestamp
            metadata = payload.get("metadata", {}).get("reported", {})
            temp_meta = metadata.get("bedroom_temperature", {})
            timestamp = temp_meta.get("timestamp")

            if timestamp:
                dt_obj = datetime.fromtimestamp(timestamp)
                last_change = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_change = "Unknown"

            message = (
                f"*Bedroom Status* 🏠\n"
                f"Temperature: {bedroom_temperature}°C\n"
                f"Humidity: {bedroom_humidity}%\n"
                "\n"
                f"*Living Room Status* 🏠\n"
                f"Temperature: {livingroom_temperature}°C\n"
                f"Humidity: {livingroom_humidity}%\n"
                "\n"
                f"Last update: {last_change}"
            )

            self.notification_service.send_message(message)

        except Exception as e:
            logger.error(f"Failed to fetch IoT shadow: {e}")
            self.notification_service.send_message(
                f"Error fetching home status: {str(e)}"
            )


def create_home_service(
    config: Settings,
    notification_service: NotificationService | None = None,
    iot_client: Any = None,
) -> HomeService:
    notification_service = notification_service or TelegramNotificationService(
        config.telegram_token, config.telegram_chat_id
    )
    return HomeService(config, notification_service, iot_client=iot_client)
