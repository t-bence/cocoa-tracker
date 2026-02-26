import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    telegram_token: str
    telegram_chat_id: str
    bucket: str
    storage_file: str = "dates.json"
    url: str = (
        "https://bfz.hu/en/concerts-tickets/concerts-and-festivals/cocoa-concerts/"
    )


class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""

    pass


def get_config(env_file: Optional[str] = ".env") -> Settings:
    """
    Load configuration from environment variables and .env file.
    """
    if env_file:
        load_dotenv(env_file)

    t_token = os.getenv("TELEGRAM_TOKEN")
    t_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bucket = os.getenv("BUCKET")

    missing = [
        name
        for name, val in {
            "TELEGRAM_TOKEN": t_token,
            "TELEGRAM_CHAT_ID": t_chat_id,
            "BUCKET": bucket,
        }.items()
        if not val
    ]

    if missing:
        raise ConfigError(f"Missing required configuration: {', '.join(missing)}")

    return Settings(
        telegram_token=t_token,  # type: ignore
        telegram_chat_id=t_chat_id,  # type: ignore
        bucket=bucket,  # type: ignore
        storage_file=os.getenv("STORAGE_FILE", "dates.json"),
        url=os.getenv(
            "URL",
            "https://bfz.hu/en/concerts-tickets/concerts-and-festivals/cocoa-concerts/",
        ),
    )
