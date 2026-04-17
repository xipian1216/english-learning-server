from pathlib import Path
import sys
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.models import DictionaryEntry, DictionarySense, User, UserVocabularyItem
from app.db.session import engine
from app.main import app


def seed_dictionary_entry() -> UUID:
    normalized_word = f"commit-{uuid4().hex[:8]}"
    with Session(engine) as session:
        entry = DictionaryEntry(
            lemma=normalized_word,
            normalized_word=normalized_word,
            display_word=normalized_word,
            phonetic="/kəˈmɪt/",
            source_provider="dictionaryapi",
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)

        sense = DictionarySense(
            entry_id=entry.id,
            part_of_speech="verb",
            definition_en="to promise or devote oneself to something",
            definition_zh="承诺；投入；提交",
            short_definition="承诺；投入",
        )
        session.add(sense)
        session.commit()
        return entry.id


def seed_user(user_id: UUID, email: str) -> User:
    with Session(engine) as session:
        existing_user = session.get(User, user_id)
        if existing_user:
            return existing_user

        user = User(id=user_id, email=email, password_hash="hashed", status="active")
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def clear_user_vocabulary_items(user_id: UUID) -> None:
    with Session(engine) as session:
        statement = select(UserVocabularyItem).where(UserVocabularyItem.user_id == user_id)
        items = session.exec(statement).all()
        for item in items:
            session.delete(item)
        session.commit()


def test_vocabulary_items_are_isolated_by_user() -> None:
    entry_id = seed_dictionary_entry()
    user_a = seed_user(UUID("00000000-0000-0000-0000-000000000101"), "usera@example.com")
    user_b = seed_user(UUID("00000000-0000-0000-0000-000000000102"), "userb@example.com")
    clear_user_vocabulary_items(user_a.id)
    clear_user_vocabulary_items(user_b.id)

    from unittest.mock import patch

    with patch("app.api.deps.decode_access_token") as mock_decode_access_token, patch(
        "app.api.deps.get_user_by_id"
    ) as mock_get_user_by_id:
        client = TestClient(app)

        mock_decode_access_token.return_value = {"sub": str(user_a.id), "type": "access"}
        mock_get_user_by_id.return_value = user_a
        create_response = client.post(
            "/api/v1/vocabulary-items",
            json={
                "text": get_entry_normalized_word(entry_id),
                "source_sentence": "She committed herself to learning English.",
            },
            headers={"Authorization": "Bearer token-a"},
        )
        assert create_response.status_code == 201

        list_response_a = client.get(
            "/api/v1/vocabulary-items",
            headers={"Authorization": "Bearer token-a"},
        )
        assert list_response_a.status_code == 200
        assert len(list_response_a.json()["data"]) == 1

        mock_decode_access_token.return_value = {"sub": str(user_b.id), "type": "access"}
        mock_get_user_by_id.return_value = user_b
        list_response_b = client.get(
            "/api/v1/vocabulary-items",
            headers={"Authorization": "Bearer token-b"},
        )
        assert list_response_b.status_code == 200
        assert list_response_b.json()["data"] == []


def test_vocabulary_item_update_and_delete() -> None:
    entry_id = seed_dictionary_entry()
    user = seed_user(UUID("00000000-0000-0000-0000-000000000103"), "userc@example.com")
    clear_user_vocabulary_items(user.id)

    from unittest.mock import patch

    with patch("app.api.deps.decode_access_token", return_value={"sub": str(user.id), "type": "access"}), patch(
        "app.api.deps.get_user_by_id", return_value=user
    ):
        client = TestClient(app)
        create_response = client.post(
            "/api/v1/vocabulary-items",
            json={"text": get_entry_normalized_word(entry_id)},
            headers={"Authorization": "Bearer token-c"},
        )
        assert create_response.status_code == 201
        item_id = create_response.json()["data"]["id"]

        update_response = client.patch(
            f"/api/v1/vocabulary-items/{item_id}",
            json={"status": "learning", "note": "important", "familiarity_score": 3},
            headers={"Authorization": "Bearer token-c"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["status"] == "learning"
        assert update_response.json()["data"]["note"] == "important"

        delete_response = client.delete(
            f"/api/v1/vocabulary-items/{item_id}",
            headers={"Authorization": "Bearer token-c"},
        )
        assert delete_response.status_code == 204


def test_vocabulary_item_can_bootstrap_dictionary_entry() -> None:
    from unittest.mock import patch
    import json

    unique_word = f"navigate-{uuid4().hex[:8]}"
    user = seed_user(UUID("00000000-0000-0000-0000-000000000104"), "userd@example.com")
    clear_user_vocabulary_items(user.id)

    dictionary_payload = [
        {
            "word": unique_word,
            "phonetic": "/ˈnæv.ɪ.ɡeɪt/",
            "phonetics": [{"text": "/ˈnæv.ɪ.ɡeɪt/", "audio": "https://audio.example/navigate.mp3"}],
            "meanings": [
                {
                    "partOfSpeech": "verb",
                    "definitions": [{"definition": "to find a way", "example": "Birds navigate by the sun."}],
                }
            ],
            "sourceUrls": ["https://dictionaryapi.dev/"],
        }
    ]
    translation_payload = {"translation": ["导航", "确定方向"], "errorCode": "0"}

    with patch("app.api.deps.decode_access_token", return_value={"sub": str(user.id), "type": "access"}), patch(
        "app.api.deps.get_user_by_id", return_value=user
    ), patch("app.clients.dictionary_api_client.urlopen") as mock_dictionary_urlopen, patch(
        "app.clients.youdao_client.urlopen"
    ) as mock_translation_urlopen:
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

        client = TestClient(app)
        response = client.post(
            "/api/v1/vocabulary-items",
            json={
                "text": unique_word,
                "source_language": "en",
                "target_language": "zh-CHS",
            },
            headers={"Authorization": "Bearer token-d"},
        )

    assert response.status_code == 201
    assert response.json()["data"]["word"] == unique_word


def get_entry_normalized_word(entry_id: UUID) -> str:
    with Session(engine) as session:
        entry = session.get(DictionaryEntry, entry_id)
        assert entry is not None
        return entry.normalized_word


if __name__ == "__main__":
    test_vocabulary_items_are_isolated_by_user()
    test_vocabulary_item_update_and_delete()
    print("Vocabulary API tests passed.")
