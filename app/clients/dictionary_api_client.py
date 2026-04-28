import json
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.core.exceptions import AppError
from app.core.logging import get_logger

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "english-learning-server/0.1",
}
logger = get_logger(__name__)


def fetch_dictionary_entries(base_url: str, word: str) -> list[dict]:
    request_url = f"{base_url}/{quote(word)}"
    request = Request(request_url, headers=DEFAULT_REQUEST_HEADERS, method="GET")
    started_at = time.perf_counter()

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        log_dictionary_failure(word=word, duration_ms=duration_ms_since(started_at), reason="http_error", status_code=exc.code)
        if exc.code == 404:
            raise AppError(status_code=404, code=40400, message="word not found") from exc
        raise AppError(status_code=502, code=50200, message=f"dictionary provider http error: {exc.code}") from exc
    except json.JSONDecodeError as exc:
        log_dictionary_failure(word=word, duration_ms=duration_ms_since(started_at), reason="invalid_json")
        raise AppError(status_code=502, code=50200, message="dictionary provider response invalid") from exc
    except TimeoutError as exc:
        log_dictionary_failure(word=word, duration_ms=duration_ms_since(started_at), reason="timeout")
        raise AppError(status_code=502, code=50200, message="dictionary provider timeout") from exc
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout):
            log_dictionary_failure(word=word, duration_ms=duration_ms_since(started_at), reason="timeout")
            raise AppError(status_code=502, code=50200, message="dictionary provider timeout") from exc
        log_dictionary_failure(word=word, duration_ms=duration_ms_since(started_at), reason="network_error")
        raise AppError(status_code=502, code=50200, message="dictionary provider network error") from exc

    if isinstance(payload, dict):
        title = payload.get("title")
        message = payload.get("message")
        if title or message:
            log_dictionary_failure(word=word, duration_ms=duration_ms_since(started_at), reason="bad_response")
            raise AppError(status_code=502, code=50200, message=f"dictionary provider bad response: {title or message}")

    if not isinstance(payload, list):
        log_dictionary_failure(word=word, duration_ms=duration_ms_since(started_at), reason="invalid_payload")
        raise AppError(status_code=502, code=50200, message="dictionary provider response invalid")

    entries = [item for item in payload if isinstance(item, dict)]
    logger.info(
        "dictionary provider request succeeded",
        extra={
            "provider": "dictionaryapi.dev",
            "word": word,
            "duration_ms": duration_ms_since(started_at),
            "result_count": len(entries),
        },
    )
    return entries


def duration_ms_since(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 2)


def log_dictionary_failure(*, word: str, duration_ms: float, reason: str, status_code: int | None = None) -> None:
    logger.warning(
        "dictionary provider request failed",
        extra={
            "provider": "dictionaryapi.dev",
            "word": word,
            "duration_ms": duration_ms,
            "reason": reason,
            "status_code": status_code or "-",
        },
    )
