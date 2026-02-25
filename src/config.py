from pydantic import AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    telegram_token: str = AliasChoices("telegram_token", "TELEGRAM_TOKEN")
    telegram_chat_id: str = AliasChoices("telegram_chat_id", "TELEGRAM_CHAT_ID")
    bucket: str = AliasChoices("bucket", "BUCKET")
    storage_file: str = "dates.json"
    url: str = (
        "https://bfz.hu/en/concerts-tickets/concerts-and-festivals/cocoa-concerts/"
    )


def get_config(**kwargs) -> Settings:
    return Settings(**kwargs)
