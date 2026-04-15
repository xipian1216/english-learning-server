from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_session
from app.schemas.common import APIResponse
from app.schemas.vocabulary import VocabularyItemCreateRequest, VocabularyItemPayload, VocabularyItemUpdateRequest
from app.services.vocabulary_service import (
    create_vocabulary_item,
    delete_vocabulary_item,
    list_user_vocabulary_items,
    update_vocabulary_item,
)

router = APIRouter(tags=["vocabulary"])


@router.get("/vocabulary-items", response_model=APIResponse[list[VocabularyItemPayload]])
def get_vocabulary_items(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> APIResponse[list[VocabularyItemPayload]]:
    return APIResponse(data=list_user_vocabulary_items(session, current_user))


@router.post(
    "/vocabulary-items",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[VocabularyItemPayload],
)
def create_vocabulary(
    payload: VocabularyItemCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> APIResponse[VocabularyItemPayload]:
    return APIResponse(data=create_vocabulary_item(session, current_user, payload))


@router.patch("/vocabulary-items/{item_id}", response_model=APIResponse[VocabularyItemPayload])
def update_vocabulary(
    item_id: UUID,
    payload: VocabularyItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> APIResponse[VocabularyItemPayload]:
    return APIResponse(data=update_vocabulary_item(session, current_user, item_id, payload))


@router.delete("/vocabulary-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vocabulary(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    delete_vocabulary_item(session, current_user, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

