import argparse
import logging
import sys

from src.common.base import BaseService
from src.common.config import get_config
from src.common.notifications import (
    ConsoleNotificationService,
    TelegramNotificationService,
)
from src.common.storage import DummyStorage, S3Storage, Storage
from src.modules.concerts.service import create_concert_service
from src.modules.day.service import create_day_service
from src.modules.home.service import create_home_service

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("cocoa-cli")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cocoa Tracker CLI")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", action="store_true", help="Run concert query service")
    group.add_argument("--home", action="store_true", help="Run home status service")
    group.add_argument(
        "--day",
        action="store_true",
        help="Run day summary service (Google Calendar + LLM)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force execution (e.g. send notifications even if no new dates)",
    )
    parser.add_argument("--s3", action="store_true", help="Use S3 storage")
    parser.add_argument(
        "--telegram",
        action="store_true",
        help="Send notifications to Telegram instead of console",
    )

    args = parser.parse_args()

    try:
        config = get_config()

        # Setup services based on flags
        notification_service = (
            TelegramNotificationService(config.telegram_token, config.telegram_chat_id)
            if args.telegram
            else ConsoleNotificationService()
        )
        storage: Storage
        service: BaseService

        if args.s3:
            storage = S3Storage(config.bucket)
        else:
            # Default for CLI is now DummyStorage (doesn't look at S3 or local file)
            storage = DummyStorage()

        if args.query:
            logger.info(f"Running Query service with {storage.__class__.__name__}...")
            service = create_concert_service(
                config, storage=storage, notification_service=notification_service
            )

            # If using DummyStorage, everything will be "new" anyway,
            # but we use force=True if explicitly asked OR if using DummyStorage to ensure it sends everything.
            force_run = args.force or isinstance(storage, DummyStorage)
            service.run(force=force_run)

        elif args.home:
            logger.info("Running Home service...")
            service = create_home_service(
                config, notification_service=notification_service
            )
            service.run()

        elif args.day:
            logger.info("Running Day service...")
            service = create_day_service(
                config, notification_service=notification_service
            )
            service.run()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
