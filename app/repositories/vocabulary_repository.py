from uuid import UUID

from sqlmodel import Session, select

from app.db.models import DictionaryEntry, DictionarySense, User, UserVocabularyItem


def list_user_vocabulary_items(session: Session, user: User) -> list[tuple[UserVocabularyItem, DictionaryEntry]]:
    statement = (
        select(UserVocabularyItem, DictionaryEntry)
        .join(DictionaryEntry, DictionaryEntry.id == UserVocabularyItem.dictionary_entry_id)
        .where(UserVocabularyItem.user_id == user.id)
        .order_by(UserVocabularyItem.created_at.desc())
    )
    return session.exec(statement).all()


def get_dictionary_entry_by_normalized_word(session: Session, normalized_word: str) -> DictionaryEntry | None:
    statement = select(DictionaryEntry).where(DictionaryEntry.normalized_word == normalized_word)
    return session.exec(statement).first()


def get_existing_vocabulary_item(session: Session, user: User, dictionary_entry_id: UUID) -> UserVocabularyItem | None:
    statement = select(UserVocabularyItem).where(
        UserVocabularyItem.user_id == user.id,
        UserVocabularyItem.dictionary_entry_id == dictionary_entry_id,
    )
    return session.exec(statement).first()


def get_user_vocabulary_item(session: Session, user: User, item_id: UUID) -> UserVocabularyItem | None:
    statement = select(UserVocabularyItem).where(
        UserVocabularyItem.id == item_id,
        UserVocabularyItem.user_id == user.id,
    )
    return session.exec(statement).first()


def get_first_dictionary_sense(session: Session, entry_id: UUID) -> DictionarySense | None:
    statement = select(DictionarySense).where(DictionarySense.entry_id == entry_id).order_by(DictionarySense.sense_order)
    return session.exec(statement).first()
