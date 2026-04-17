from uuid import UUID

from sqlmodel import Session, select

from app.db.models import User, UserProfile


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: str) -> User | None:
    statement = select(User).where(User.id == UUID(user_id))
    return session.exec(statement).first()


def get_user_profile(session: Session, user_id: UUID) -> UserProfile | None:
    statement = select(UserProfile).where(UserProfile.user_id == user_id)
    return session.exec(statement).first()


def create_user(session: Session, *, email: str, password_hash: str, display_name: str | None) -> User:
    user = User(email=email, password_hash=password_hash, display_name=display_name)
    session.add(user)
    session.flush()

    profile = UserProfile(user_id=user.id)
    session.add(profile)
    session.commit()
    session.refresh(user)
    return user
