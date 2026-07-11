from app.models.address import Address
from app.models.customer_profile import CustomerProfile
from sqlalchemy import select, update
from sqlalchemy.orm import Session


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_profile(self, user_id: str) -> CustomerProfile | None:
        statement = select(CustomerProfile).where(CustomerProfile.user_id == user_id)
        return self.db.scalar(statement)

    def list_addresses(self, user_id: str) -> list[Address]:
        statement = (
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.is_default_shipping.desc(), Address.created_at.desc())
        )
        return list(self.db.scalars(statement))

    def get_address(self, *, user_id: str, address_id: str) -> Address | None:
        statement = select(Address).where(
            Address.id == address_id,
            Address.user_id == user_id,
        )
        return self.db.scalar(statement)

    def create_address(self, *, user_id: str, data: dict[str, object]) -> Address:
        address = Address(user_id=user_id, **data)
        self.db.add(address)
        return address

    def clear_default_shipping(self, user_id: str) -> None:
        statement = (
            update(Address)
            .where(Address.user_id == user_id, Address.is_default_shipping.is_(True))
            .values(is_default_shipping=False)
        )
        self.db.execute(statement)
