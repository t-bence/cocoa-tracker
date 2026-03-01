import pytest
from src.common.config import get_config, ConfigError


def test_get_config_missing_required(monkeypatch):
    # Clear environment variables to test defaults
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.delenv("BUCKET", raising=False)
    monkeypatch.delenv("IOT_THING_NAME", raising=False)

    with pytest.raises(ConfigError):
        get_config(env_file=None)


def test_get_config_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat-id")
    monkeypatch.setenv("BUCKET", "test-bucket")
    monkeypatch.setenv("IOT_THING_NAME", "test-thing")
    monkeypatch.setenv("IOT_SHADOW_NAME", "test-shadow")

    # Pass env_file=None to avoid loading the real .env which would be skipped anyway due to monkeypatch
    config = get_config(env_file=None)
    assert config.telegram_token == "test-token"
    assert config.telegram_chat_id == "test-chat-id"
    assert config.bucket == "test-bucket"
    assert config.iot_thing_name == "test-thing"
    assert config.iot_shadow_name == "test-shadow"
