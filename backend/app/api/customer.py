from typing import Annotated

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models.user import User, UserRole
from app.schemas.customer import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    CustomerProfileResponse,
    CustomerProfileUpdate,
)
from app.services.customer_service import CustomerService
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/customer", tags=["Customer"])

DbSession = Annotated[Session, Depends(get_db)]
CustomerUser = Annotated[User, Depends(require_roles(UserRole.CUSTOMER, UserRole.ADMIN))]


@router.get("/profile", response_model=CustomerProfileResponse)
def get_profile(
    db: DbSession,
    current_user: CustomerUser,
) -> CustomerProfileResponse:
    return CustomerService(db).get_profile(current_user.id)


@router.put("/profile", response_model=CustomerProfileResponse)
def update_profile(
    payload: CustomerProfileUpdate,
    db: DbSession,
    current_user: CustomerUser,
) -> CustomerProfileResponse:
    return CustomerService(db).update_profile(user_id=current_user.id, payload=payload)


@router.get("/addresses", response_model=list[AddressResponse])
def list_addresses(
    db: DbSession,
    current_user: CustomerUser,
) -> list[AddressResponse]:
    return CustomerService(db).list_addresses(current_user.id)


@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    payload: AddressCreate,
    db: DbSession,
    current_user: CustomerUser,
) -> AddressResponse:
    return CustomerService(db).create_address(user_id=current_user.id, payload=payload)


@router.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: str,
    payload: AddressUpdate,
    db: DbSession,
    current_user: CustomerUser,
) -> AddressResponse:
    return CustomerService(db).update_address(
        user_id=current_user.id,
        address_id=address_id,
        payload=payload,
    )


@router.put("/addresses/{address_id}/default", response_model=AddressResponse)
def set_default_shipping_address(
    address_id: str,
    db: DbSession,
    current_user: CustomerUser,
) -> AddressResponse:
    return CustomerService(db).set_default_shipping(
        user_id=current_user.id,
        address_id=address_id,
    )


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: str,
    db: DbSession,
    current_user: CustomerUser,
) -> Response:
    CustomerService(db).delete_address(user_id=current_user.id, address_id=address_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
