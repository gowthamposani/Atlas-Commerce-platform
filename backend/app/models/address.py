from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from app.core.security import utc_now
from app.database.base import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(160), nullable=False)
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(30), nullable=False)
    country: Mapped[str] = mapped_column(String(80), default="US", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_default_shipping: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="addresses")
