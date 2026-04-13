from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utc_timestamp_column(*, onupdate: Any | None = None) -> Column:
    return Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=onupdate,
    )


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=utcnow, sa_column_kwargs={"nullable": False})


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


class DictionaryEntry(SQLModel, table=True):
    __tablename__ = cast(Any, "dictionary_entries")
    __table_args__ = (
        Index("ix_dictionary_entries_lemma", "lemma"),
        Index("ix_dictionary_entries_normalized_word", "normalized_word"),
        Index("ix_dictionary_entries_lemma_source_provider", "lemma", "source_provider"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lemma: str = Field(sa_column=Column(String(100), nullable=False))
    normalized_word: str = Field(sa_column=Column(String(100), nullable=False))
    display_word: str = Field(sa_column=Column(String(100), nullable=False))
    phonetic: str | None = Field(default=None, sa_column=Column(String(120), nullable=True))
    audio_url: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    cefr_level: str | None = Field(default=None, sa_column=Column(String(10), nullable=True))
    frequency_rank: int | None = Field(default=None, nullable=True)
    source_provider: str = Field(sa_column=Column(String(50), nullable=False))
    raw_payload: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB, nullable=True))
    cached_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column(onupdate=func.now()))

    senses: list["DictionarySense"] = Relationship(back_populates="entry")
    examples: list["DictionaryExample"] = Relationship(back_populates="entry")
    collocations: list["DictionaryCollocation"] = Relationship(back_populates="entry")
    vocabulary_items: list["UserVocabularyItem"] = Relationship(back_populates="dictionary_entry")


class DictionarySense(SQLModel, table=True):
    __tablename__ = cast(Any, "dictionary_senses")
    __table_args__ = (
        Index("ix_dictionary_senses_entry_id", "entry_id"),
        Index("ix_dictionary_senses_part_of_speech", "part_of_speech"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    entry_id: UUID = Field(foreign_key="dictionary_entries.id", nullable=False)
    part_of_speech: str = Field(sa_column=Column(String(50), nullable=False))
    definition_en: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    definition_zh: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    short_definition: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    sense_order: int = Field(default=1, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())

    entry: "DictionaryEntry" = Relationship(back_populates="senses")
    examples: list["DictionaryExample"] = Relationship(back_populates="sense")


class DictionaryExample(SQLModel, table=True):
    __tablename__ = cast(Any, "dictionary_examples")
    __table_args__ = (
        Index("ix_dictionary_examples_entry_id", "entry_id"),
        Index("ix_dictionary_examples_sense_id", "sense_id"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    entry_id: UUID = Field(foreign_key="dictionary_entries.id", nullable=False)
    sense_id: UUID | None = Field(default=None, foreign_key="dictionary_senses.id")
    sentence_en: str = Field(sa_column=Column(Text, nullable=False))
    sentence_zh: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    example_order: int = Field(default=1, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())

    entry: "DictionaryEntry" = Relationship(back_populates="examples")
    sense: "DictionarySense" = Relationship(back_populates="examples")


class DictionaryCollocation(SQLModel, table=True):
    __tablename__ = cast(Any, "dictionary_collocations")
    __table_args__ = (
        Index("ix_dictionary_collocations_entry_id", "entry_id"),
        Index("ix_dictionary_collocations_phrase", "phrase"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    entry_id: UUID = Field(foreign_key="dictionary_entries.id", nullable=False)
    phrase: str = Field(sa_column=Column(String(255), nullable=False))
    translation_zh: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    note: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    collocation_type: str | None = Field(default=None, sa_column=Column(String(50), nullable=True))
    sort_order: int = Field(default=1, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_timestamp_column())

    entry: "DictionaryEntry" = Relationship(back_populates="collocations")


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
