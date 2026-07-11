from app.core.exceptions import not_found
from app.models.address import Address
from app.models.customer_profile import CustomerProfile
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import AddressCreate, AddressUpdate, CustomerProfileUpdate
from sqlalchemy.orm import Session


class CustomerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.customers = CustomerRepository(db)

    def get_profile(self, user_id: str) -> CustomerProfile:
        profile = self.customers.get_profile(user_id)
        if profile is None:
            raise not_found("Customer profile was not found")
        return profile

    def update_profile(self, *, user_id: str, payload: CustomerProfileUpdate) -> CustomerProfile:
        profile = self.get_profile(user_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def list_addresses(self, user_id: str) -> list[Address]:
        return self.customers.list_addresses(user_id)

    def create_address(self, *, user_id: str, payload: AddressCreate) -> Address:
        data = payload.model_dump()
        if data["is_default_shipping"]:
            self.customers.clear_default_shipping(user_id)
        address = self.customers.create_address(user_id=user_id, data=data)
        self.db.commit()
        self.db.refresh(address)
        return address

    def update_address(
        self,
        *,
        user_id: str,
        address_id: str,
        payload: AddressUpdate,
    ) -> Address:
        address = self._get_address(user_id=user_id, address_id=address_id)
        data = payload.model_dump(exclude_unset=True)
        if data.get("is_default_shipping") is True:
            self.customers.clear_default_shipping(user_id)
        for field, value in data.items():
            setattr(address, field, value)
        self.db.commit()
        self.db.refresh(address)
        return address

    def set_default_shipping(self, *, user_id: str, address_id: str) -> Address:
        address = self._get_address(user_id=user_id, address_id=address_id)
        self.customers.clear_default_shipping(user_id)
        address.is_default_shipping = True
        self.db.commit()
        self.db.refresh(address)
        return address

    def delete_address(self, *, user_id: str, address_id: str) -> None:
        address = self._get_address(user_id=user_id, address_id=address_id)
        self.db.delete(address)
        self.db.commit()

    def _get_address(self, *, user_id: str, address_id: str) -> Address:
        address = self.customers.get_address(user_id=user_id, address_id=address_id)
        if address is None:
            raise not_found("Address was not found")
        return address
