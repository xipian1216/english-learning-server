from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.errors import ApiError
from app.db.models import User, UserProfile, utc_now


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email.lower())).first()


def get_user_by_id(session: Session, user_id: UUID) -> User | None:
    return session.get(User, user_id)


def create_user(session: Session, email: str, password_hash: str, display_name: str | None) -> User:
    user = User(email=email.lower(), password_hash=password_hash, display_name=display_name, status="active")
    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise ApiError(status_code=409, code=1101, message="email already exists") from exc
    session.refresh(user)

    profile = UserProfile(user_id=user.id)
    session.add(profile)
    session.commit()
    session.refresh(user)
    return user


def update_user_password(session: Session, user: User, password_hash: str) -> None:
    user.password_hash = password_hash
    user.updated_at = utc_now()
    session.add(user)
    session.commit()
