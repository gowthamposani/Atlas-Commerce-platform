from collections.abc import Callable
from typing import Annotated

from app.core.exceptions import forbidden, unauthorized
from app.core.security import decode_jwt_token
from app.database.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    credentials: BearerCredentials,
    db: DbSession,
) -> User:
    if credentials is None:
        raise unauthorized()

    try:
        payload = decode_jwt_token(credentials.credentials)
    except ValueError as exc:
        raise unauthorized() from exc

    if payload.get("type") != "access":
        raise unauthorized("Access token required")

    user_id = payload.get("sub")
    if not isinstance(user_id, str):
        raise unauthorized()

    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise unauthorized()

    return user


def require_roles(*allowed_roles: UserRole) -> Callable[..., User]:
    def checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise forbidden()
        return current_user

    return checker
