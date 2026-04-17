from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="English Learning Server", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    database_echo: bool = Field(default=False, alias="APP_DATABASE_ECHO")
    auto_create_tables: bool = Field(default=False, alias="APP_AUTO_CREATE_TABLES")
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
