from uuid import UUID
from typing import cast

from sqlmodel import Session

from app.core.exceptions import AppError
from app.db.models import DictionaryEntry, User, UserVocabularyItem
from app.repositories.vocabulary_repository import (
    get_dictionary_entry_by_normalized_word,
    get_existing_vocabulary_item,
    get_first_dictionary_sense,
    get_user_vocabulary_item,
    list_user_vocabulary_items as list_user_vocabulary_rows,
)
from app.schemas.vocabulary import VocabularyItemCreateRequest, VocabularyItemPayload, VocabularyItemUpdateRequest
from app.schemas.word_detail import WordDetailRequest
from app.services.word_detail_service import build_word_detail, normalize_text


def list_user_vocabulary_items(session: Session, user: User) -> list[VocabularyItemPayload]:
    rows = list_user_vocabulary_rows(session, user)
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

    existing_item = get_existing_vocabulary_item(session, user, dictionary_entry.id)

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

    item = cast(UserVocabularyItem, UserVocabularyItem(user_id=user.id, dictionary_entry_id=dictionary_entry.id))
    item.selected_text = payload.text
    item.source_sentence = payload.source_sentence
    item.source_url = payload.source_url
    item.source_title = payload.source_title
    item.note = payload.note
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
    if not item:
        raise AppError(status_code=404, code=40400, message="vocabulary item not found")
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
    if not item:
        raise AppError(status_code=404, code=40400, message="vocabulary item not found")
    session.delete(item)
    session.commit()


def build_vocabulary_payload(
    session: Session,
    item: UserVocabularyItem,
    entry: DictionaryEntry,
) -> VocabularyItemPayload:
    first_sense = get_first_dictionary_sense(session, entry.id)
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
