import hashlib
import json
import socket
import time
from uuid import uuid4
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.exceptions import AppError

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "english-learning-server/0.1",
}


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

    try:
        with urlopen(request, timeout=10) as response:
            raw_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise AppError(status_code=502, code=50010, message=f"translation provider http error: {exc.code}") from exc
    except json.JSONDecodeError as exc:
        raise AppError(status_code=502, code=50011, message="translation provider response invalid") from exc
    except TimeoutError as exc:
        raise AppError(status_code=502, code=50010, message="translation provider timeout") from exc
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout):
            raise AppError(status_code=502, code=50010, message="translation provider timeout") from exc
        raise AppError(status_code=502, code=50010, message="translation provider network error") from exc

    return raw_payload


def build_youdao_sign(*, app_key: str, text: str, salt: str, curtime: str, app_secret: str) -> str:
    sign_str = f"{app_key}{truncate_text(text)}{salt}{curtime}{app_secret}"
    return hashlib.sha256(sign_str.encode("utf-8")).hexdigest()


def truncate_text(text: str) -> str:
    if len(text) <= 20:
        return text
    return f"{text[:10]}{len(text)}{text[-10:]}"
