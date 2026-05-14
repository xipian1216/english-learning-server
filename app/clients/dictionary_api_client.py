import json
from urllib.parse import quote
from urllib.request import urlopen

from app.core.config import get_settings


def lookup_dictionary_entries(word: str) -> list[dict]:
    settings = get_settings()
    url = f"{settings.dictionary_api_base_url.rstrip('/')}/{quote(word)}"
    with urlopen(url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list):
        raise ValueError("dictionary provider returned invalid payload")
    return payload
