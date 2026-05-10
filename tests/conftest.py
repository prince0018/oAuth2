import os

import pytest

from src.config import get_settings


DEFAULT_ENV = {
    "GOOGLE_CLIENT_ID": "test-client-id",
    "GOOGLE_CLIENT_SECRET": "test-client-secret",
    "SECRET_KEY": "test-secret-key-with-at-least-32-chars",
    "SESSION_SECRET_KEY": "test-session-secret-with-32-characters",
    "DB_NAME": "test-db",
    "DB_USER": "test-user",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
}


for key, value in DEFAULT_ENV.items():
    os.environ.setdefault(key, value)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
