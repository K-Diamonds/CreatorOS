from __future__ import annotations

from dataclasses import dataclass

from database import User, get_session_factory
from fastapi import HTTPException, status

from app.auth.demo_auth import demo_auth_allowed, provision_demo_user
from app.core.config import Settings
from app.core.passwords import hash_password, verify_password


@dataclass(frozen=True, slots=True)
class AuthResult:
    user: User
    auth_mode: str


class AuthError(Exception):
    pass


def register_user(*, settings: Settings, email: str, password: str, full_name: str | None = None) -> AuthResult:
    if len(password) < 8:
        raise AuthError("Password must be at least 8 characters.")

    session_factory = get_session_factory()
    with session_factory() as session:
        existing = session.query(User).filter(User.email == email).one_or_none()
        if existing is not None:
            raise AuthError("An account with this email already exists.")

        user = User(
            email=email,
            full_name=full_name,
            is_active=True,
            password_hash=hash_password(password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return AuthResult(user=user, auth_mode="password")


def authenticate_user(*, settings: Settings, email: str, password: str) -> AuthResult:
    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    session_factory = get_session_factory()
    with session_factory() as session:
        user = session.query(User).filter(User.email == email).one_or_none()

        if user is not None and user.password_hash:
            if not verify_password(password, user.password_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")
            return AuthResult(user=user, auth_mode="password")

        if demo_auth_allowed(settings):
            if user is None:
                user = provision_demo_user(session=session, email=email)
            return AuthResult(user=user, auth_mode="demo")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
