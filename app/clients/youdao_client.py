import json
import time
import uuid
from urllib.parse import urlencode
from urllib.request import urlopen

from app.core.config import get_settings


def truncate_text(text: str) -> str:
    if len(text) <= 20:
        return text
    return f"{text[:10]}{len(text)}{text[-10:]}"


def build_youdao_sign(app_key: str, text: str, salt: str, curtime: str, app_secret: str) -> str:
    import hashlib

    raw = f"{app_key}{truncate_text(text)}{salt}{curtime}{app_secret}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def translate_text(text: str, source_language: str = "en", target_language: str = "zh-CHS") -> dict:
    settings = get_settings()
    if not settings.youdao_app_key or not settings.youdao_app_secret:
        raise RuntimeError("translation provider credentials are not configured")

    salt = uuid.uuid4().hex
    curtime = str(int(time.time()))
    query = urlencode(
        {
            "q": text,
            "from": source_language,
            "to": target_language,
            "appKey": settings.youdao_app_key,
            "salt": salt,
            "sign": build_youdao_sign(settings.youdao_app_key, text, salt, curtime, settings.youdao_app_secret),
            "signType": "v3",
            "curtime": curtime,
        }
    )
    url = f"{settings.youdao_api_base_url}?{query}"
    with urlopen(url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("translation provider returned invalid payload")
    return payload
