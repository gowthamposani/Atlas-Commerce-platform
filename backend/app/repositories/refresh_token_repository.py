from datetime import datetime
from hashlib import sha256

from app.core.security import utc_now
from app.models.refresh_token import RefreshToken
from sqlalchemy import select
from sqlalchemy.orm import Session


def hash_refresh_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


class RefreshTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, user_id: str, token: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(token),
            expires_at=expires_at,
        )
        self.db.add(refresh_token)
        return refresh_token

    def get_active(self, token: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(token),
            RefreshToken.revoked_at.is_(None),
        )
        return self.db.scalar(statement)

    def revoke(self, token: str) -> RefreshToken | None:
        refresh_token = self.get_active(token)
        if refresh_token is not None:
            refresh_token.revoked_at = utc_now()
        return refresh_token

    def revoke_all_for_user(self, user_id: str) -> None:
        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        for refresh_token in self.db.scalars(statement):
            refresh_token.revoked_at = utc_now()
