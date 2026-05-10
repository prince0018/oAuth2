import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv


load_dotenv()


class ConfigError(RuntimeError):
    """Raised when required application configuration is missing or invalid."""


def _env(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    value = os.getenv(name, default)
    if isinstance(value, str):
        value = value.strip()
    if required and not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def _bool_env(name: str, default: bool = False) -> bool:
    value = _env(name)
    if value is None or value == "":
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _csv_env(name: str) -> tuple[str, ...]:
    value = _env(name, "")
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _require_min_length(name: str, value: str, minimum: int = 32) -> str:
    if len(value) < minimum:
        raise ConfigError(f"{name} must be at least {minimum} characters long")
    return value


def _optional_url(name: str) -> Optional[str]:
    value = _env(name)
    if not value:
        return None

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConfigError(f"{name} must be a valid http or https URL")
    return value


@dataclass(frozen=True)
class Settings:
    google_client_id: str
    google_client_secret: str
    secret_key: str
    session_secret_key: str
    db_name: str
    db_user: str
    db_password: Optional[str]
    db_host: str
    db_port: int
    cors_origins: tuple[str, ...]
    session_cookie_secure: bool
    session_cookie_samesite: str
    frontend_success_url: Optional[str]


@lru_cache
def get_settings() -> Settings:
    db_port_raw = _env("DB_PORT", "5432")
    try:
        db_port = int(db_port_raw or "5432")
    except ValueError as exc:
        raise ConfigError("DB_PORT must be a valid integer") from exc

    secret_key = _require_min_length("SECRET_KEY", _env("SECRET_KEY", required=True))
    session_secret_key = _require_min_length(
        "SESSION_SECRET_KEY",
        _env("SESSION_SECRET_KEY", secret_key, required=True),
    )
    session_cookie_samesite = (_env("SESSION_COOKIE_SAMESITE", "lax", required=True) or "lax").lower()
    if session_cookie_samesite not in {"lax", "strict", "none"}:
        raise ConfigError("SESSION_COOKIE_SAMESITE must be one of: lax, strict, none")

    return Settings(
        google_client_id=_env("GOOGLE_CLIENT_ID", required=True),
        google_client_secret=_env("GOOGLE_CLIENT_SECRET", required=True),
        secret_key=secret_key,
        session_secret_key=session_secret_key,
        db_name=_env("DB_NAME", required=True),
        db_user=_env("DB_USER", required=True),
        db_password=_env("DB_PASSWORD"),
        db_host=_env("DB_HOST", "localhost", required=True),
        db_port=db_port,
        cors_origins=_csv_env("CORS_ORIGINS"),
        session_cookie_secure=_bool_env("SESSION_COOKIE_SECURE", False),
        session_cookie_samesite=session_cookie_samesite,
        frontend_success_url=_optional_url("FRONTEND_SUCCESS_URL"),
    )
