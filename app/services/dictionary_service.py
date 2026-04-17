from app.core.config import get_settings
from app.clients.dictionary_api_client import fetch_dictionary_entries
from app.schemas.dictionary import (
    DictionaryDefinitionPayload,
    DictionaryEntryPayload,
    DictionaryMeaningPayload,
    DictionaryPhoneticPayload,
)


def lookup_word(word: str) -> list[DictionaryEntryPayload]:
    normalized_word = word.strip().lower()
    if not normalized_word:
        from app.core.exceptions import AppError

        raise AppError(status_code=400, code=40001, message="word is required")

    settings = get_settings()
    payload = fetch_dictionary_entries(settings.dictionary_api_base_url, normalized_word)
    return [build_dictionary_entry(item) for item in payload]


def build_dictionary_entry(item: dict) -> DictionaryEntryPayload:
    phonetics = []
    for phonetic in item.get("phonetics", []):
        if not isinstance(phonetic, dict):
            continue
        phonetics.append(
            DictionaryPhoneticPayload(
                text=phonetic.get("text"),
                audio_url=phonetic.get("audio") or None,
            )
        )

    meanings = []
    for meaning in item.get("meanings", []):
        if not isinstance(meaning, dict):
            continue
        definitions = []
        for definition in meaning.get("definitions", []):
            if not isinstance(definition, dict) or not definition.get("definition"):
                continue
            definitions.append(
                DictionaryDefinitionPayload(
                    definition=definition["definition"],
                    example=definition.get("example"),
                )
            )
        if definitions and meaning.get("partOfSpeech"):
            meanings.append(
                DictionaryMeaningPayload(
                    part_of_speech=meaning["partOfSpeech"],
                    definitions=definitions,
                )
            )

    return DictionaryEntryPayload(
        word=item.get("word", ""),
        phonetic=item.get("phonetic"),
        phonetics=phonetics,
        meanings=meanings,
        source_urls=[url for url in item.get("sourceUrls", []) if isinstance(url, str)],
    )
