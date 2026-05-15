import socket
from urllib.error import HTTPError, URLError

from app.clients.youdao_client import build_youdao_sign, translate_text, truncate_text
from app.core.errors import ApiError


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

    provider_error_code = str(payload.get("errorCode"))
    if provider_error_code != "0":
        raise ApiError(status_code=502, code=3006, message=f"translation provider returned error: {provider_error_code}")
    translations = payload.get("translation") or []
    return {"provider": "youdao", "query_text": text, "translations": translations}
