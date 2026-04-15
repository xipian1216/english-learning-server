from pathlib import Path
import sys
from unittest.mock import patch

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

    with patch("app.services.dictionary_service.urlopen", return_value=MockHTTPResponse(response_payload)):
        client = TestClient(app)
        response = client.get("/api/v1/dictionary/entries/hello")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"][0]["word"] == "hello"
    assert body["data"][0]["meanings"][0]["part_of_speech"] == "exclamation"


if __name__ == "__main__":
    test_dictionary_lookup_success()
    print("Dictionary API test passed.")
