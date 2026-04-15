import json
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.schemas.dictionary import (
    DictionaryDefinitionPayload,
    DictionaryEntryPayload,
    DictionaryMeaningPayload,
    DictionaryPhoneticPayload,
)

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "english-learning-server/0.1",
}


def lookup_word(word: str) -> list[DictionaryEntryPayload]:
    normalized_word = word.strip().lower()
    if not normalized_word:
        raise AppError(status_code=400, code=40001, message="word is required")

    settings = get_settings()
    request_url = f"{settings.dictionary_api_base_url}/{quote(normalized_word)}"
    request = Request(request_url, headers=DEFAULT_REQUEST_HEADERS, method="GET")

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise AppError(status_code=404, code=40400, message="word not found") from exc
        raise AppError(
            status_code=502,
            code=50200,
            message=f"dictionary provider http error: {exc.code}",
        ) from exc
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
            raise AppError(
                status_code=502,
                code=50200,
                message=f"dictionary provider bad response: {title or message}",
            )

    if not isinstance(payload, list):
        raise AppError(status_code=502, code=50200, message="dictionary provider response invalid")

    return [build_dictionary_entry(item) for item in payload if isinstance(item, dict)]


def build_dictionary_entry(item: dict) -> DictionaryEntryPayload:
    phonetics = []
    for phonetic in item.get("phonetics", []):
        if not isinstance(phonetic, dict):
            continue
        phonetics.append(
            DictionaryPhoneticPayload(
                text=phonetic.get("text"),
                audio_url=phonetic.get("audio") or None,
            )
        )

    meanings = []
    for meaning in item.get("meanings", []):
        if not isinstance(meaning, dict):
            continue
        definitions = []
        for definition in meaning.get("definitions", []):
            if not isinstance(definition, dict) or not definition.get("definition"):
                continue
            definitions.append(
                DictionaryDefinitionPayload(
                    definition=definition["definition"],
                    example=definition.get("example"),
                )
            )
        if definitions and meaning.get("partOfSpeech"):
            meanings.append(
                DictionaryMeaningPayload(
                    part_of_speech=meaning["partOfSpeech"],
                    definitions=definitions,
                )
            )

    return DictionaryEntryPayload(
        word=item.get("word", ""),
        phonetic=item.get("phonetic"),
        phonetics=phonetics,
        meanings=meanings,
        source_urls=[url for url in item.get("sourceUrls", []) if isinstance(url, str)],
    )
