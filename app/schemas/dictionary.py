from pydantic import BaseModel


class DictionaryPhoneticPayload(BaseModel):
    text: str | None = None
    audio_url: str | None = None


class DictionaryDefinitionPayload(BaseModel):
    definition: str
    example: str | None = None


class DictionaryMeaningPayload(BaseModel):
    part_of_speech: str
    definitions: list[DictionaryDefinitionPayload]


class DictionaryEntryPayload(BaseModel):
    word: str
    phonetic: str | None = None
    phonetics: list[DictionaryPhoneticPayload]
    meanings: list[DictionaryMeaningPayload]
    source_urls: list[str]

