from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import Column, Index, String
from sqlmodel import Field, Relationship, SQLModel

from app.db.models.base import utc_timestamp_column, utcnow


class ReviewRecord(SQLModel, table=True):
    __tablename__ = cast(Any, "review_records")
    __table_args__ = (
        Index("ix_review_records_user_id", "user_id"),
        Index("ix_review_records_vocabulary_item_id", "vocabulary_item_id"),
        Index("ix_review_records_user_id_reviewed_at", "user_id", "reviewed_at"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    vocabulary_item_id: UUID = Field(foreign_key="user_vocabulary_items.id", nullable=False)
    result: str = Field(sa_column=Column(String(20), nullable=False))
    score: int | None = Field(default=None, nullable=True)
    reviewed_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())
    next_review_at: datetime | None = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())

    user: "User" = Relationship(back_populates="review_records")
    vocabulary_item: "UserVocabularyItem" = Relationship(back_populates="review_records")
