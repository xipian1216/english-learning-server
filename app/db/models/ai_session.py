from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import Column, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.db.models.base import TimestampMixin, utc_timestamp_column, utcnow


class AISession(TimestampMixin, table=True):
    __tablename__ = cast(Any, "ai_sessions")
    __table_args__ = (
        Index("ix_ai_sessions_user_id", "user_id"),
        Index("ix_ai_sessions_user_id_updated_at", "user_id", "updated_at"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    title: str | None = Field(default=None, sa_column=Column(String(255), nullable=True))
    session_type: str = Field(default="teacher_chat", sa_column=Column(String(50), nullable=False))
    current_context: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column(onupdate=func.now()))

    user: "User" = Relationship(back_populates="ai_sessions")
    messages: list["AIMessage"] = Relationship(back_populates="session")


class AIMessage(SQLModel, table=True):
    __tablename__ = cast(Any, "ai_messages")
    __table_args__ = (
        Index("ix_ai_messages_session_id", "session_id"),
        Index("ix_ai_messages_session_id_created_at", "session_id", "created_at"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="ai_sessions.id", nullable=False)
    role: str = Field(sa_column=Column(String(20), nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    message_metadata: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column("metadata", JSONB, nullable=True),
    )
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())

    session: "AISession" = Relationship(back_populates="messages")
