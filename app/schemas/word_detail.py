from pydantic import BaseModel, Field


class WordDetailRequest(BaseModel):
    text: str = Field(min_length=1, max_length=255)
    source_language: str = Field(default="en", min_length=2, max_length=20)
    target_language: str = Field(default="zh-CHS", min_length=2, max_length=20)
    context_sentence: str | None = Field(default=None, max_length=2000)
    source_url: str | None = Field(default=None, max_length=2000)
    source_title: str | None = Field(default=None, max_length=255)


class WordDetailSensePayload(BaseModel):
    part_of_speech: str
    definition_en: str | None = None
    definition_zh: str | None = None
    short_definition: str | None = None


class WordDetailExamplePayload(BaseModel):
    sentence_en: str
    sentence_zh: str | None = None


class WordDetailCollocationPayload(BaseModel):
    phrase: str
    translation_zh: str | None = None
    note: str | None = None


class WordDetailEntryPayload(BaseModel):
    word: str
    phonetic: str | None = None
    audio_url: str | None = None
    cefr_level: str | None = None
    senses: list[WordDetailSensePayload]
    examples: list[WordDetailExamplePayload]
    collocations: list[WordDetailCollocationPayload]


class WordDetailSourcePayload(BaseModel):
    provider: str
    cached: bool = False


class WordDetailPayload(BaseModel):
    query_text: str
    normalized_text: str
    lemma: str
    source_language: str
    target_language: str
    entry: WordDetailEntryPayload
    source: WordDetailSourcePayload

