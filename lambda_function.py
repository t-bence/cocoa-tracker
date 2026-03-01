import json
import logging
from typing import Any

from src.common.config import get_config
from src.modules.concerts.service import create_concert_service
from src.modules.home.service import create_home_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_command(update: Any, authorized_chat_id: str) -> str | None:
    """Check if the Telegram update contains an authorized command."""
    if not isinstance(update, dict):
        return None

    message = update.get("message")
    if not isinstance(message, dict):
        return None

    # Security: Verify the message comes from the authorized chat ID
    chat = message.get("chat")
    if not isinstance(chat, dict) or str(chat.get("id")) != authorized_chat_id:
        logger.warning(
            f"Received message from unauthorized chat: {chat.get('id') if chat else 'unknown'}"
        )
        return None

    return message.get("text")


def lambda_handler(event: dict[str, Any] | None, context: object) -> dict[str, Any]:  # pyright: ignore[reportUnusedParameter]
    logger.info("Lambda handler started")

    event = event or {}
    try:
        config = get_config()

        # Check if the event is a Telegram update
        body = event.get("body")
        update = None
        if body and isinstance(body, str):
            try:
                update = json.loads(body)
            except json.JSONDecodeError:
                pass
        elif isinstance(event, dict) and "message" in event:
            update = event

        command = _get_command(update, config.telegram_chat_id) if update else None

        if command == "/query":
            logger.info("Processing /query command")
            service = create_concert_service(config)
            service.run(force=True)
        elif command == "/home":
            logger.info("Processing /home command")
            create_home_service(config).run()
        else:
            # Normal scheduled run (or unknown command from authorized user)
            logger.info("Normal scheduled run or unknown command")
            force = event.get("force", False)
            service = create_concert_service(config)
            service.run(force=force)

        return {"statusCode": 200, "body": json.dumps({"status": "ok"})}

    except Exception as e:
        logger.exception(f"Unhandled exception in lambda_handler: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Running locally to test notifications (force=True)")

    # Use LocalStorage for local script execution to avoid needing AWS credentials
    config = get_config()

    from src.common.notifications import TelegramNotificationService
    from src.common.storage import LocalStorage
    from src.modules.concerts.service import ConcertService

    storage = LocalStorage(base_dir=".")
    notifier = TelegramNotificationService(
        config.telegram_token, config.telegram_chat_id
    )
    service = ConcertService(config, storage, notifier)

    service.run(force=True)
