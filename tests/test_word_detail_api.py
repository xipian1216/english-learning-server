from pathlib import Path
import sys
from unittest.mock import patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.models import DictionaryEntry
from app.db.session import engine
from app.main import app


def test_word_detail_requires_auth() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/word-details",
        json={
            "text": "commit",
            "source_language": "en",
            "target_language": "zh-CHS",
        },
    )
    assert response.status_code == 401


def test_word_detail_success() -> None:
    dictionary_payload = [
        {
            "word": "commit",
            "phonetic": "/kəˈmɪt/",
            "phonetics": [{"text": "/kəˈmɪt/", "audio": "https://audio.example/commit.mp3"}],
            "meanings": [
                {
                    "partOfSpeech": "verb",
                    "definitions": [
                        {
                            "definition": "to promise or devote oneself to something",
                            "example": "She committed herself to learning English every day.",
                        }
                    ],
                }
            ],
            "sourceUrls": ["https://dictionaryapi.dev/"],
        }
    ]
    translation_payload = {"translation": ["承诺", "投入", "提交"], "errorCode": "0"}
    sentence_translation_payload = {"translation": ["她承诺每天学习英语。"], "errorCode": "0"}

    with patch("app.services.dictionary_service.urlopen") as mock_dictionary_urlopen, patch(
        "app.services.translation_service.urlopen"
    ) as mock_translation_urlopen, patch("app.api.deps.decode_access_token", return_value={"sub": "00000000-0000-0000-0000-000000000001", "type": "access"}), patch(
        "app.api.deps.get_user_by_id"
    ) as mock_get_user_by_id:
        from app.db.models import User
        from uuid import UUID
        import json

        class MockResponse:
            def __init__(self, payload: str):
                self.payload = payload

            def read(self) -> bytes:
                return self.payload.encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                return None

        mock_dictionary_urlopen.return_value = MockResponse(json.dumps(dictionary_payload))
        mock_translation_urlopen.side_effect = [
            MockResponse(json.dumps(translation_payload)),
            MockResponse(json.dumps(sentence_translation_payload)),
        ]
        mock_get_user_by_id.return_value = User(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            email="tester@example.com",
            password_hash="hashed",
            status="active",
        )

        client = TestClient(app)
        response = client.post(
            "/api/v1/word-details",
            json={
                "text": "commit",
                "source_language": "en",
                "target_language": "zh-CHS",
                "context_sentence": "She committed herself to learning English every day.",
            },
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["query_text"] == "commit"
    assert body["data"]["entry"]["word"] == "commit"
    assert body["data"]["entry"]["senses"][0]["definition_zh"] == "承诺；投入；提交"
    assert body["data"]["entry"]["examples"][0]["sentence_zh"] == "她承诺每天学习英语。"


def test_word_detail_writes_cache() -> None:
    unique_word = f"commit-{uuid4().hex[:8]}"
    dictionary_payload = [
        {
            "word": unique_word,
            "phonetic": "/kəˈmɪt/",
            "phonetics": [{"text": "/kəˈmɪt/", "audio": "https://audio.example/commit.mp3"}],
            "meanings": [
                {
                    "partOfSpeech": "verb",
                    "definitions": [{"definition": "to promise", "example": "They commit to practice."}],
                }
            ],
            "sourceUrls": ["https://dictionaryapi.dev/"],
        }
    ]
    translation_payload = {"translation": ["承诺"], "errorCode": "0"}

    with patch("app.services.dictionary_service.urlopen") as mock_dictionary_urlopen, patch(
        "app.services.translation_service.urlopen"
    ) as mock_translation_urlopen, patch("app.api.deps.decode_access_token", return_value={"sub": "00000000-0000-0000-0000-000000000001", "type": "access"}), patch(
        "app.api.deps.get_user_by_id"
    ) as mock_get_user_by_id:
        from app.db.models import User
        import json

        class MockResponse:
            def __init__(self, payload: str):
                self.payload = payload

            def read(self) -> bytes:
                return self.payload.encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                return None

        mock_dictionary_urlopen.return_value = MockResponse(json.dumps(dictionary_payload))
        mock_translation_urlopen.return_value = MockResponse(json.dumps(translation_payload))
        mock_get_user_by_id.return_value = User(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            email="tester@example.com",
            password_hash="hashed",
            status="active",
        )

        client = TestClient(app)
        response = client.post(
            "/api/v1/word-details",
            json={
                "text": unique_word,
                "source_language": "en",
                "target_language": "zh-CHS",
            },
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 200
    with Session(engine) as session:
        statement = select(DictionaryEntry).where(DictionaryEntry.normalized_word == unique_word)
        cached_entry = session.exec(statement).first()
        assert cached_entry is not None


if __name__ == "__main__":
    test_word_detail_requires_auth()
    test_word_detail_success()
    print("Word detail API tests passed.")
