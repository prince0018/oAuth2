import pytest
from fastapi import HTTPException

from src.auth import oauth_routes
from src.auth.oauth_routes import _extract_google_profile, _frontend_success_redirect


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


def test_frontend_success_redirect_uses_url_fragment(monkeypatch):
    updated_settings = oauth_routes.settings.__class__(
        **{
            **oauth_routes.settings.__dict__,
            "frontend_success_url": "http://localhost:3000/",
        }
    )
    monkeypatch.setattr(oauth_routes, "settings", updated_settings)

    response = _frontend_success_redirect("token-value", 7)

    assert response is not None
    assert response.headers["location"] == (
        "http://localhost:3000/#access_token=token-value&token_type=bearer&user_id=7"
    )
