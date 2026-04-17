from app.core.exceptions import AppError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models import User
from app.repositories.user_repository import create_user, get_user_by_email
from app.schemas.auth import LoginRequest, SessionPayload, UserCreateRequest, UserPayload, UserWithTokenPayload
from sqlmodel import Session


def build_user_payload(user: User, profile_data: dict | None = None) -> UserPayload:
    payload = UserPayload.model_validate(user).model_dump()
    if profile_data:
        payload.update(profile_data)
    return UserPayload.model_validate(payload)


def register_user(session: Session, payload: UserCreateRequest) -> UserWithTokenPayload:
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
    return UserWithTokenPayload(
        user=build_user_payload(user),
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )


def create_session(session: Session, payload: LoginRequest) -> SessionPayload:
    user = get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppError(status_code=401, code=40100, message="invalid email or password")
    if user.status != "active":
        raise AppError(status_code=403, code=40300, message="account unavailable")

    access_token, expires_in = create_access_token(subject=str(user.id))
    return SessionPayload(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=build_user_payload(user),
    )
