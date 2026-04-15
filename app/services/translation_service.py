from __future__ import annotations

import hashlib
import json
import socket
import time
from uuid import uuid4
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.schemas.translation import TranslationCreateRequest, TranslationPayload

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "english-learning-server/0.1",
}


def translate_text(payload: TranslationCreateRequest) -> TranslationPayload:
    settings = get_settings()
    if not settings.youdao_app_key or not settings.youdao_app_secret:
        raise AppError(status_code=500, code=50010, message="youdao credentials are not configured")

    salt = uuid4().hex
    curtime = str(int(time.time()))
    form_data = {
        "q": payload.text,
        "from": payload.source_language,
        "to": payload.target_language,
        "appKey": settings.youdao_app_key,
        "salt": salt,
        "curtime": curtime,
        "signType": "v3",
        "sign": build_youdao_sign(
            app_key=settings.youdao_app_key,
            text=payload.text,
            salt=salt,
            curtime=curtime,
            app_secret=settings.youdao_app_secret,
        ),
    }
    if payload.vocab_id:
        form_data["vocabId"] = payload.vocab_id

    request = Request(
        settings.youdao_api_base_url,
        data=urlencode(form_data).encode("utf-8"),
        headers={
            **DEFAULT_REQUEST_HEADERS,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            raw_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise AppError(
            status_code=502,
            code=50010,
            message=f"translation provider http error: {exc.code}",
        ) from exc
    except json.JSONDecodeError as exc:
        raise AppError(status_code=502, code=50011, message="translation provider response invalid") from exc
    except TimeoutError as exc:
        raise AppError(status_code=502, code=50010, message="translation provider timeout") from exc
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout):
            raise AppError(status_code=502, code=50010, message="translation provider timeout") from exc
        raise AppError(status_code=502, code=50010, message="translation provider network error") from exc

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


def build_youdao_sign(*, app_key: str, text: str, salt: str, curtime: str, app_secret: str) -> str:
    sign_str = f"{app_key}{truncate_text(text)}{salt}{curtime}{app_secret}"
    return hashlib.sha256(sign_str.encode("utf-8")).hexdigest()


def truncate_text(text: str) -> str:
    if len(text) <= 20:
        return text
    return f"{text[:10]}{len(text)}{text[-10:]}"
