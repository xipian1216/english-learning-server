from dataclasses import dataclass

from sqlmodel import Session

from app.clients.dictionary_api_client import lookup_dictionary_entries
from app.clients.youdao_client import translate_text
from app.db.models import DictionaryEntry, DictionaryExample, DictionarySense, utc_now
from app.repositories.learning_repository import get_dictionary_entry_by_normalized_word, get_entry_examples, get_entry_senses
from app.schemas.learning import normalize_lookup_text


@dataclass
class LookupResult:
    word_detail: dict | None
    lookup_status: str
    cache_status: str
    entry: DictionaryEntry | None


def lookup_word_detail(
    session: Session,
    text: str,
    source_language: str = "en",
    target_language: str = "zh-CHS",
    context_sentence: str | None = None,
) -> LookupResult:
    normalized_text = normalize_lookup_text(text)
    cached_entry = get_dictionary_entry_by_normalized_word(session, normalized_text)
    if cached_entry is not None:
        return LookupResult(
            word_detail=serialize_word_detail(session, cached_entry, text),
            lookup_status="success",
            cache_status="hit",
            entry=cached_entry,
        )

    dictionary_payload: list[dict] | None = None
    translation_payload: dict | None = None
    sentence_translation_payload: dict | None = None
    dictionary_failed = False
    translation_failed = False

    try:
        dictionary_payload = lookup_dictionary_entries(normalized_text)
    except Exception:
        dictionary_failed = True

    try:
        translation_payload = translate_text(text, source_language, target_language)
    except Exception:
        translation_failed = True

    if context_sentence:
        try:
            sentence_translation_payload = translate_text(context_sentence, source_language, target_language)
        except Exception:
            pass

    if dictionary_failed and translation_failed:
        return LookupResult(
            word_detail={"query_text": text, "entry": None},
            lookup_status="failed",
            cache_status="miss",
            entry=None,
        )

    entry = persist_dictionary_result(session, text, normalized_text, dictionary_payload, translation_payload, sentence_translation_payload)
    lookup_status = "success" if not dictionary_failed and not translation_failed else "partial_failed"
    return LookupResult(
        word_detail=serialize_word_detail(session, entry, text),
        lookup_status=lookup_status,
        cache_status="miss",
        entry=entry,
    )


def persist_dictionary_result(
    session: Session,
    text: str,
    normalized_text: str,
    dictionary_payload: list[dict] | None,
    translation_payload: dict | None,
    sentence_translation_payload: dict | None,
) -> DictionaryEntry:
    first_entry = dictionary_payload[0] if dictionary_payload else {}
    display_word = first_entry.get("word") or text
    phonetics = first_entry.get("phonetics") or []
    audio_url = next((item.get("audio") for item in phonetics if item.get("audio")), None)
    phonetic = first_entry.get("phonetic") or next((item.get("text") for item in phonetics if item.get("text")), None)
    entry = DictionaryEntry(
        lemma=normalized_text,
        normalized_word=normalized_text,
        display_word=display_word,
        phonetic=phonetic,
        audio_url=audio_url,
        source_provider="dictionaryapi+youdao" if dictionary_payload and translation_payload else "partial",
        raw_payload={"dictionary": dictionary_payload, "translation": translation_payload},
        cached_at=utc_now(),
        updated_at=utc_now(),
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)

    translations = translation_payload.get("translation") if translation_payload else None
    definition_zh = "；".join(translations) if translations else None
    example_translation = None
    if sentence_translation_payload and sentence_translation_payload.get("translation"):
        example_translation = sentence_translation_payload["translation"][0]

    sense_order = 0
    example_order = 0
    for provider_entry in dictionary_payload or []:
        for meaning in provider_entry.get("meanings") or []:
            part_of_speech = meaning.get("partOfSpeech") or "unknown"
            for definition in meaning.get("definitions") or []:
                sense = DictionarySense(
                    entry_id=entry.id,
                    part_of_speech=part_of_speech,
                    definition_en=definition.get("definition"),
                    definition_zh=definition_zh,
                    short_definition=definition_zh or definition.get("definition"),
                    sense_order=sense_order,
                )
                session.add(sense)
                session.commit()
                session.refresh(sense)
                if definition.get("example"):
                    example = DictionaryExample(
                        entry_id=entry.id,
                        sense_id=sense.id,
                        sentence_en=definition["example"],
                        sentence_zh=example_translation,
                        example_order=example_order,
                    )
                    session.add(example)
                    example_order += 1
                sense_order += 1

    if not dictionary_payload and definition_zh:
        session.add(
            DictionarySense(
                entry_id=entry.id,
                part_of_speech="unknown",
                definition_zh=definition_zh,
                short_definition=definition_zh,
                sense_order=0,
            )
        )
    session.commit()
    session.refresh(entry)
    return entry


def serialize_word_detail(session: Session, entry: DictionaryEntry, query_text: str) -> dict:
    senses = get_entry_senses(session, entry.id)
    examples = get_entry_examples(session, entry.id)
    return {
        "query_text": query_text,
        "entry": {
            "id": str(entry.id),
            "word": entry.display_word,
            "normalized_word": entry.normalized_word,
            "phonetic": entry.phonetic,
            "audio_url": entry.audio_url,
            "source_provider": entry.source_provider,
            "senses": [
                {
                    "id": str(sense.id),
                    "part_of_speech": sense.part_of_speech,
                    "definition_en": sense.definition_en,
                    "definition_zh": sense.definition_zh,
                    "short_definition": sense.short_definition,
                }
                for sense in senses
            ],
            "examples": [
                {
                    "id": str(example.id),
                    "sentence_en": example.sentence_en,
                    "sentence_zh": example.sentence_zh,
                }
                for example in examples
            ],
        },
    }
