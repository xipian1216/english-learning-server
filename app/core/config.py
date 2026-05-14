from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = Field(default="English Learning Server", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    database_echo: bool = Field(default=False, validation_alias="APP_DATABASE_ECHO")
    auto_create_tables: bool = Field(default=False, validation_alias="APP_AUTO_CREATE_TABLES")
    secret_key: str | None = Field(default=None, validation_alias="APP_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="APP_JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, validation_alias="APP_ACCESS_TOKEN_EXPIRE_MINUTES")

    authentik_enabled: bool = Field(default=False, validation_alias="APP_AUTHENTIK_ENABLED")
    authentik_issuer_url: str | None = Field(default=None, validation_alias="APP_AUTHENTIK_ISSUER_URL")
    authentik_client_id: str | None = Field(default=None, validation_alias="APP_AUTHENTIK_CLIENT_ID")
    authentik_client_secret: str | None = Field(default=None, validation_alias="APP_AUTHENTIK_CLIENT_SECRET")
    authentik_scopes: str = Field(default="openid email profile", validation_alias="APP_AUTHENTIK_SCOPES")
    authentik_allowed_redirect_uris: str = Field(default="", validation_alias="APP_AUTHENTIK_ALLOWED_REDIRECT_URIS")
    oauth_login_code_expire_seconds: int = Field(default=120, validation_alias="APP_OAUTH_LOGIN_CODE_EXPIRE_SECONDS")
    session_cookie_name: str = Field(default="english_learning_session", validation_alias="APP_SESSION_COOKIE_NAME")
    session_cookie_secure: bool = Field(default=False, validation_alias="APP_SESSION_COOKIE_SECURE")

    cors_dev_allow_origins: str = Field(default="http://localhost:5173", validation_alias="APP_CORS_DEV_ALLOW_ORIGINS")
    cors_prod_allow_origins: str = Field(default="", validation_alias="APP_CORS_PROD_ALLOW_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, validation_alias="APP_CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: str = Field(default="GET,POST,PUT,PATCH,DELETE,OPTIONS", validation_alias="APP_CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default="Content-Type,Authorization", validation_alias="APP_CORS_ALLOW_HEADERS")
    dictionary_api_base_url: str = Field(
        default="https://api.dictionaryapi.dev/api/v2/entries/en", validation_alias="APP_DICTIONARY_API_BASE_URL"
    )
    youdao_api_base_url: str = Field(default="https://openapi.youdao.com/api", validation_alias="YOUDAO_API_BASE_URL")
    youdao_app_key: str | None = Field(default=None, validation_alias="YOUDAO_APP_KEY")
    youdao_app_secret: str | None = Field(default=None, validation_alias="YOUDAO_APP_SECRET")

    @field_validator("authentik_issuer_url")
    @classmethod
    def normalize_url(cls, value: str | None) -> str | None:
        return value.rstrip("/") if value else value

    @model_validator(mode="after")
    def validate_required_settings(self) -> "Settings":
        if not self.database_url:
            raise ValueError("DATABASE_URL is required")
        if not self.secret_key:
            raise ValueError("APP_SECRET_KEY is required")
        if self.authentik_enabled:
            required = {
                "APP_AUTHENTIK_ISSUER_URL": self.authentik_issuer_url,
                "APP_AUTHENTIK_CLIENT_ID": self.authentik_client_id,
                "APP_AUTHENTIK_CLIENT_SECRET": self.authentik_client_secret,
            }
            for name, value in required.items():
                if not value:
                    raise ValueError(f"{name} is required when APP_AUTHENTIK_ENABLED=true")
        return self

    def get_authentik_scopes(self) -> list[str]:
        return [item.strip() for item in self.authentik_scopes.split() if item.strip()]

    def get_authentik_allowed_redirect_uris(self) -> list[str]:
        return [item.strip() for item in self.authentik_allowed_redirect_uris.split(",") if item.strip()]

    def get_cors_origins(self) -> list[str]:
        raw = self.cors_dev_allow_origins if self.app_env == "development" else self.cors_prod_allow_origins
        return [item.strip() for item in raw.split(",") if item.strip()]

    def get_cors_methods(self) -> list[str]:
        return [item.strip() for item in self.cors_allow_methods.split(",") if item.strip()]

    def get_cors_headers(self) -> list[str]:
        return [item.strip() for item in self.cors_allow_headers.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
