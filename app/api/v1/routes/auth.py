from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.exceptions import AppError
from app.core.security import create_access_token, get_password_hash, verify_password
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
from app.services.user_service import create_user, get_user_by_email, get_user_profile

router = APIRouter(tags=["auth"])


def build_user_payload(user: User, profile_data: dict | None = None) -> UserPayload:
    payload = UserPayload.model_validate(user).model_dump()
    if profile_data:
        payload.update(profile_data)
    return UserPayload.model_validate(payload)


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[UserWithTokenPayload],
)
def register_user(
    payload: UserCreateRequest,
    session: Session = Depends(get_session),
) -> APIResponse[UserWithTokenPayload]:
    existing_user = get_user_by_email(session, payload.email)
    if existing_user:
        raise AppError(status_code=409, code=40900, message="email already exists")

    user = create_user(
        session=session,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        display_name=payload.display_name,
    )
    access_token, expires_in = create_access_token(subject=str(user.id))

    return APIResponse(
        data=UserWithTokenPayload(
            user=build_user_payload(user),
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
        )
    )


@router.post("/sessions", response_model=APIResponse[SessionPayload])
def create_session(
    payload: LoginRequest,
    session: Session = Depends(get_session),
) -> APIResponse[SessionPayload]:
    user = get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppError(status_code=401, code=40100, message="invalid email or password")
    if user.status != "active":
        raise AppError(status_code=403, code=40300, message="account unavailable")

    access_token, expires_in = create_access_token(subject=str(user.id))
    return APIResponse(
        data=SessionPayload(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user=build_user_payload(user),
        )
    )


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
