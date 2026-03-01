import json
import logging
from datetime import datetime

import boto3

from src.common.config import Settings
from src.common.notifications import NotificationService, TelegramNotificationService

logger = logging.getLogger(__name__)


class HomeService:
    def __init__(self, config: Settings, notification_service: NotificationService):
        self.config = config
        self.notification_service = notification_service
        self.iot_client = boto3.client("iot-data")

    def run(self) -> None:
        logger.info(f"Fetching shadow for thing: {self.config.iot_thing_name}")
        try:
            kwargs = {"thingName": self.config.iot_thing_name}
            if self.config.iot_shadow_name:
                kwargs["shadowName"] = self.config.iot_shadow_name

            response = self.iot_client.get_thing_shadow(**kwargs)
            streaming_body = response["payload"]
            payload = json.loads(streaming_body.read())

            state = payload.get("state", {}).get("reported", {})
            temp = state.get("temperature", "N/A")
            hum = state.get("humidity", "N/A")

            # Metadata for timestamp
            metadata = payload.get("metadata", {}).get("reported", {})
            temp_meta = metadata.get("temperature", {})
            timestamp = temp_meta.get("timestamp")

            if timestamp:
                dt_obj = datetime.fromtimestamp(timestamp)
                last_change = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_change = "Unknown"

            message = (
                f"*Home Status* 🏠\n"
                f"Temperature: {temp}°C\n"
                f"Humidity: {hum}%\n"
                f"Last update: {last_change}"
            )

            self.notification_service.send_message(message)

        except Exception as e:
            logger.error(f"Failed to fetch IoT shadow: {e}")
            self.notification_service.send_message(
                f"Error fetching home status: {str(e)}"
            )


def create_home_service(config: Settings) -> HomeService:
    notification_service = TelegramNotificationService(
        config.telegram_token, config.telegram_chat_id
    )
    return HomeService(config, notification_service)
