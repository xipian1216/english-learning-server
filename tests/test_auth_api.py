import os
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def require_database_url() -> None:
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is required to run auth API tests")


def test_auth_flow() -> None:
    require_database_url()
    client = TestClient(app)

    email = f"codex-{uuid4().hex[:8]}@example.com"
    password = "password123"

    register_response = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "password": password,
            "display_name": "Codex",
        },
    )
    assert register_response.status_code == 201
    register_payload = register_response.json()
    assert register_payload["code"] == 0

    token = register_payload["data"]["access_token"]

    login_response = client.post(
        "/api/v1/sessions",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200
    assert login_response.json()["code"] == 0

    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["data"]["email"] == email

    change_password_response = client.patch(
        "/api/v1/users/me/password",
        json={
            "old_password": password,
            "new_password": "password456",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert change_password_response.status_code == 200
    assert change_password_response.json()["data"] == {"updated": True}
