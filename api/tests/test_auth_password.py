import pytest

from app.auth.service import authenticate_user, register_user
from app.core.config import get_settings


def test_register_and_login_with_password(sqlite_session_factory, monkeypatch) -> None:
    monkeypatch.setattr("app.auth.service.get_session_factory", lambda: sqlite_session_factory)
    monkeypatch.setenv("DEMO_AUTH_ENABLED", "false")
    get_settings.cache_clear()
    settings = get_settings()

    registered = register_user(
        settings=settings,
        email="creator@example.com",
        password="securepass1",
        full_name="Creator",
    )
    assert registered.auth_mode == "password"

    result = authenticate_user(
        settings=settings,
        email="creator@example.com",
        password="securepass1",
    )
    assert result.user.email == "creator@example.com"
    assert result.auth_mode == "password"


def test_demo_auth_only_when_enabled(sqlite_session_factory, monkeypatch) -> None:
    monkeypatch.setattr("app.auth.service.get_session_factory", lambda: sqlite_session_factory)
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DEMO_AUTH_ENABLED", "true")
    get_settings.cache_clear()
    settings = get_settings()

    result = authenticate_user(
        settings=settings,
        email="newdemo@example.com",
        password="demopass1",
    )
    assert result.auth_mode == "demo"
