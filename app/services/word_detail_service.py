from sqlmodel import Session

from app.core.exceptions import AppError
from app.db.models import DictionaryEntry
from app.repositories.dictionary_repository import get_cached_dictionary_entry, get_cached_examples, get_cached_senses, save_word_detail_to_cache
from app.schemas.translation import TranslationCreateRequest
from app.schemas.word_detail import (
    WordDetailCollocationPayload,
    WordDetailEntryPayload,
    WordDetailExamplePayload,
    WordDetailPayload,
    WordDetailRequest,
    WordDetailSensePayload,
    WordDetailSourcePayload,
)
from app.services.dictionary_service import lookup_word
from app.services.translation_service import translate_text


def build_word_detail(session: Session, payload: WordDetailRequest) -> WordDetailPayload:
    normalized_text = normalize_text(payload.text)
    cached_entry = get_cached_dictionary_entry(session, normalized_text)
    if cached_entry:
        return build_word_detail_from_cache(payload, normalized_text, cached_entry, session)

    dictionary_entries = lookup_word(normalized_text)
    if not dictionary_entries:
        raise AppError(status_code=404, code=40400, message="word detail not found")

    entry = dictionary_entries[0]
    translation = translate_text(
        TranslationCreateRequest(
            text=normalized_text,
            source_language=payload.source_language,
            target_language=payload.target_language,
        )
    )

    translated_examples = build_examples(entry.meanings, payload.context_sentence, payload.source_language, payload.target_language)
    senses = build_senses(entry.meanings, translation.translations)

    word_detail_entry = WordDetailEntryPayload(
        word=entry.word or normalized_text,
        phonetic=entry.phonetic,
        audio_url=next((item.audio_url for item in entry.phonetics if item.audio_url), None),
        cefr_level=None,
        senses=senses,
        examples=translated_examples,
        collocations=[],
    )
    save_word_detail_to_cache(
        session,
        normalized_text=normalized_text,
        entry_payload=word_detail_entry,
        provider="dictionaryapi+youdao",
    )

    return WordDetailPayload(
        query_text=payload.text,
        normalized_text=normalized_text,
        lemma=entry.word or normalized_text,
        source_language=payload.source_language,
        target_language=payload.target_language,
        entry=word_detail_entry,
        source=WordDetailSourcePayload(provider="dictionaryapi+youdao", cached=False),
    )


def normalize_text(text: str) -> str:
    normalized = text.strip().lower()
    if not normalized:
        raise AppError(status_code=400, code=40001, message="text is required")
    return normalized


def build_senses(meanings: list, translations: list[str]) -> list[WordDetailSensePayload]:
    joined_translation = "；".join(translations) if translations else None
    senses: list[WordDetailSensePayload] = []
    for meaning in meanings:
        if not meaning.definitions:
            continue
        first_definition = meaning.definitions[0]
        senses.append(
            WordDetailSensePayload(
                part_of_speech=meaning.part_of_speech,
                definition_en=first_definition.definition,
                definition_zh=joined_translation,
                short_definition=joined_translation,
            )
        )
    return senses


def build_examples(meanings: list, context_sentence: str | None, source_language: str, target_language: str) -> list[WordDetailExamplePayload]:
    examples: list[WordDetailExamplePayload] = []
    for meaning in meanings:
        for definition in meaning.definitions:
            if definition.example:
                examples.append(WordDetailExamplePayload(sentence_en=definition.example, sentence_zh=None))
                break
        if examples:
            break

    if context_sentence:
        translated_context = translate_text(
            TranslationCreateRequest(
                text=context_sentence,
                source_language=source_language,
                target_language=target_language,
            )
        )
        examples.insert(
            0,
            WordDetailExamplePayload(
                sentence_en=context_sentence,
                sentence_zh=translated_context.translations[0] if translated_context.translations else None,
            ),
        )

    return examples


def build_word_detail_from_cache(
    payload: WordDetailRequest,
    normalized_text: str,
    cached_entry: DictionaryEntry,
    session: Session,
) -> WordDetailPayload:
    cached_senses = get_cached_senses(session, cached_entry.id)
    cached_examples = get_cached_examples(session, cached_entry.id)
    senses = [
        WordDetailSensePayload(
            part_of_speech=sense.part_of_speech,
            definition_en=sense.definition_en,
            definition_zh=sense.definition_zh,
            short_definition=sense.short_definition,
        )
        for sense in cached_senses
    ]
    examples = [
        WordDetailExamplePayload(
            sentence_en=example.sentence_en,
            sentence_zh=example.sentence_zh,
        )
        for example in cached_examples
    ]

    return WordDetailPayload(
        query_text=payload.text,
        normalized_text=normalized_text,
        lemma=cached_entry.lemma,
        source_language=payload.source_language,
        target_language=payload.target_language,
        entry=WordDetailEntryPayload(
            word=cached_entry.display_word,
            phonetic=cached_entry.phonetic,
            audio_url=cached_entry.audio_url,
            cefr_level=cached_entry.cefr_level,
            senses=senses,
            examples=examples,
            collocations=[],
        ),
        source=WordDetailSourcePayload(provider=cached_entry.source_provider, cached=True),
    )
