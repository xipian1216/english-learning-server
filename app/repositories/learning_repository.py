from uuid import UUID

from sqlmodel import Session, select

from app.db.models import DictionaryEntry, DictionaryExample, DictionarySense, UserVocabularyItem, utc_now


def get_dictionary_entry_by_normalized_word(session: Session, normalized_word: str) -> DictionaryEntry | None:
    return session.exec(
        select(DictionaryEntry).where(DictionaryEntry.normalized_word == normalized_word).order_by(DictionaryEntry.cached_at.desc())
    ).first()


def get_entry_senses(session: Session, entry_id: UUID) -> list[DictionarySense]:
    return list(
        session.exec(select(DictionarySense).where(DictionarySense.entry_id == entry_id).order_by(DictionarySense.sense_order)).all()
    )


def get_entry_examples(session: Session, entry_id: UUID) -> list[DictionaryExample]:
    return list(
        session.exec(
            select(DictionaryExample).where(DictionaryExample.entry_id == entry_id).order_by(DictionaryExample.example_order)
        ).all()
    )


def get_user_vocabulary_item(session: Session, user_id: UUID, normalized_text: str) -> UserVocabularyItem | None:
    return session.exec(
        select(UserVocabularyItem).where(
            UserVocabularyItem.user_id == user_id,
            UserVocabularyItem.normalized_text == normalized_text,
        )
    ).first()


def list_user_vocabulary_items(session: Session, user_id: UUID) -> list[UserVocabularyItem]:
    return list(
        session.exec(
            select(UserVocabularyItem).where(UserVocabularyItem.user_id == user_id).order_by(UserVocabularyItem.created_at.desc())
        ).all()
    )


def get_user_vocabulary_item_by_id(session: Session, user_id: UUID, item_id: UUID) -> UserVocabularyItem | None:
    return session.exec(
        select(UserVocabularyItem).where(UserVocabularyItem.id == item_id, UserVocabularyItem.user_id == user_id)
    ).first()


def create_vocabulary_item(
    session: Session,
    user_id: UUID,
    text: str,
    normalized_text: str,
    dictionary_entry_id: UUID | None,
    lookup_status: str,
    source_sentence: str | None,
    source_url: str | None,
    source_title: str | None,
    note: str | None,
) -> UserVocabularyItem:
    item = UserVocabularyItem(
        user_id=user_id,
        text=text,
        normalized_text=normalized_text,
        dictionary_entry_id=dictionary_entry_id,
        lookup_status=lookup_status,
        source_sentence=source_sentence,
        source_url=source_url,
        source_title=source_title,
        note=note,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def update_vocabulary_item(
    session: Session,
    item: UserVocabularyItem,
    status: str | None,
    note: str | None,
    familiarity_score: int | None,
) -> UserVocabularyItem:
    if status is not None:
        item.status = status
    if note is not None:
        item.note = note
    if familiarity_score is not None:
        item.familiarity_score = familiarity_score
    item.updated_at = utc_now()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_vocabulary_item(session: Session, item: UserVocabularyItem) -> None:
    session.delete(item)
    session.commit()
