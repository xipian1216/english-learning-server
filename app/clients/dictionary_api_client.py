import json
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.core.config import get_settings


def lookup_dictionary_entries(word: str) -> list[dict]:
    settings = get_settings()
    url = f"{settings.dictionary_api_base_url.rstrip('/')}/{quote(word, safe='')}"
    try:
        payload = read_dictionary_payload(build_dictionary_request(url))
    except HTTPError as exc:
        if exc.code != 403:
            raise
        payload = read_dictionary_payload(build_dictionary_request(url, browser_like=True))
    if not isinstance(payload, list):
        raise ValueError("dictionary provider returned invalid payload")
    return payload


def read_dictionary_payload(request: Request) -> object:
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def build_dictionary_request(url: str, browser_like: bool = False) -> Request:
    headers = {
        "Accept": "application/json",
        "User-Agent": "english-learning-server/0.1 (+https://dictionaryapi.dev)",
    }
    if browser_like:
        headers.update(
            {
                "Accept": "application/json,text/plain,*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Referer": "https://dictionaryapi.dev/",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            }
        )
    return Request(url, headers=headers)
