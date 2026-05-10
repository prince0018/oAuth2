import pytest

from src.db.users import get_or_create_user, get_user_by_id


def test_get_or_create_user_requires_email():
    with pytest.raises(ValueError, match="email"):
        get_or_create_user("", "Example User", "google-subject")


def test_get_or_create_user_requires_google_id():
    with pytest.raises(ValueError, match="stable user id"):
        get_or_create_user("user@example.com", "Example User", "")


def test_get_user_by_id_returns_none_for_empty_id():
    assert get_user_by_id(None) is None
