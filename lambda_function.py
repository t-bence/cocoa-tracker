import json
import logging
from typing import Any

from src.common.commands import CommandRegistry
from src.common.config import get_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_command_text(update: Any, authorized_chat_id: str) -> str | None:
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

        # Parse Telegram update if present
        body = event.get("body")
        update = None
        if body and isinstance(body, str):
            try:
                update = json.loads(body)
            except json.JSONDecodeError:
                pass
        elif isinstance(event, dict) and "message" in event:
            update = event

        command_text = (
            _get_command_text(update, config.telegram_chat_id) if update else None
        )

        # Route and execute the command
        registry = CommandRegistry(config)
        command = registry.get_command(command_text)
        command.execute(force=event.get("force", False))

        return {"statusCode": 200, "body": json.dumps({"status": "ok"})}

    except Exception as e:
        logger.exception(f"Unhandled exception in lambda_handler: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
