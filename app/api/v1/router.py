from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.dictionary import router as dictionary_router
from app.api.v1.routes.translation import router as translation_router
from app.api.v1.routes.vocabulary import router as vocabulary_router
from app.api.v1.routes.word_detail import router as word_detail_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(dictionary_router)
api_router.include_router(translation_router)
api_router.include_router(vocabulary_router)
api_router.include_router(word_detail_router)
