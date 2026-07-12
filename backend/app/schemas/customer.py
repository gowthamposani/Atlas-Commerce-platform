from datetime import datetime

from app.schemas.marketplace import OrderResponse
from app.schemas.validation import (
    clean_optional_required_text,
    clean_optional_text,
    clean_text,
    validate_optional_person_name,
    validate_person_name,
    validate_phone_number,
    validate_postal_code,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CustomerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    phone: str | None = None
    created_at: datetime
    updated_at: datetime


class CustomerProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str | None, info) -> str | None:
        label = "First name" if info.field_name == "first_name" else "Last name"
        return validate_optional_person_name(value, field_name=label)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return validate_phone_number(value)


class AddressBase(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    recipient_name: str = Field(min_length=1, max_length=160)
    line1: str = Field(min_length=1, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=120)
    state: str = Field(min_length=1, max_length=120)
    postal_code: str = Field(min_length=1, max_length=30)
    country: str = Field(default="US", min_length=2, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    is_default_shipping: bool = False

    @field_validator("label", "line1", "city", "state", "country")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return clean_text(value, field_name=str(info.field_name).replace("_", " ").title()) or ""

    @field_validator("line2")
    @classmethod
    def validate_optional_line2(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Address line 2")

    @field_validator("recipient_name")
    @classmethod
    def validate_recipient(cls, value: str) -> str:
        return validate_person_name(value, field_name="Recipient name")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return validate_phone_number(value)

    @model_validator(mode="after")
    def validate_postal(self) -> "AddressBase":
        self.country = self.country.upper()
        self.postal_code = validate_postal_code(self.postal_code, country=self.country)
        return self


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=80)
    recipient_name: str | None = Field(default=None, min_length=1, max_length=160)
    line1: str | None = Field(default=None, min_length=1, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    state: str | None = Field(default=None, min_length=1, max_length=120)
    postal_code: str | None = Field(default=None, min_length=1, max_length=30)
    country: str | None = Field(default=None, min_length=2, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    is_default_shipping: bool | None = None

    @field_validator("label", "line1", "city", "state", "country")
    @classmethod
    def validate_optional_text_fields(cls, value: str | None, info) -> str | None:
        return clean_optional_required_text(
            value,
            field_name=str(info.field_name).replace("_", " ").title(),
        )

    @field_validator("line2")
    @classmethod
    def validate_optional_line2(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Address line 2")

    @field_validator("recipient_name")
    @classmethod
    def validate_recipient(cls, value: str | None) -> str | None:
        return validate_optional_person_name(value, field_name="Recipient name")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return validate_phone_number(value)

    @model_validator(mode="after")
    def validate_postal(self) -> "AddressUpdate":
        if self.country is not None:
            self.country = self.country.upper()
        if self.postal_code is not None:
            self.postal_code = validate_postal_code(self.postal_code, country=self.country or "US")
        return self


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    recipient_name: str
    line1: str
    line2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    phone: str | None
    is_default_shipping: bool
    created_at: datetime
    updated_at: datetime


class CustomerDashboardResponse(BaseModel):
    total_orders: int
    wishlist_items: int
    cart_items: int
    recent_orders: list[OrderResponse]
