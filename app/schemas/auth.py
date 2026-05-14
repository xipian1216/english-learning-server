from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetSubmitRequest(BaseModel):
    email: EmailStr
    code: str | None = None
    reset_token: str | None = None
    new_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def require_code_or_token(self) -> "PasswordResetSubmitRequest":
        if not self.code and not self.reset_token:
            raise ValueError("code or reset_token is required")
        return self


class OidcSessionRequest(BaseModel):
    login_code: str = Field(min_length=1)
