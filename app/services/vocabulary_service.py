from uuid import UUID

from sqlmodel import Session, select

from app.core.exceptions import AppError
from app.db.models import DictionaryEntry, DictionarySense, User, UserVocabularyItem
from app.schemas.vocabulary import VocabularyItemCreateRequest, VocabularyItemPayload, VocabularyItemUpdateRequest
from app.services.word_detail_service import build_word_detail, normalize_text
from app.schemas.word_detail import WordDetailRequest


def list_user_vocabulary_items(session: Session, user: User) -> list[VocabularyItemPayload]:
    statement = (
        select(UserVocabularyItem, DictionaryEntry)
        .join(DictionaryEntry, DictionaryEntry.id == UserVocabularyItem.dictionary_entry_id)
        .where(UserVocabularyItem.user_id == user.id)
        .order_by(UserVocabularyItem.created_at.desc())
    )
    rows = session.exec(statement).all()
    return [build_vocabulary_payload(session, item, entry) for item, entry in rows]


def create_vocabulary_item(
    session: Session,
    user: User,
    payload: VocabularyItemCreateRequest,
) -> VocabularyItemPayload:
    normalized_text = normalize_text(payload.text)
    dictionary_entry = get_dictionary_entry_by_normalized_word(session, normalized_text)
    if not dictionary_entry:
        build_word_detail(
            session,
            WordDetailRequest(
                text=payload.text,
                source_language=payload.source_language,
                target_language=payload.target_language,
                context_sentence=payload.source_sentence,
                source_url=payload.source_url,
                source_title=payload.source_title,
            ),
        )
        dictionary_entry = get_dictionary_entry_by_normalized_word(session, normalized_text)
        if not dictionary_entry:
            raise AppError(status_code=404, code=40400, message="dictionary entry not found")

    statement = select(UserVocabularyItem).where(
        UserVocabularyItem.user_id == user.id,
        UserVocabularyItem.dictionary_entry_id == dictionary_entry.id,
    )
    existing_item = session.exec(statement).first()

    if existing_item:
        existing_item.selected_text = payload.text
        existing_item.source_sentence = payload.source_sentence
        existing_item.source_url = payload.source_url
        existing_item.source_title = payload.source_title
        existing_item.note = payload.note
        session.add(existing_item)
        session.commit()
        session.refresh(existing_item)
        return build_vocabulary_payload(session, existing_item, dictionary_entry)

    item = UserVocabularyItem(
        user_id=user.id,
        dictionary_entry_id=dictionary_entry.id,
        selected_text=payload.text,
        source_sentence=payload.source_sentence,
        source_url=payload.source_url,
        source_title=payload.source_title,
        note=payload.note,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return build_vocabulary_payload(session, item, dictionary_entry)


def update_vocabulary_item(
    session: Session,
    user: User,
    item_id: UUID,
    payload: VocabularyItemUpdateRequest,
) -> VocabularyItemPayload:
    item = get_user_vocabulary_item(session, user, item_id)
    if payload.status is not None:
        item.status = payload.status
    if payload.note is not None:
        item.note = payload.note
    if payload.familiarity_score is not None:
        item.familiarity_score = payload.familiarity_score
    if payload.next_review_at is not None:
        item.next_review_at = payload.next_review_at

    session.add(item)
    session.commit()
    session.refresh(item)
    entry = session.get(DictionaryEntry, item.dictionary_entry_id)
    if not entry:
        raise AppError(status_code=404, code=40400, message="dictionary entry not found")
    return build_vocabulary_payload(session, item, entry)


def delete_vocabulary_item(session: Session, user: User, item_id: UUID) -> None:
    item = get_user_vocabulary_item(session, user, item_id)
    session.delete(item)
    session.commit()


def get_user_vocabulary_item(session: Session, user: User, item_id: UUID) -> UserVocabularyItem:
    statement = select(UserVocabularyItem).where(
        UserVocabularyItem.id == item_id,
        UserVocabularyItem.user_id == user.id,
    )
    item = session.exec(statement).first()
    if not item:
        raise AppError(status_code=404, code=40400, message="vocabulary item not found")
    return item


def get_dictionary_entry_by_normalized_word(session: Session, normalized_word: str) -> DictionaryEntry | None:
    statement = select(DictionaryEntry).where(DictionaryEntry.normalized_word == normalized_word)
    return session.exec(statement).first()


def build_vocabulary_payload(
    session: Session,
    item: UserVocabularyItem,
    entry: DictionaryEntry,
) -> VocabularyItemPayload:
    sense_statement = select(DictionarySense).where(DictionarySense.entry_id == entry.id).order_by(DictionarySense.sense_order)
    first_sense = session.exec(sense_statement).first()
    meaning_zh = None
    if first_sense:
        meaning_zh = first_sense.definition_zh or first_sense.short_definition

    return VocabularyItemPayload(
        id=item.id,
        dictionary_entry_id=entry.id,
        word=entry.display_word,
        phonetic=entry.phonetic,
        meaning_zh=meaning_zh,
        status=item.status,
        selected_text=item.selected_text,
        source_sentence=item.source_sentence,
        source_url=item.source_url,
        source_title=item.source_title,
        note=item.note,
        familiarity_score=item.familiarity_score,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
