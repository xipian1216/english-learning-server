from urllib.error import HTTPError, URLError

from app.clients.dictionary_api_client import lookup_dictionary_entries
from app.core.errors import ApiError


def lookup_entries(word: str) -> list[dict]:
    try:
        payload = lookup_dictionary_entries(word)
    except HTTPError as exc:
        raise ApiError(status_code=502, code=3101, message=f"dictionary provider http error: {exc.code}") from exc
    except URLError as exc:
        raise ApiError(status_code=502, code=3102, message="dictionary provider unavailable") from exc
    except Exception as exc:
        raise ApiError(status_code=502, code=3103, message="dictionary provider invalid response") from exc
    return [serialize_provider_entry(entry) for entry in payload]


def serialize_provider_entry(entry: dict) -> dict:
    meanings = []
    for meaning in entry.get("meanings") or []:
        definitions = []
        for definition in meaning.get("definitions") or []:
            definitions.append(
                {
                    "definition": definition.get("definition"),
                    "example": definition.get("example"),
                }
            )
        meanings.append({"part_of_speech": meaning.get("partOfSpeech"), "definitions": definitions})
    return {
        "word": entry.get("word"),
        "phonetic": entry.get("phonetic"),
        "phonetics": entry.get("phonetics") or [],
        "meanings": meanings,
        "source_urls": entry.get("sourceUrls") or [],
    }
