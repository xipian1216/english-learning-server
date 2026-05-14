from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str | None = Field(default=None, max_length=255)
    display_name: str | None = Field(default=None, max_length=100)
    status: str = Field(default="active", max_length=20)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    profile: "UserProfile" = Relationship(back_populates="user")


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)
    english_level: str | None = Field(default=None, max_length=20)
    learning_goal: str | None = Field(default=None, max_length=255)
    preferred_explanation_language: str = Field(default="zh", max_length=20)
    teacher_style: str | None = Field(default=None, max_length=100)
    daily_target: int | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    user: User = Relationship(back_populates="profile")


class ExternalIdentity(SQLModel, table=True):
    __tablename__ = "external_identities"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    provider: str = Field(max_length=50)
    provider_subject: str = Field(max_length=255)
    email: str | None = Field(default=None, max_length=255)
    email_verified: bool = False
    raw_profile: dict | None = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class OAuthLoginCode(SQLModel, table=True):
    __tablename__ = "oauth_login_codes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    code_hash: str = Field(index=True, unique=True, max_length=255)
    user_id: UUID = Field(foreign_key="users.id")
    provider: str = Field(max_length=50)
    redirect_uri: str
    expires_at: datetime
    used_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DictionaryEntry(SQLModel, table=True):
    __tablename__ = "dictionary_entries"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lemma: str = Field(max_length=100, index=True)
    normalized_word: str = Field(max_length=100, index=True)
    display_word: str = Field(max_length=100)
    phonetic: str | None = Field(default=None, max_length=120)
    audio_url: str | None = None
    cefr_level: str | None = Field(default=None, max_length=10)
    frequency_rank: int | None = None
    source_provider: str = Field(max_length=50)
    raw_payload: dict | list | None = Field(default=None, sa_column=Column(JSONB))
    cached_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DictionarySense(SQLModel, table=True):
    __tablename__ = "dictionary_senses"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    entry_id: UUID = Field(foreign_key="dictionary_entries.id", index=True)
    part_of_speech: str = Field(max_length=50, index=True)
    definition_en: str | None = None
    definition_zh: str | None = None
    short_definition: str | None = None
    sense_order: int = 0
    created_at: datetime = Field(default_factory=utc_now)


class DictionaryExample(SQLModel, table=True):
    __tablename__ = "dictionary_examples"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    entry_id: UUID = Field(foreign_key="dictionary_entries.id", index=True)
    sense_id: UUID | None = Field(default=None, foreign_key="dictionary_senses.id", index=True)
    sentence_en: str
    sentence_zh: str | None = None
    example_order: int = 0
    created_at: datetime = Field(default_factory=utc_now)


class UserVocabularyItem(SQLModel, table=True):
    __tablename__ = "user_vocabulary_items"
    __table_args__ = (UniqueConstraint("user_id", "normalized_text", name="uq_user_vocab_user_normalized_text"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    dictionary_entry_id: UUID | None = Field(default=None, foreign_key="dictionary_entries.id")
    text: str = Field(max_length=100)
    normalized_text: str = Field(max_length=100, index=True)
    source_sentence: str | None = None
    source_url: str | None = None
    source_title: str | None = Field(default=None, max_length=255)
    note: str | None = None
    status: str = Field(default="new", max_length=20, index=True)
    lookup_status: str = Field(default="failed", max_length=20)
    familiarity_score: int | None = None
    first_added_at: datetime = Field(default_factory=utc_now)
    last_reviewed_at: datetime | None = None
    next_review_at: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
