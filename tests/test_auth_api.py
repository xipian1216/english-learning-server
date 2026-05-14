import os
from pathlib import Path
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.core.config import get_settings


def require_database_url() -> None:
    if not (os.getenv("DATABASE_URL") or get_settings().database_url):
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

    old_password_login_response = client.post(
        "/api/v1/sessions",
        json={"email": email, "password": password},
    )
    assert old_password_login_response.status_code == 401

    new_password_login_response = client.post(
        "/api/v1/sessions",
        json={"email": email, "password": "password456"},
    )
    assert new_password_login_response.status_code == 200


def test_register_rejects_duplicate_email() -> None:
    require_database_url()
    client = TestClient(app)
    email = f"duplicate-{uuid4().hex[:8]}@example.com"

    first_response = client.post(
        "/api/v1/users",
        json={"email": email, "password": "password123", "display_name": "Codex"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/users",
        json={"email": email, "password": "password123", "display_name": "Codex"},
    )
    assert second_response.status_code == 409
    assert second_response.json()["code"] == 1101


def test_register_rejects_invalid_email_and_weak_password() -> None:
    client = TestClient(app)

    invalid_email_response = client.post(
        "/api/v1/users",
        json={"email": "not-email", "password": "password123", "display_name": "Codex"},
    )
    assert invalid_email_response.status_code == 400

    weak_password_response = client.post(
        "/api/v1/users",
        json={"email": "weak@example.com", "password": "short", "display_name": "Codex"},
    )
    assert weak_password_response.status_code == 400


def test_login_rejects_unknown_email_and_wrong_password() -> None:
    require_database_url()
    client = TestClient(app)
    email = f"login-{uuid4().hex[:8]}@example.com"

    unknown_response = client.post(
        "/api/v1/sessions",
        json={"email": email, "password": "password123"},
    )
    assert unknown_response.status_code == 401


    client.post(
        "/api/v1/users",
        json={"email": email, "password": "password123", "display_name": "Codex"},
    )
    wrong_password_response = client.post(
        "/api/v1/sessions",
        json={"email": email, "password": "password999"},
    )
    assert wrong_password_response.status_code == 401


def test_me_rejects_missing_and_invalid_token() -> None:
    client = TestClient(app)

    missing_response = client.get("/api/v1/users/me")
    assert missing_response.status_code == 401

    invalid_response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer invalid-token"})
    assert invalid_response.status_code == 401


def test_change_password_rejects_wrong_old_password() -> None:
    require_database_url()
    client = TestClient(app)
    email = f"change-{uuid4().hex[:8]}@example.com"

    register_response = client.post(
        "/api/v1/users",
        json={"email": email, "password": "password123", "display_name": "Codex"},
    )
    token = register_response.json()["data"]["access_token"]

    response = client.patch(
        "/api/v1/users/me/password",
        json={"old_password": "password999", "new_password": "password456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_reserved_password_reset_apis() -> None:
    client = TestClient(app)

    request_response = client.post(
        "/api/v1/users/password-reset-requests",
        json={"email": "reset@example.com"},
    )
    assert request_response.status_code == 501
    assert request_response.json()["message"] == "password reset is not configured"

    reset_response = client.post(
        "/api/v1/users/password-resets",
        json={"email": "reset@example.com", "code": "123456", "new_password": "password456"},
    )
    assert reset_response.status_code == 501
    assert reset_response.json()["message"] == "password reset is not configured"


def test_reserved_oidc_apis() -> None:
    client = TestClient(app)

    login_response = client.get("/api/v1/auth/oidc/authentik/login")
    assert login_response.status_code == 503
    assert login_response.json()["message"] == "oidc provider is not configured"

    callback_response = client.get("/api/v1/auth/oidc/authentik/callback")
    assert callback_response.status_code == 503

    session_response = client.post(
        "/api/v1/auth/oidc/authentik/sessions",
        json={"login_code": "login-code"},
    )
    assert session_response.status_code == 503

    unknown_provider_response = client.get("/api/v1/auth/oidc/google/login")
    assert unknown_provider_response.status_code == 404


if __name__ == "__main__":
    require_database_url()
    test_auth_flow()
    print("Auth API test passed.")
