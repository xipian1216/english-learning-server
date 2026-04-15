from sqlmodel import Session, delete, select

from app.db.models import DictionaryEntry, DictionaryExample, DictionarySense
from app.schemas.word_detail import WordDetailEntryPayload


def get_cached_dictionary_entry(session: Session, normalized_text: str) -> DictionaryEntry | None:
    statement = select(DictionaryEntry).where(DictionaryEntry.normalized_word == normalized_text)
    return session.exec(statement).first()


def save_word_detail_to_cache(
    session: Session,
    *,
    normalized_text: str,
    entry_payload: WordDetailEntryPayload,
    provider: str,
) -> DictionaryEntry:
    dictionary_entry = get_cached_dictionary_entry(session, normalized_text)
    if dictionary_entry is None:
        dictionary_entry = DictionaryEntry(
            lemma=entry_payload.word,
            normalized_word=normalized_text,
            display_word=entry_payload.word,
            phonetic=entry_payload.phonetic,
            audio_url=entry_payload.audio_url,
            cefr_level=entry_payload.cefr_level,
            source_provider=provider,
            raw_payload=None,
        )
        session.add(dictionary_entry)
        session.commit()
        session.refresh(dictionary_entry)
    else:
        dictionary_entry.lemma = entry_payload.word
        dictionary_entry.display_word = entry_payload.word
        dictionary_entry.phonetic = entry_payload.phonetic
        dictionary_entry.audio_url = entry_payload.audio_url
        dictionary_entry.cefr_level = entry_payload.cefr_level
        dictionary_entry.source_provider = provider
        session.add(dictionary_entry)
        session.commit()
        session.refresh(dictionary_entry)

    replace_senses(session, dictionary_entry.id, entry_payload.senses)
    replace_examples(session, dictionary_entry.id, entry_payload.examples)
    return dictionary_entry


def replace_senses(session: Session, entry_id, senses) -> None:
    session.exec(delete(DictionarySense).where(DictionarySense.entry_id == entry_id))
    session.commit()

    for index, sense in enumerate(senses, start=1):
        session.add(
            DictionarySense(
                entry_id=entry_id,
                part_of_speech=sense.part_of_speech,
                definition_en=sense.definition_en,
                definition_zh=sense.definition_zh,
                short_definition=sense.short_definition,
                sense_order=index,
            )
        )
    session.commit()


def replace_examples(session: Session, entry_id, examples) -> None:
    session.exec(delete(DictionaryExample).where(DictionaryExample.entry_id == entry_id))
    session.commit()

    for index, example in enumerate(examples, start=1):
        session.add(
            DictionaryExample(
                entry_id=entry_id,
                sentence_en=example.sentence_en,
                sentence_zh=example.sentence_zh,
                example_order=index,
            )
        )
    session.commit()

