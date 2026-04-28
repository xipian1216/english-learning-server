import hashlib
import json
import socket
import time
from uuid import uuid4
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.exceptions import AppError
from app.core.logging import get_logger

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "english-learning-server/0.1",
}
logger = get_logger(__name__)


def request_translation(
    *,
    base_url: str,
    app_key: str,
    app_secret: str,
    text: str,
    source_language: str,
    target_language: str,
    vocab_id: str | None,
) -> dict:
    salt = uuid4().hex
    curtime = str(int(time.time()))
    form_data = {
        "q": text,
        "from": source_language,
        "to": target_language,
        "appKey": app_key,
        "salt": salt,
        "curtime": curtime,
        "signType": "v3",
        "sign": build_youdao_sign(
            app_key=app_key,
            text=text,
            salt=salt,
            curtime=curtime,
            app_secret=app_secret,
        ),
    }
    if vocab_id:
        form_data["vocabId"] = vocab_id

    request = Request(
        base_url,
        data=urlencode(form_data).encode("utf-8"),
        headers={**DEFAULT_REQUEST_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    started_at = time.perf_counter()

    try:
        with urlopen(request, timeout=10) as response:
            raw_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        log_translation_failure(
            source_language=source_language,
            target_language=target_language,
            text_length=len(text),
            duration_ms=duration_ms_since(started_at),
            reason="http_error",
            status_code=exc.code,
        )
        raise AppError(status_code=502, code=50010, message=f"translation provider http error: {exc.code}") from exc
    except json.JSONDecodeError as exc:
        log_translation_failure(
            source_language=source_language,
            target_language=target_language,
            text_length=len(text),
            duration_ms=duration_ms_since(started_at),
            reason="invalid_json",
        )
        raise AppError(status_code=502, code=50011, message="translation provider response invalid") from exc
    except TimeoutError as exc:
        log_translation_failure(
            source_language=source_language,
            target_language=target_language,
            text_length=len(text),
            duration_ms=duration_ms_since(started_at),
            reason="timeout",
        )
        raise AppError(status_code=502, code=50010, message="translation provider timeout") from exc
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout):
            log_translation_failure(
                source_language=source_language,
                target_language=target_language,
                text_length=len(text),
                duration_ms=duration_ms_since(started_at),
                reason="timeout",
            )
            raise AppError(status_code=502, code=50010, message="translation provider timeout") from exc
        log_translation_failure(
            source_language=source_language,
            target_language=target_language,
            text_length=len(text),
            duration_ms=duration_ms_since(started_at),
            reason="network_error",
        )
        raise AppError(status_code=502, code=50010, message="translation provider network error") from exc

    logger.info(
        "translation provider request completed",
        extra={
            "provider": "youdao",
            "source_language": source_language,
            "target_language": target_language,
            "text_length": len(text),
            "has_vocab_id": bool(vocab_id),
            "duration_ms": duration_ms_since(started_at),
            "provider_error_code": raw_payload.get("errorCode"),
        },
    )
    return raw_payload


def build_youdao_sign(*, app_key: str, text: str, salt: str, curtime: str, app_secret: str) -> str:
    sign_str = f"{app_key}{truncate_text(text)}{salt}{curtime}{app_secret}"
    return hashlib.sha256(sign_str.encode("utf-8")).hexdigest()


def truncate_text(text: str) -> str:
    if len(text) <= 20:
        return text
    return f"{text[:10]}{len(text)}{text[-10:]}"


def duration_ms_since(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 2)


def log_translation_failure(
    *,
    source_language: str,
    target_language: str,
    text_length: int,
    duration_ms: float,
    reason: str,
    status_code: int | None = None,
) -> None:
    logger.warning(
        "translation provider request failed",
        extra={
            "provider": "youdao",
            "source_language": source_language,
            "target_language": target_language,
            "text_length": text_length,
            "duration_ms": duration_ms,
            "reason": reason,
            "status_code": status_code or "-",
        },
    )
