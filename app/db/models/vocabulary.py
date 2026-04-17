from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import Column, Index, String, Text, UniqueConstraint, func
from sqlmodel import Field, Relationship

from app.db.models.base import TimestampMixin, utc_timestamp_column, utcnow


class UserVocabularyItem(TimestampMixin, table=True):
    __tablename__ = cast(Any, "user_vocabulary_items")
    __table_args__ = (
        UniqueConstraint("user_id", "dictionary_entry_id", name="uq_user_vocab_user_entry"),
        Index("ix_user_vocabulary_items_user_id", "user_id"),
        Index("ix_user_vocabulary_items_status", "status"),
        Index("ix_user_vocabulary_items_user_id_next_review_at", "user_id", "next_review_at"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    dictionary_entry_id: UUID = Field(foreign_key="dictionary_entries.id", nullable=False)
    selected_text: str | None = Field(default=None, sa_column=Column(String(100), nullable=True))
    source_sentence: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    source_url: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    source_title: str | None = Field(default=None, sa_column=Column(String(255), nullable=True))
    note: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    status: str = Field(default="new", sa_column=Column(String(20), nullable=False))
    familiarity_score: int | None = Field(default=None, nullable=True)
    first_added_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())
    last_reviewed_at: datetime | None = Field(default=None, nullable=True)
    next_review_at: datetime | None = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column(onupdate=func.now()))

    user: "User" = Relationship(back_populates="vocabulary_items")
    dictionary_entry: "DictionaryEntry" = Relationship(back_populates="vocabulary_items")
    review_records: list["ReviewRecord"] = Relationship(back_populates="vocabulary_item")
