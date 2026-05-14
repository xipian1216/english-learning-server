import hashlib
import socket
from urllib.error import HTTPError, URLError

from app.clients.youdao_client import translate_text
from app.core.errors import ApiError


def truncate_text(text: str) -> str:
    if len(text) <= 20:
        return text
    return f"{text[:10]}{len(text)}{text[-10:]}"


def build_youdao_sign(app_key: str, text: str, salt: str, curtime: str, app_secret: str) -> str:
    raw = f"{app_key}{truncate_text(text)}{salt}{curtime}{app_secret}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_translation(text: str, source_language: str = "en", target_language: str = "zh-CHS") -> dict:
    try:
        payload = translate_text(text, source_language, target_language)
    except HTTPError as exc:
        raise ApiError(status_code=502, code=3004, message=f"translation provider http error: {exc.code}") from exc
    except URLError as exc:
        if isinstance(exc.reason, socket.timeout):
            raise ApiError(status_code=502, code=3002, message="translation provider timeout") from exc
        raise ApiError(status_code=502, code=3003, message="translation provider unavailable") from exc
    except Exception as exc:
        raise ApiError(status_code=502, code=3005, message="translation provider invalid response") from exc

    if str(payload.get("errorCode")) != "0":
        raise ApiError(status_code=502, code=3006, message="translation provider returned error")
    translations = payload.get("translation") or []
    return {"provider": "youdao", "query_text": text, "translations": translations, "raw_payload": payload}
