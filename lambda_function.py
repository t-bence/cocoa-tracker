import json
import logging
from typing import Any

from src.config import get_config
from src.service import create_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _is_query_command(update: Any, authorized_chat_id: str) -> bool:
    """Check if the Telegram update contains a /query command from an authorized chat."""
    if not isinstance(update, dict):
        return False

    message = update.get("message")
    if not isinstance(message, dict):
        return False

    # Security: Verify the message comes from the authorized chat ID
    chat = message.get("chat")
    if not isinstance(chat, dict) or str(chat.get("id")) != authorized_chat_id:
        logger.warning(
            f"Received message from unauthorized chat: {chat.get('id') if chat else 'unknown'}"
        )
        return False

    text = message.get("text")
    return text == "/query"


def lambda_handler(event: dict[str, Any] | None, context: object) -> dict[str, Any]:  # pyright: ignore[reportUnusedParameter]
    logger.info("Lambda handler started")

    event = event or {}
    force = event.get("force", False)

    try:
        config = get_config()

        # Check if the event is a Telegram webhook update
        # 1. From API Gateway/Function URL (body is a string)
        body = event.get("body")
        if body and isinstance(body, str):
            try:
                update = json.loads(body)
                if _is_query_command(update, config.telegram_chat_id):
                    logger.info("Received authorized /query from Telegram webhook.")
                    force = True
            except json.JSONDecodeError:
                pass
        # 2. Direct event (e.g. from Telegram Lambda integration or direct invoke)
        elif _is_query_command(event, config.telegram_chat_id):
            logger.info("Received authorized /query from Telegram direct event.")
            force = True

        service = create_service(config)
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
    from src.notifications import TelegramNotificationService
    from src.service import ConcertTrackerService
    from src.storage import LocalStorage

    storage = LocalStorage(base_dir=".")
    notifier = TelegramNotificationService(
        config.telegram_token, config.telegram_chat_id
    )
    service = ConcertTrackerService(config, storage, notifier)

    service.run(force=True)
