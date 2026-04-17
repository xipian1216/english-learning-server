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
