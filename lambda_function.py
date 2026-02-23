import logging

from src.config import get_config
from src.notifications import TelegramNotificationService
from src.scraper import fetch_concert_dates
from src.storage import DateCache, S3Storage

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    config = get_config()
    logger.info("Lambda handler started")

    current_dates = fetch_concert_dates(config.url)

    storage = S3Storage(config.bucket)
    cache = DateCache(storage, config.storage_file)
    new_dates = cache.find_new_dates(current_dates)

    if new_dates:
        logger.info(f"New dates found: {new_dates}. Sending notifications.")
        service = TelegramNotificationService(
            config.telegram_token, config.telegram_chat_id
        )
        service.send_notification(new_dates)
        cache.update(current_dates)
    else:
        logger.info("No new dates found, nothing to send")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Running as script")
    config = get_config()
    dates = fetch_concert_dates(config.url)
    logger.info(f"Dates found: {dates}")
