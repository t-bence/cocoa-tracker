import logging
from typing import Any

from src.common.base import BaseService
from src.common.config import Settings
from src.common.notifications import NotificationService, TelegramNotificationService
from src.common.storage import DateCache, S3Storage, Storage
from src.modules.concerts.scraper import fetch_concert_dates

logger = logging.getLogger(__name__)


class ConcertService(BaseService):
    def __init__(
        self,
        config: Settings,
        notification_service: NotificationService,
        storage: Storage,
    ):
        super().__init__(config, notification_service)
        self.cache = DateCache(storage, config.storage_file)

    def run(self, **kwargs: Any) -> None:
        force = kwargs.get("force", False)
        logger.info("Starting concert tracker run")
        current_dates = fetch_concert_dates(self.config.url)

        if not current_dates:
            logger.info("No dates found or error during scraping")
            if not force:
                return

        if force:
            dates_to_send = self.cache.dates if self.cache.dates else current_dates
            logger.info(f"Force mode enabled. Sending dates: {dates_to_send}")
            if dates_to_send:
                self.notification_service.send_notification(dates_to_send)
            return

        new_dates = self.cache.find_new_dates(current_dates)

        if new_dates:
            logger.info(f"New dates found: {new_dates}. Sending notifications.")
            self.notification_service.send_notification(new_dates)
            self.cache.update(current_dates)
        else:
            logger.info("No new dates found, nothing to send")


def create_concert_service(
    config: Settings,
    storage: Storage | None = None,
    notification_service: NotificationService | None = None,
) -> ConcertService:
    storage = storage or S3Storage(config.bucket)
    notification_service = notification_service or TelegramNotificationService(
        config.telegram_token, config.telegram_chat_id
    )
    return ConcertService(config, notification_service, storage)
