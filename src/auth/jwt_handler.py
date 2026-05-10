import jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from src.config import get_settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_token(user_id: int) -> str:
    """Create JWT access token for user."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "exp": now + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": now,
    }
    return jwt.encode(payload, get_settings().secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate JWT token. Returns payload or None if invalid."""
    try:
        return jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
