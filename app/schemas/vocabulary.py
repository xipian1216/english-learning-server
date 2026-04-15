from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class VocabularyItemCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100)
    source_language: str = Field(default="en", min_length=2, max_length=20)
    target_language: str = Field(default="zh-CHS", min_length=2, max_length=20)
    source_sentence: str | None = Field(default=None, max_length=2000)
    source_url: str | None = Field(default=None, max_length=2000)
    source_title: str | None = Field(default=None, max_length=255)
    note: str | None = Field(default=None, max_length=2000)


class VocabularyItemUpdateRequest(BaseModel):
    status: str | None = Field(default=None, max_length=20)
    note: str | None = Field(default=None, max_length=2000)
    familiarity_score: int | None = Field(default=None, ge=1, le=5)
    next_review_at: datetime | None = None


class VocabularyItemPayload(BaseModel):
    id: UUID
    dictionary_entry_id: UUID
    word: str
    phonetic: str | None = None
    meaning_zh: str | None = None
    status: str
    selected_text: str | None = None
    source_sentence: str | None = None
    source_url: str | None = None
    source_title: str | None = None
    note: str | None = None
    familiarity_score: int | None = None
    created_at: datetime
    updated_at: datetime

