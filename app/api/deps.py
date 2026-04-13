from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlmodel import Session

from app.core.exceptions import AppError
from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_session
from app.services.user_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/sessions")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
    except InvalidTokenError as exc:
        raise AppError(status_code=401, code=40100, message="invalid token") from exc

    if not user_id or token_type != "access":
        raise AppError(status_code=401, code=40100, message="invalid token")

    user = get_user_by_id(session, user_id)
    if not user:
        raise AppError(status_code=401, code=40100, message="invalid token")
    if user.status != "active":
        raise AppError(status_code=403, code=40300, message="account unavailable")

    return user

