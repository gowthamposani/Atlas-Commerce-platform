from typing import Annotated

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Authentication"])
DbSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/register",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: DbSession) -> CurrentUserResponse:
    return AuthService(db).register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    return AuthService(db).login(payload)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: DbSession) -> TokenResponse:
    return AuthService(db).refresh(payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: DbSession) -> Response:
    AuthService(db).logout(payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=CurrentUserResponse)
def current_user(current_user: AuthenticatedUser) -> CurrentUserResponse:
    return AuthService.to_current_user(current_user)
