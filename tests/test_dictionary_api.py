from pathlib import Path
import sys
from unittest.mock import patch
from urllib.error import HTTPError

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


class MockHTTPResponse:
    def __init__(self, payload: str):
        self.payload = payload

    def read(self) -> bytes:
        return self.payload.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_dictionary_lookup_success() -> None:
    response_payload = """
    [
      {
        "word": "hello",
        "phonetic": "/həˈləʊ/",
        "phonetics": [{"text": "/həˈləʊ/", "audio": "https://audio.example/hello.mp3"}],
        "meanings": [
          {
            "partOfSpeech": "exclamation",
            "definitions": [{"definition": "Used as a greeting.", "example": "Hello, world!"}]
          }
        ],
        "sourceUrls": ["https://dictionaryapi.dev/"]
      }
    ]
    """

    with patch("app.clients.dictionary_api_client.urlopen", return_value=MockHTTPResponse(response_payload)):
        client = TestClient(app)
        response = client.get("/api/v1/dictionary/entries/hello")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"][0]["word"] == "hello"
    assert body["data"][0]["meanings"][0]["part_of_speech"] == "exclamation"


def test_dictionary_client_sends_provider_headers() -> None:
    from app.clients.dictionary_api_client import lookup_dictionary_entries

    response_payload = '[{"word":"hello","meanings":[]}]'

    with patch("app.clients.dictionary_api_client.urlopen", return_value=MockHTTPResponse(response_payload)) as mock_urlopen:
        entries = lookup_dictionary_entries("hello")

    request = mock_urlopen.call_args.args[0]
    assert entries[0]["word"] == "hello"
    assert request.get_header("Accept") == "application/json"
    assert request.get_header("User-agent") == "english-learning-server/0.1 (+https://dictionaryapi.dev)"


def test_dictionary_client_retries_403_with_browser_headers() -> None:
    from app.clients.dictionary_api_client import lookup_dictionary_entries

    response_payload = '[{"word":"hello","meanings":[]}]'
    http_error = HTTPError(
        url="https://api.dictionaryapi.dev/api/v2/entries/en/hello",
        code=403,
        msg="Forbidden",
        hdrs=None,
        fp=None,
    )

    with patch(
        "app.clients.dictionary_api_client.urlopen",
        side_effect=[http_error, MockHTTPResponse(response_payload)],
    ) as mock_urlopen:
        entries = lookup_dictionary_entries("hello")

    retry_request = mock_urlopen.call_args_list[1].args[0]
    assert entries[0]["word"] == "hello"
    assert mock_urlopen.call_count == 2
    assert retry_request.get_header("Referer") == "https://dictionaryapi.dev/"
    assert "Mozilla/5.0" in retry_request.get_header("User-agent")


if __name__ == "__main__":
    test_dictionary_lookup_success()
    test_dictionary_client_sends_provider_headers()
    test_dictionary_client_retries_403_with_browser_headers()
    print("Dictionary API test passed.")
