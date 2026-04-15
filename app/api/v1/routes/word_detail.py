from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_session
from app.schemas.common import APIResponse
from app.schemas.word_detail import WordDetailPayload, WordDetailRequest
from app.services.word_detail_service import build_word_detail

router = APIRouter(tags=["word-detail"])


@router.post("/word-details", response_model=APIResponse[WordDetailPayload])
def create_word_detail(
    payload: WordDetailRequest,
    _: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> APIResponse[WordDetailPayload]:
    return APIResponse(data=build_word_detail(session, payload))
