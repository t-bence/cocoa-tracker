import logging

from src.config import Settings
from src.notifications import NotificationService, TelegramNotificationService
from src.scraper import fetch_concert_dates
from src.storage import DateCache, S3Storage, Storage

logger = logging.getLogger(__name__)


class ConcertTrackerService:
    def __init__(
        self,
        config: Settings,
        storage: Storage,
        notification_service: NotificationService,
    ):
        self.config = config
        self.cache = DateCache(storage, config.storage_file)
        self.notification_service = notification_service

    def run(self, force: bool | str = False) -> None:
        logger.info("Starting concert tracker run")
        current_dates = fetch_concert_dates(self.config.url)

        if not current_dates:
            logger.info("No dates found or error during scraping")
            # If force is true, we might still want to proceed with cached dates if we want to test notification
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


def create_service(config: Settings) -> ConcertTrackerService:
    storage = S3Storage(config.bucket)
    notification_service = TelegramNotificationService(
        config.telegram_token, config.telegram_chat_id
    )
    return ConcertTrackerService(config, storage, notification_service)
