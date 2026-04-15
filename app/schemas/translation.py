from pydantic import BaseModel, Field


class TranslationCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    source_language: str = Field(min_length=2, max_length=20)
    target_language: str = Field(min_length=2, max_length=20)
    vocab_id: str | None = Field(default=None, max_length=100)


class TranslationPayload(BaseModel):
    text: str
    source_language: str
    target_language: str
    translations: list[str]
    provider: str = "youdao"
    raw: dict | None = None

