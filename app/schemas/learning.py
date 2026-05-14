from uuid import UUID

from pydantic import BaseModel, Field, field_validator


def normalize_lookup_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


class DictionaryEntryResponse(BaseModel):
    id: UUID | None = None
    word: str
    normalized_word: str | None = None
    phonetic: str | None = None
    audio_url: str | None = None
    senses: list[dict] = Field(default_factory=list)
    examples: list[dict] = Field(default_factory=list)
    source_provider: str | None = None


class WordDetailRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100)
    source_language: str = Field(default="en", max_length=20)
    target_language: str = Field(default="zh-CHS", max_length=20)
    context_sentence: str | None = Field(default=None, max_length=2000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = normalize_lookup_text(value)
        if not normalized:
            raise ValueError("text is required")
        return value.strip()


class VocabularyItemCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100)
    source_sentence: str | None = Field(default=None, max_length=2000)
    source_url: str | None = Field(default=None, max_length=2000)
    source_title: str | None = Field(default=None, max_length=255)
    note: str | None = Field(default=None, max_length=2000)
    source_language: str = Field(default="en", max_length=20)
    target_language: str = Field(default="zh-CHS", max_length=20)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = normalize_lookup_text(value)
        if not normalized:
            raise ValueError("text is required")
        return value.strip()


class VocabularyItemUpdateRequest(BaseModel):
    status: str | None = Field(default=None, max_length=20)
    note: str | None = Field(default=None, max_length=2000)
    familiarity_score: int | None = Field(default=None, ge=0, le=5)
