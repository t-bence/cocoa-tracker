import logging

from src.config import get_config
from src.service import create_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict[str, bool | str] | None, context: object) -> None:  # pyright: ignore[reportUnusedParameter]
    logger.info("Lambda handler started")

    try:
        config = get_config()
        service = create_service(config)

        force = (event or {}).get("force", False)
        service.run(force=force)

    except Exception as e:
        logger.exception(f"Unhandled exception in lambda_handler: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Running locally to test notifications (force=True)")

    # Use LocalStorage for local script execution to avoid needing AWS credentials
    config = get_config()
    from src.notifications import TelegramNotificationService
    from src.service import ConcertTrackerService
    from src.storage import LocalStorage

    storage = LocalStorage(base_dir=".")
    notifier = TelegramNotificationService(
        config.telegram_token, config.telegram_chat_id
    )
    service = ConcertTrackerService(config, storage, notifier)

    service.run(force=True)
