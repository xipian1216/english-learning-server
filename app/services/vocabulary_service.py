from uuid import UUID

from sqlmodel import Session

from app.core.errors import ApiError
from app.db.models import User, UserVocabularyItem
from app.repositories.learning_repository import (
    create_vocabulary_item,
    delete_vocabulary_item,
    get_user_vocabulary_item,
    get_user_vocabulary_item_by_id,
    list_user_vocabulary_items,
    update_vocabulary_item,
)
from app.schemas.learning import VocabularyItemCreateRequest, VocabularyItemUpdateRequest, normalize_lookup_text
from app.services.word_detail_service import lookup_word_detail


def create_or_get_vocabulary_item(session: Session, user: User, payload: VocabularyItemCreateRequest) -> dict:
    normalized_text = normalize_lookup_text(payload.text)
    existing = get_user_vocabulary_item(session, user.id, normalized_text)
    if existing is not None:
        detail_result = lookup_word_detail(session, payload.text, payload.source_language, payload.target_language)
        item_data = serialize_vocabulary_item(existing)
        return {
            **item_data,
            "item": item_data,
            "word_detail": detail_result.word_detail,
            "lookup_status": existing.lookup_status,
        }

    detail_result = lookup_word_detail(
        session,
        payload.text,
        payload.source_language,
        payload.target_language,
        payload.source_sentence,
    )
    item = create_vocabulary_item(
        session=session,
        user_id=user.id,
        text=payload.text,
        normalized_text=normalized_text,
        dictionary_entry_id=detail_result.entry.id if detail_result.entry else None,
        lookup_status=detail_result.lookup_status,
        source_sentence=payload.source_sentence,
        source_url=payload.source_url,
        source_title=payload.source_title,
        note=payload.note,
    )
    item_data = serialize_vocabulary_item(item)
    return {**item_data, "item": item_data, "word_detail": detail_result.word_detail, "lookup_status": item.lookup_status}


def list_vocabulary_items(session: Session, user: User) -> list[dict]:
    return [serialize_vocabulary_item(item) for item in list_user_vocabulary_items(session, user.id)]


def patch_vocabulary_item(
    session: Session, user: User, item_id: UUID, payload: VocabularyItemUpdateRequest
) -> dict:
    item = get_user_vocabulary_item_by_id(session, user.id, item_id)
    if item is None:
        raise ApiError(status_code=404, code=4001, message="vocabulary item not found")
    item = update_vocabulary_item(session, item, payload.status, payload.note, payload.familiarity_score)
    return serialize_vocabulary_item(item)


def remove_vocabulary_item(session: Session, user: User, item_id: UUID) -> None:
    item = get_user_vocabulary_item_by_id(session, user.id, item_id)
    if item is None:
        raise ApiError(status_code=404, code=4001, message="vocabulary item not found")
    delete_vocabulary_item(session, item)


def serialize_vocabulary_item(item: UserVocabularyItem) -> dict:
    data = {
        "id": str(item.id),
        "user_id": str(item.user_id),
        "dictionary_entry_id": str(item.dictionary_entry_id) if item.dictionary_entry_id else None,
        "text": item.text,
        "word": item.text,
        "normalized_text": item.normalized_text,
        "source_sentence": item.source_sentence,
        "source_url": item.source_url,
        "source_title": item.source_title,
        "note": item.note,
        "status": item.status,
        "lookup_status": item.lookup_status,
        "familiarity_score": item.familiarity_score,
    }
    return data
