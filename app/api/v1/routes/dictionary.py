from fastapi import APIRouter

from app.schemas.common import APIResponse
from app.schemas.dictionary import DictionaryEntryPayload
from app.services.dictionary_service import lookup_word

router = APIRouter(tags=["dictionary"])


@router.get("/dictionary/entries/{word}", response_model=APIResponse[list[DictionaryEntryPayload]])
def get_dictionary_entry(word: str) -> APIResponse[list[DictionaryEntryPayload]]:
    return APIResponse(data=lookup_word(word))
