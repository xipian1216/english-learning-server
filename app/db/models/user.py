from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import Column, String, UniqueConstraint, func
from sqlmodel import Field, Relationship

from app.db.models.base import TimestampMixin, utc_timestamp_column, utcnow


class User(TimestampMixin, table=True):
    __tablename__ = cast(Any, "users")

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(String(255), nullable=False, unique=True, index=True))
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    display_name: str | None = Field(default=None, sa_column=Column(String(100), nullable=True))
    status: str = Field(default="active", sa_column=Column(String(20), nullable=False))
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column(onupdate=func.now()))

    profile: "UserProfile" = Relationship(back_populates="user")
    vocabulary_items: list["UserVocabularyItem"] = Relationship(back_populates="user")
    review_records: list["ReviewRecord"] = Relationship(back_populates="user")
    ai_sessions: list["AISession"] = Relationship(back_populates="user")


class UserProfile(TimestampMixin, table=True):
    __tablename__ = cast(Any, "user_profiles")
    __table_args__ = (UniqueConstraint("user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, unique=True)
    english_level: str | None = Field(default=None, sa_column=Column(String(20), nullable=True))
    learning_goal: str | None = Field(default=None, sa_column=Column(String(255), nullable=True))
    preferred_explanation_language: str = Field(
        default="zh-CN", sa_column=Column(String(20), nullable=False)
    )
    teacher_style: str | None = Field(default=None, sa_column=Column(String(100), nullable=True))
    daily_target: int | None = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column(onupdate=func.now()))

    user: "User" = Relationship(back_populates="profile")
