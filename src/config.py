import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    sns_topic_arn: str
    telegram_token: str
    telegram_chat_id: str
    bucket: str
    storage_file: str = "dates.json"
    url: str = (
        "https://bfz.hu/en/concerts-tickets/concerts-and-festivals/cocoa-concerts/"
    )


def get_config() -> Config:
    return Config(
        sns_topic_arn=os.environ.get("SNS_TOPIC_ARN", ""),
        telegram_token=os.environ.get("TELEGRAM_TOKEN", ""),
        telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
        bucket=os.environ.get("BUCKET", ""),
    )
