from sqlmodel import Session

from app.core.errors import ApiError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.user_repository import create_user, get_user_by_email, update_user_password


def register_user(session: Session, email: str, password: str, display_name: str | None) -> dict:
    normalized_email = email.lower()
    if get_user_by_email(session, normalized_email) is not None:
        raise ApiError(status_code=409, code=1101, message="email already exists")
    user = create_user(session, normalized_email, hash_password(password), display_name)
    return build_auth_payload(user)


def login_user(session: Session, email: str, password: str) -> dict:
    user = get_user_by_email(session, email.lower())
    if user is None or not verify_password(password, user.password_hash):
        raise ApiError(status_code=401, code=1201, message="invalid email or password")
    if user.status != "active":
        raise ApiError(status_code=403, code=1003, message="account is not active")
    return build_auth_payload(user)


def change_password(session: Session, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise ApiError(status_code=401, code=1301, message="old password is incorrect")
    update_user_password(session, user, hash_password(new_password))


def build_auth_payload(user: User) -> dict:
    token, expires_in = create_access_token(user.id)
    return {
        "user": serialize_user(user),
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


def serialize_user(user: User) -> dict:
    profile = getattr(user, "profile", None)
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
        "profile": {
            "english_level": profile.english_level if profile else None,
            "learning_goal": profile.learning_goal if profile else None,
            "preferred_explanation_language": profile.preferred_explanation_language if profile else "zh",
        },
    }
