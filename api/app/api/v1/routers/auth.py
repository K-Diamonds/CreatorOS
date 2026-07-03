from fastapi import APIRouter, HTTPException, Response, status

from app.auth.service import AuthError, authenticate_user, register_user
from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.auth import AuthRegisterRequest, AuthTokenRequest, AuthTokenResponse

router = APIRouter(prefix="/auth")

from app.auth.constants import AUTH_COOKIE_NAME

def _attach_auth_cookie(*, response: Response, token: str, settings) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.environment.lower() in {"production", "staging"},
        samesite="lax",
        max_age=settings.auth_access_token_exp_minutes * 60,
        path="/",
    )


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: AuthRegisterRequest, response: Response) -> AuthTokenResponse:
    settings = get_settings()
    try:
        result = register_user(
            settings=settings,
            email=str(payload.email),
            password=payload.password,
            full_name=payload.full_name,
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    token = create_access_token(subject=result.user.id, email=result.user.email)
    _attach_auth_cookie(response=response, token=token, settings=settings)
    return AuthTokenResponse(
        access_token=token,
        expires_in_seconds=settings.auth_access_token_exp_minutes * 60,
        user_id=result.user.id,
        auth_mode=result.auth_mode,
    )


@router.post("/token", response_model=AuthTokenResponse)
def issue_access_token(payload: AuthTokenRequest, response: Response) -> AuthTokenResponse:
    settings = get_settings()
    result = authenticate_user(settings=settings, email=str(payload.email), password=payload.password)
    token = create_access_token(subject=result.user.id, email=result.user.email)
    _attach_auth_cookie(response=response, token=token, settings=settings)
    return AuthTokenResponse(
        access_token=token,
        expires_in_seconds=settings.auth_access_token_exp_minutes * 60,
        user_id=result.user.id,
        auth_mode=result.auth_mode,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(key=AUTH_COOKIE_NAME, path="/")
