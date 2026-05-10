import pytest

from src.config import ConfigError, get_settings


def test_get_settings_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(ConfigError, match="SECRET_KEY"):
        get_settings()


def test_get_settings_rejects_invalid_db_port(monkeypatch):
    monkeypatch.setenv("DB_PORT", "not-a-port")
    get_settings.cache_clear()

    with pytest.raises(ConfigError, match="DB_PORT"):
        get_settings()


def test_get_settings_parses_cors_origins(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, https://example.com")
    get_settings.cache_clear()

    assert get_settings().cors_origins == ("http://localhost:3000", "https://example.com")


def test_get_settings_rejects_invalid_frontend_success_url(monkeypatch):
    monkeypatch.setenv("FRONTEND_SUCCESS_URL", "localhost:3000")
    get_settings.cache_clear()

    with pytest.raises(ConfigError, match="FRONTEND_SUCCESS_URL"):
        get_settings()
