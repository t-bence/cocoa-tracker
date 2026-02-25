import pytest
from pydantic import ValidationError
from src.config import get_config


def test_get_config_missing_required(monkeypatch):
    # Clear environment variables to test defaults
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.delenv("BUCKET", raising=False)

    with pytest.raises(ValidationError):
        get_config(_env_file=None)


def test_get_config_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat-id")
    monkeypatch.setenv("BUCKET", "test-bucket")

    config = get_config(_env_file=None)
    assert config.telegram_token == "test-token"
    assert config.telegram_chat_id == "test-chat-id"
    assert config.bucket == "test-bucket"
