from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import Column, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.db.models.base import utc_timestamp_column, utcnow


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
