from datetime import datetime, timedelta, timezone

import jwt

from src.auth.jwt_handler import ALGORITHM, create_token, decode_token
from src.config import get_settings


def test_create_and_decode_token_round_trip():
    token = create_token(42)
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["user_id"] == 42


def test_decode_token_returns_none_for_expired_token():
    expired_token = jwt.encode(
        {
            "sub": "42",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        get_settings().secret_key,
        algorithm=ALGORITHM,
    )

    assert decode_token(expired_token) is None
