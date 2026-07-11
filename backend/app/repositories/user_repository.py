from app.models.customer_profile import CustomerProfile
from app.models.user import User, UserRole
from sqlalchemy import select
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)

    def create_customer(
        self,
        *,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        phone: str | None,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.CUSTOMER,
        )
        user.profile = CustomerProfile(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        self.db.add(user)
        return user
