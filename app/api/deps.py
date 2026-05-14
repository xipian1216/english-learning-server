from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.errors import ApiError
from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_session
from app.repositories.user_repository import get_user_by_id


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    if credentials is None:
        raise ApiError(status_code=401, code=1001, message="missing access token")

    payload = decode_access_token(credentials.credentials)
    if payload.get("type") != "access":
        raise ApiError(status_code=401, code=1002, message="invalid access token")

    subject = payload.get("sub")
    if not subject:
        raise ApiError(status_code=401, code=1002, message="invalid access token")

    try:
        user_id = UUID(str(subject))
    except ValueError as exc:
        raise ApiError(status_code=401, code=1002, message="invalid access token") from exc

    user = get_user_by_id(session, user_id)
    if user is None:
        raise ApiError(status_code=401, code=1002, message="invalid access token")
    if user.status != "active":
        raise ApiError(status_code=403, code=1003, message="account is not active")
    return user
