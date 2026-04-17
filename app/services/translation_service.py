from __future__ import annotations

from app.clients.youdao_client import build_youdao_sign, request_translation, truncate_text
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.schemas.translation import TranslationCreateRequest, TranslationPayload


def translate_text(payload: TranslationCreateRequest) -> TranslationPayload:
    settings = get_settings()
    if not settings.youdao_app_key or not settings.youdao_app_secret:
        raise AppError(status_code=500, code=50010, message="youdao credentials are not configured")

    raw_payload = request_translation(
        base_url=settings.youdao_api_base_url,
        app_key=settings.youdao_app_key,
        app_secret=settings.youdao_app_secret,
        text=payload.text,
        source_language=payload.source_language,
        target_language=payload.target_language,
        vocab_id=payload.vocab_id,
    )

    if raw_payload.get("errorCode") != "0":
        raise AppError(
            status_code=502,
            code=50010,
            message=f"translation provider request failed: {raw_payload.get('errorCode')}",
        )

    translations = raw_payload.get("translation")
    if not isinstance(translations, list) or not all(isinstance(item, str) for item in translations):
        raise AppError(status_code=502, code=50011, message="translation provider response invalid")

    return TranslationPayload(
        text=payload.text,
        source_language=payload.source_language,
        target_language=payload.target_language,
        translations=translations,
        raw=raw_payload,
    )


__all__ = ["build_youdao_sign", "translate_text", "truncate_text"]
