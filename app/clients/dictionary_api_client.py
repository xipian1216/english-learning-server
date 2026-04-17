import json
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.core.exceptions import AppError

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "english-learning-server/0.1",
}


def fetch_dictionary_entries(base_url: str, word: str) -> list[dict]:
    request_url = f"{base_url}/{quote(word)}"
    request = Request(request_url, headers=DEFAULT_REQUEST_HEADERS, method="GET")

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise AppError(status_code=404, code=40400, message="word not found") from exc
        raise AppError(status_code=502, code=50200, message=f"dictionary provider http error: {exc.code}") from exc
    except json.JSONDecodeError as exc:
        raise AppError(status_code=502, code=50200, message="dictionary provider response invalid") from exc
    except TimeoutError as exc:
        raise AppError(status_code=502, code=50200, message="dictionary provider timeout") from exc
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout):
            raise AppError(status_code=502, code=50200, message="dictionary provider timeout") from exc
        raise AppError(status_code=502, code=50200, message="dictionary provider network error") from exc

    if isinstance(payload, dict):
        title = payload.get("title")
        message = payload.get("message")
        if title or message:
            raise AppError(status_code=502, code=50200, message=f"dictionary provider bad response: {title or message}")

    if not isinstance(payload, list):
        raise AppError(status_code=502, code=50200, message="dictionary provider response invalid")

    return [item for item in payload if isinstance(item, dict)]
