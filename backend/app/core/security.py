from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_jwt_token(
    *,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    role: str,
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "role": role,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid4()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_jwt_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
    return payload


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
