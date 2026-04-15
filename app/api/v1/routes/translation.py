from fastapi import APIRouter

from app.schemas.common import APIResponse
from app.schemas.translation import TranslationCreateRequest, TranslationPayload
from app.services.translation_service import translate_text

router = APIRouter(tags=["translation"])


@router.post("/translations", response_model=APIResponse[TranslationPayload])
def create_translation(payload: TranslationCreateRequest) -> APIResponse[TranslationPayload]:
    return APIResponse(data=translate_text(payload))

