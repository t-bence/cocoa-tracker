import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""

    pass


class Settings(BaseSettings):
    """
    Project settings and configuration using Pydantic.
    Environment variables are automatically mapped to these fields.
    """

    telegram_token: str = Field(alias="TELEGRAM_TOKEN")
    telegram_chat_id: str = Field(alias="TELEGRAM_CHAT_ID")
    bucket: str = Field(alias="BUCKET")
    iot_thing_name: str = Field(alias="IOT_THING_NAME")
    iot_shadow_name: Optional[str] = Field(default=None, alias="IOT_SHADOW_NAME")
    storage_file: str = Field(default="dates.json", alias="STORAGE_FILE")
    url: str = Field(
        default="https://bfz.hu/en/concerts-tickets/concerts-and-festivals/cocoa-concerts/",
        alias="URL",
    )
    google_service_account_info: Optional[str] = Field(
        default=None, alias="GOOGLE_SERVICE_ACCOUNT_INFO"
    )
    google_calendar_id: str = Field(default="primary", alias="GOOGLE_CALENDAR_ID")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL"
    )

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8", extra="ignore", populate_by_name=True
    )


def get_config(env_file: Optional[str] = ".env") -> Settings:
    """
    Load configuration from environment variables and .env file.
    """
    try:
        # If env_file is provided and exists, use it. Otherwise, rely on env vars.
        if env_file and os.path.exists(env_file):
            return Settings(_env_file=env_file)
        return Settings()
    except Exception as e:
        raise ConfigError(f"Configuration error: {e}") from e
