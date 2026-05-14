from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.errors import ApiError
from app.db.models import User
from app.db.session import get_session
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    OidcSessionRequest,
    PasswordResetRequest,
    PasswordResetSubmitRequest,
    RegisterRequest,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import (
    change_password,
    login_user,
    register_user,
    serialize_user,
)


router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.post("/users", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Annotated[Session, Depends(get_session)]) -> ApiResponse:
    return ApiResponse(data=register_user(session, payload.email, payload.password, payload.display_name))


@router.post("/sessions")
def login(payload: LoginRequest, session: Annotated[Session, Depends(get_session)]) -> ApiResponse:
    return ApiResponse(data=login_user(session, payload.email, payload.password))


@router.get("/users/me")
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> ApiResponse:
    return ApiResponse(data=serialize_user(current_user))


@router.patch("/users/me/password")
def update_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> ApiResponse:
    change_password(session, current_user, payload.old_password, payload.new_password)
    return ApiResponse(data={"updated": True})


@router.post("/users/password-reset-requests", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_password_reset_request(payload: PasswordResetRequest) -> ApiResponse:
    raise ApiError(status_code=501, code=1401, message="password reset is not configured")


@router.post("/users/password-resets", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def submit_password_reset(payload: PasswordResetSubmitRequest) -> ApiResponse:
    raise ApiError(status_code=501, code=1401, message="password reset is not configured")


@router.get("/auth/oidc/{provider}/login")
def oidc_login(provider: str, request: Request, redirect_uri: str | None = Query(default=None)) -> ApiResponse:
    ensure_reserved_provider(provider)
    raise ApiError(status_code=503, code=1502, message="oidc provider is not configured")


@router.get("/auth/oidc/{provider}/callback")
def oidc_callback(provider: str, request: Request) -> ApiResponse:
    ensure_reserved_provider(provider)
    raise ApiError(status_code=503, code=1502, message="oidc provider is not configured")


@router.post("/auth/oidc/{provider}/sessions")
def oidc_session(provider: str, payload: OidcSessionRequest) -> ApiResponse:
    ensure_reserved_provider(provider)
    raise ApiError(status_code=503, code=1502, message="oidc provider is not configured")


def ensure_reserved_provider(provider: str) -> None:
    if provider != "authentik":
        raise ApiError(status_code=404, code=1501, message="oidc provider not found")
