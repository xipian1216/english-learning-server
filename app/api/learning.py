from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.errors import ApiError
from app.db.models import User
from app.db.session import get_session
from app.schemas.common import ApiResponse
from app.schemas.learning import VocabularyItemCreateRequest, VocabularyItemUpdateRequest, WordDetailRequest
from app.services.dictionary_service import lookup_entries
from app.services.translation_service import create_translation
from app.services.vocabulary_service import (
    create_or_get_vocabulary_item,
    list_vocabulary_items,
    patch_vocabulary_item,
    remove_vocabulary_item,
)
from app.services.word_detail_service import lookup_word_detail


router = APIRouter(prefix="/api/v1", tags=["learning"])


@router.get("/dictionary/entries/{word}")
def get_dictionary_entries(word: str) -> ApiResponse:
    if not word.strip():
        raise ApiError(status_code=400, code=2001, message="word is required")
    return ApiResponse(data=lookup_entries(word.strip()))


@router.post("/translations")
def post_translation(payload: WordDetailRequest) -> ApiResponse:
    return ApiResponse(data=create_translation(payload.text, payload.source_language, payload.target_language))


@router.post("/word-details")
def post_word_detail(
    payload: WordDetailRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> ApiResponse:
    result = lookup_word_detail(
        session,
        payload.text,
        payload.source_language,
        payload.target_language,
        payload.context_sentence,
    )
    if result.lookup_status == "failed":
        raise ApiError(status_code=503, code=3201, message="word detail providers unavailable")
    data = result.word_detail or {"query_text": payload.text, "entry": None}
    data["lookup_status"] = result.lookup_status
    data["cache_status"] = result.cache_status
    return ApiResponse(data=data)


@router.get("/vocabulary-items")
def get_vocabulary_items(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> ApiResponse:
    return ApiResponse(data=list_vocabulary_items(session, current_user))


@router.post("/vocabulary-items", status_code=status.HTTP_201_CREATED)
def post_vocabulary_item(
    payload: VocabularyItemCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> ApiResponse:
    return ApiResponse(data=create_or_get_vocabulary_item(session, current_user, payload))


@router.patch("/vocabulary-items/{item_id}")
def patch_vocabulary_item_route(
    item_id: UUID,
    payload: VocabularyItemUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> ApiResponse:
    return ApiResponse(data=patch_vocabulary_item(session, current_user, item_id, payload))


@router.delete("/vocabulary-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vocabulary_item_route(
    item_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    remove_vocabulary_item(session, current_user, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
