import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from app.core.security import utc_now
from app.database.base import Base
from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.customer_profile import CustomerProfile
    from app.models.refresh_token import RefreshToken


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.CUSTOMER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    profile: Mapped["CustomerProfile"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
