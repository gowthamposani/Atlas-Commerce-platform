from datetime import timedelta

from app.core.config import get_settings
from app.core.exceptions import bad_request, unauthorized
from app.core.security import (
    create_jwt_token,
    decode_jwt_token,
    hash_password,
    utc_now,
    verify_password,
)
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from sqlalchemy.orm import Session


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.users = UserRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    def register(self, payload: RegisterRequest) -> CurrentUserResponse:
        if self.users.get_by_email(payload.email) is not None:
            raise bad_request("Email is already registered")

        user = self.users.create_customer(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone,
        )
        self.db.commit()
        self.db.refresh(user)
        return self.to_current_user(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise unauthorized("Invalid email or password")
        if not user.is_active:
            raise unauthorized("User account is inactive")
        return self.issue_tokens(user)

    def refresh(self, payload: RefreshRequest) -> TokenResponse:
        try:
            token_payload = decode_jwt_token(payload.refresh_token)
        except ValueError as exc:
            raise unauthorized() from exc

        if token_payload.get("type") != "refresh":
            raise unauthorized("Refresh token required")

        stored_token = self.refresh_tokens.get_active(payload.refresh_token)
        if stored_token is None or stored_token.expires_at <= utc_now():
            raise unauthorized("Refresh token is expired or revoked")

        user = self.users.get_by_id(stored_token.user_id)
        if user is None or not user.is_active:
            raise unauthorized()

        self.refresh_tokens.revoke(payload.refresh_token)
        return self.issue_tokens(user)

    def logout(self, refresh_token: str) -> None:
        self.refresh_tokens.revoke(refresh_token)
        self.db.commit()

    def issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_jwt_token(
            subject=user.id,
            token_type="access",
            expires_delta=timedelta(minutes=self.settings.access_token_expire_minutes),
            role=user.role.value,
        )
        refresh_expiry = utc_now() + timedelta(days=self.settings.refresh_token_expire_days)
        refresh_token = create_jwt_token(
            subject=user.id,
            token_type="refresh",
            expires_delta=timedelta(days=self.settings.refresh_token_expire_days),
            role=user.role.value,
        )
        self.refresh_tokens.create(
            user_id=user.id,
            token=refresh_token,
            expires_at=refresh_expiry,
        )
        self.db.commit()
        self.db.refresh(user)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=self.to_current_user(user),
        )

    @staticmethod
    def to_current_user(user: User) -> CurrentUserResponse:
        return CurrentUserResponse.model_validate(user)
