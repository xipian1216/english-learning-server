from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="English Learning Server", alias="APP_NAME")
    app_env: Literal["development", "production"] = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    log_json: bool = Field(default=False, alias="APP_LOG_JSON")
    log_access_enabled: bool = Field(default=True, alias="APP_LOG_ACCESS_ENABLED")
    database_echo: bool = Field(default=False, alias="APP_DATABASE_ECHO")
    auto_create_tables: bool = Field(default=False, alias="APP_AUTO_CREATE_TABLES")
    cors_allow_credentials: bool = Field(default=True, alias="APP_CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: str = Field(default="GET,POST,PUT,PATCH,DELETE,OPTIONS", alias="APP_CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default="Content-Type,Authorization", alias="APP_CORS_ALLOW_HEADERS")
    cors_expose_headers: str = Field(default="", alias="APP_CORS_EXPOSE_HEADERS")
    cors_max_age: int = Field(default=600, alias="APP_CORS_MAX_AGE")
    cors_dev_allow_origins: str = Field(default="http://localhost:5173", alias="APP_CORS_DEV_ALLOW_ORIGINS")
    cors_prod_allow_origins: str = Field(default="", alias="APP_CORS_PROD_ALLOW_ORIGINS")
    dictionary_api_base_url: str = Field(
        default="https://api.dictionaryapi.dev/api/v2/entries/en",
        alias="APP_DICTIONARY_API_BASE_URL",
    )
    youdao_app_key: str | None = Field(default=None, alias="YOUDAO_APP_KEY")
    youdao_app_secret: str | None = Field(default=None, alias="YOUDAO_APP_SECRET")
    youdao_api_base_url: str = Field(
        default="https://openapi.youdao.com/api",
        alias="YOUDAO_API_BASE_URL",
    )
    secret_key: str | None = Field(default=None, alias="APP_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="APP_JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="APP_ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_required_settings(self) -> "Settings":
        missing_fields: list[str] = []
        if not self.secret_key:
            missing_fields.append("APP_SECRET_KEY")
        if not self.database_url:
            missing_fields.append("DATABASE_URL")

        if missing_fields:
            missing = ", ".join(missing_fields)
            raise ValueError(f"Missing required environment variables: {missing}")

        return self

    def get_cors_allow_origins(self) -> list[str]:
        raw_value = self.cors_dev_allow_origins if self.app_env == "development" else self.cors_prod_allow_origins
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    def get_cors_allow_methods(self) -> list[str]:
        return [item.strip() for item in self.cors_allow_methods.split(",") if item.strip()]

    def get_cors_allow_headers(self) -> list[str]:
        return [item.strip() for item in self.cors_allow_headers.split(",") if item.strip()]

    def get_cors_expose_headers(self) -> list[str]:
        return [item.strip() for item in self.cors_expose_headers.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
