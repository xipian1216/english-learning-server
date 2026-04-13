from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings
from app.db import base  # noqa: F401

settings = get_settings()
engine = create_engine(settings.database_url, echo=settings.database_echo, pool_pre_ping=True)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

