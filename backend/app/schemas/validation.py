import re
from typing import Any

from app.core.config import get_settings

CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SCRIPT_TAG_PATTERN = re.compile(r"<\s*/?\s*script\b", re.IGNORECASE)
PERSON_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z' -]*$")
PHONE_PATTERN = re.compile(r"^\+?\d+$")
POSTAL_CODE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 -]{1,18}[A-Za-z0-9]$")
US_ZIP_PATTERN = re.compile(r"^\d{5}(?:-\d{4})?$")
SKU_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._-]{1,79}$")
CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._-]{1,79}$")


def clean_text(value: Any, *, field_name: str, required: bool = True) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"{field_name} is required")
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text")
    cleaned = value.strip()
    if not cleaned:
        if required:
            raise ValueError(f"{field_name} is required")
        return None
    if CONTROL_CHAR_PATTERN.search(cleaned) or SCRIPT_TAG_PATTERN.search(cleaned):
        raise ValueError(f"{field_name} contains unsupported characters")
    return cleaned


def clean_optional_text(value: Any, *, field_name: str) -> str | None:
    return clean_text(value, field_name=field_name, required=False)


def clean_optional_required_text(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    return clean_text(value, field_name=field_name)


def validate_person_name(value: Any, *, field_name: str) -> str:
    cleaned = clean_text(value, field_name=field_name)
    if cleaned is None or not PERSON_NAME_PATTERN.fullmatch(cleaned):
        raise ValueError(f"{field_name} may contain letters, spaces, hyphens, and apostrophes only")
    return cleaned


def validate_optional_person_name(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    return validate_person_name(value, field_name=field_name)


def validate_password_strength(value: Any) -> str:
    password = clean_text(value, field_name="Password")
    if password is None:
        raise ValueError("Password is required")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must include an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must include a lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must include a number")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must include a special character")
    return password


def validate_phone_number(value: Any) -> str | None:
    cleaned = clean_optional_text(value, field_name="Phone number")
    if cleaned is None:
        return None
    settings = get_settings()
    digit_count = len(cleaned[1:] if cleaned.startswith("+") else cleaned)
    if not PHONE_PATTERN.fullmatch(cleaned):
        raise ValueError("Phone number must contain digits only and may start with +")
    if digit_count < settings.phone_min_digits or digit_count > settings.phone_max_digits:
        raise ValueError(
            "Phone number must contain "
            f"{settings.phone_min_digits} to {settings.phone_max_digits} digits",
        )
    return cleaned


def validate_postal_code(value: Any, *, country: str | None = None) -> str:
    cleaned = clean_text(value, field_name="Postal code")
    if cleaned is None:
        raise ValueError("Postal code is required")
    if (country or "").strip().upper() == "US":
        if not US_ZIP_PATTERN.fullmatch(cleaned):
            raise ValueError("US ZIP code must be 5 digits or ZIP+4 format")
        return cleaned
    if not POSTAL_CODE_PATTERN.fullmatch(cleaned):
        raise ValueError("Postal code contains invalid characters")
    return cleaned


def validate_sku(value: Any) -> str:
    cleaned = clean_text(value, field_name="SKU")
    if cleaned is None:
        raise ValueError("SKU is required")
    normalized = cleaned.upper()
    if not SKU_PATTERN.fullmatch(normalized):
        raise ValueError(
            "SKU may contain uppercase letters, numbers, dots, hyphens, and underscores",
        )
    return normalized


def validate_code(value: Any, *, field_name: str) -> str:
    cleaned = clean_text(value, field_name=field_name)
    if cleaned is None:
        raise ValueError(f"{field_name} is required")
    normalized = cleaned.upper()
    if not CODE_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{field_name} may contain letters, numbers, dots, hyphens, and underscores",
        )
    return normalized
