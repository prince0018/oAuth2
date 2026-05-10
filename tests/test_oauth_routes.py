import pytest
from fastapi import HTTPException

from src.auth.oauth_routes import _extract_google_profile


def test_extract_google_profile_accepts_verified_profile():
    email, username, google_id = _extract_google_profile(
        {
            "email": "User@Example.com",
            "email_verified": True,
            "name": "Example User",
            "sub": "google-subject",
        }
    )

    assert email == "User@Example.com"
    assert username == "Example User"
    assert google_id == "google-subject"


def test_extract_google_profile_requires_verified_email():
    with pytest.raises(HTTPException) as exc:
        _extract_google_profile(
            {
                "email": "user@example.com",
                "email_verified": False,
                "sub": "google-subject",
            }
        )

    assert exc.value.status_code == 403


def test_extract_google_profile_requires_email_and_google_id():
    with pytest.raises(HTTPException) as exc:
        _extract_google_profile({"email_verified": True})

    assert exc.value.status_code == 400
