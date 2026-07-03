"""Demo-only auth helpers — disabled in production unless DEMO_AUTH_ENABLED=true."""

from __future__ import annotations

from database import User

from app.core.config import Settings


def demo_auth_allowed(settings: Settings) -> bool:
    env = settings.environment.strip().lower()
    if env in {"production", "staging"}:
        return settings.demo_auth_enabled
    return settings.demo_auth_enabled or env in {"development", "test"}


def provision_demo_user(*, session, email: str) -> User:
    user = User(email=email, full_name=None, is_active=True, password_hash=None)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
