import pytest
from pathlib import Path
import sys
from typing import Any, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import Settings


def build_settings(**kwargs) -> Settings:
    original_env: dict[str, str | None] = {
        "APP_AUTO_CREATE_TABLES": None,
        "APP_DEBUG": None,
        "APP_NAME": None,
        "APP_ENV": None,
        "APP_DATABASE_ECHO": None,
        "APP_DICTIONARY_API_BASE_URL": None,
        "APP_SECRET_KEY": None,
        "APP_JWT_ALGORITHM": None,
        "APP_ACCESS_TOKEN_EXPIRE_MINUTES": None,
        "DATABASE_URL": None,
        "YOUDAO_APP_KEY": None,
        "YOUDAO_APP_SECRET": None,
        "YOUDAO_API_BASE_URL": None,
        "APP_AUTHENTIK_ENABLED": None,
        "APP_AUTHENTIK_ISSUER_URL": None,
        "APP_AUTHENTIK_CLIENT_ID": None,
        "APP_AUTHENTIK_CLIENT_SECRET": None,
        "APP_AUTHENTIK_SCOPES": None,
        "APP_AUTHENTIK_ALLOWED_REDIRECT_URIS": None,
        "APP_OAUTH_LOGIN_CODE_EXPIRE_SECONDS": None,
        "APP_SESSION_COOKIE_NAME": None,
        "APP_SESSION_COOKIE_SECURE": None,
    }
    import os

    for key in original_env:
        original_env[key] = os.environ.get(key)
        os.environ.pop(key, None)

    try:
        settings_cls = cast(Any, Settings)
        return settings_cls(_env_file=None, **kwargs)
    finally:
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_settings_require_secret_key() -> None:
    with pytest.raises(ValueError, match="APP_SECRET_KEY"):
        build_settings(
            DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/testdb",
            APP_SECRET_KEY=None,
        )


def test_settings_require_database_url() -> None:
    with pytest.raises(ValueError, match="DATABASE_URL"):
        build_settings(
            DATABASE_URL=None,
            APP_SECRET_KEY="test-secret-key",
        )


def test_auto_create_tables_defaults_to_false() -> None:
    settings = build_settings(
        DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/testdb",
        APP_SECRET_KEY="test-secret-key",
    )
    assert settings.auto_create_tables is False


def test_authentik_defaults_to_disabled() -> None:
    settings = build_settings(
        DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/testdb",
        APP_SECRET_KEY="test-secret-key",
    )
    assert settings.authentik_enabled is False
    assert settings.get_authentik_allowed_redirect_uris() == []


def test_authentik_enabled_requires_provider_settings() -> None:
    with pytest.raises(ValueError, match="APP_AUTHENTIK_ISSUER_URL"):
        build_settings(
            DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/testdb",
            APP_SECRET_KEY="test-secret-key",
            APP_AUTHENTIK_ENABLED=True,
        )


def test_authentik_enabled_with_complete_settings() -> None:
    settings = build_settings(
        DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/testdb",
        APP_SECRET_KEY="test-secret-key",
        APP_AUTHENTIK_ENABLED=True,
        APP_AUTHENTIK_ISSUER_URL="https://auth.example.com/application/o/app/",
        APP_AUTHENTIK_CLIENT_ID="client-id",
        APP_AUTHENTIK_CLIENT_SECRET="client-secret",
        APP_AUTHENTIK_ALLOWED_REDIRECT_URIS="http://localhost:5173/auth/callback,https://app.example.com/auth/callback",
    )
    assert settings.authentik_issuer_url == "https://auth.example.com/application/o/app"
    assert settings.get_authentik_scopes() == ["openid", "email", "profile"]
    assert settings.get_authentik_allowed_redirect_uris() == [
        "http://localhost:5173/auth/callback",
        "https://app.example.com/auth/callback",
    ]
