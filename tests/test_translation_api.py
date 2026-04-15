from pathlib import Path
import socket
import sys
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.services.translation_service import build_youdao_sign, truncate_text


class MockHTTPResponse:
    def __init__(self, payload: str):
        self.payload = payload

    def read(self) -> bytes:
        return self.payload.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_truncate_text() -> None:
    assert truncate_text("commit") == "commit"
    assert truncate_text("abcdefghijklmnopqrstuvwxyz") == "abcdefghij26qrstuvwxyz"


def test_build_youdao_sign() -> None:
    sign = build_youdao_sign(
        app_key="test-app-key",
        text="commit",
        salt="salt123",
        curtime="1713000000",
        app_secret="secret456",
    )
    assert sign == "6e0cc4adfb2dd6eb1859a282c0657d7a7935e23df9e5a24022fa8a5215451018"


def test_create_translation_success() -> None:
    response_payload = """
    {
      "errorCode": "0",
      "query": "commit",
      "translation": ["承诺", "投入", "提交"]
    }
    """

    with patch("app.services.translation_service.urlopen", return_value=MockHTTPResponse(response_payload)):
        client = TestClient(app)
        response = client.post(
            "/api/v1/translations",
            json={
                "text": "commit",
                "source_language": "en",
                "target_language": "zh-CHS",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["provider"] == "youdao"
    assert body["data"]["translations"] == ["承诺", "投入", "提交"]


def test_create_translation_timeout_error() -> None:
    with patch("app.services.translation_service.urlopen", side_effect=URLError(socket.timeout("timed out"))):
        client = TestClient(app)
        response = client.post(
            "/api/v1/translations",
            json={
                "text": "commit",
                "source_language": "en",
                "target_language": "zh-CHS",
            },
        )

    assert response.status_code == 502
    assert response.json()["message"] == "translation provider timeout"


def test_create_translation_http_error() -> None:
    http_error = HTTPError(
        url="https://openapi.youdao.com/api",
        code=403,
        msg="Forbidden",
        hdrs=None,
        fp=None,
    )

    with patch("app.services.translation_service.urlopen", side_effect=http_error):
        client = TestClient(app)
        response = client.post(
            "/api/v1/translations",
            json={
                "text": "commit",
                "source_language": "en",
                "target_language": "zh-CHS",
            },
        )

    assert response.status_code == 502
    assert response.json()["message"] == "translation provider http error: 403"


if __name__ == "__main__":
    test_truncate_text()
    test_build_youdao_sign()
    test_create_translation_success()
    test_create_translation_timeout_error()
    test_create_translation_http_error()
    print("Translation API tests passed.")
