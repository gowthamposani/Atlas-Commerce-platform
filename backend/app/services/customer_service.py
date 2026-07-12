from app.core.exceptions import not_found
from app.models.address import Address
from app.models.customer_profile import CustomerProfile
from app.models.marketplace import CartItem, Order, WishlistItem
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import (
    AddressCreate,
    AddressUpdate,
    CustomerDashboardResponse,
    CustomerProfileUpdate,
)
from app.schemas.marketplace import OrderResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload


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

    def dashboard(self, user_id: str) -> CustomerDashboardResponse:
        total_orders = int(
            self.db.scalar(select(func.count(Order.id)).where(Order.user_id == user_id)) or 0,
        )
        wishlist_items = int(
            self.db.scalar(
                select(func.count(WishlistItem.id)).where(WishlistItem.user_id == user_id),
            )
            or 0,
        )
        cart_items = int(
            self.db.scalar(
                select(func.coalesce(func.sum(CartItem.quantity), 0)).where(
                    CartItem.user_id == user_id,
                ),
            )
            or 0,
        )
        recent_orders = list(
            self.db.scalars(
                select(Order)
                .options(selectinload(Order.items))
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
                .limit(5),
            ),
        )
        return CustomerDashboardResponse(
            total_orders=total_orders,
            wishlist_items=wishlist_items,
            cart_items=cart_items,
            recent_orders=[OrderResponse.model_validate(order) for order in recent_orders],
        )

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
