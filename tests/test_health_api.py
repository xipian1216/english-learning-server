from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def test_healthz() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/healthz")

    assert response.status_code == 200
    assert response.json() == {"code": 0, "message": "ok", "data": {"status": "ok"}}
