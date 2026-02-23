from src.config import get_config


def test_get_config_defaults(monkeypatch):
    # Clear environment variables to test defaults
    monkeypatch.delenv("SNS_TOPIC_ARN", raising=False)
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.delenv("BUCKET", raising=False)

    config = get_config()
    assert config.sns_topic_arn == ""
    assert config.telegram_token == ""
    assert config.telegram_chat_id == ""
    assert config.bucket == ""
    assert config.storage_file == "dates.json"
    assert "bfz.hu" in config.url


def test_get_config_from_env(monkeypatch):
    monkeypatch.setenv("SNS_TOPIC_ARN", "test-arn")
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat-id")
    monkeypatch.setenv("BUCKET", "test-bucket")

    config = get_config()
    assert config.sns_topic_arn == "test-arn"
    assert config.telegram_token == "test-token"
    assert config.telegram_chat_id == "test-chat-id"
    assert config.bucket == "test-bucket"
