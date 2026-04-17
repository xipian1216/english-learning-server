from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.exceptions import AppError
from app.core.security import get_password_hash, verify_password
from app.db.models import User
from app.db.session import get_session
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    SessionPayload,
    UserCreateRequest,
    UserPayload,
    UserWithTokenPayload,
)
from app.schemas.common import APIResponse
from app.services.auth_service import (
    build_user_payload,
    create_session as create_session_service,
    register_user as register_user_service,
)
from app.services.user_service import get_user_profile

router = APIRouter(tags=["auth"])


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[UserWithTokenPayload],
)
def register_user(
    payload: UserCreateRequest,
    session: Session = Depends(get_session),
) -> APIResponse[UserWithTokenPayload]:
    return APIResponse(data=register_user_service(session, payload))


@router.post("/sessions", response_model=APIResponse[SessionPayload])
def create_session(
    payload: LoginRequest,
    session: Session = Depends(get_session),
) -> APIResponse[SessionPayload]:
    return APIResponse(data=create_session_service(session, payload))


@router.get("/users/me", response_model=APIResponse[UserPayload])
def get_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> APIResponse[UserPayload]:
    profile = get_user_profile(session, current_user.id)
    return APIResponse(data=build_user_payload(current_user, profile.model_dump() if profile else None))


@router.patch("/users/me/password", response_model=APIResponse[dict[str, bool]])
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> APIResponse[dict[str, bool]]:
    if not verify_password(payload.old_password, current_user.password_hash):
        raise AppError(status_code=401, code=40100, message="invalid password")

    current_user.password_hash = get_password_hash(payload.new_password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return APIResponse(data={"updated": True})
