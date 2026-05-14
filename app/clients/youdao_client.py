import json
from urllib.parse import urlencode
from urllib.request import urlopen

from app.core.config import get_settings


def translate_text(text: str, source_language: str = "en", target_language: str = "zh-CHS") -> dict:
    settings = get_settings()
    query = urlencode({"q": text, "from": source_language, "to": target_language})
    url = f"{settings.youdao_api_base_url}?{query}"
    with urlopen(url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("translation provider returned invalid payload")
    return payload
