from typing import Annotated

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.marketplace import CheckoutCreate, OrderResponse, OrderStatusUpdate
from app.services.marketplace_service import OrderService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/orders", tags=["Orders"])

DbSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_current_user)]


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: CheckoutCreate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> OrderResponse:
    return OrderService(db).create_order(user_id=current_user.id, payload=payload)


@router.get("", response_model=list[OrderResponse])
def order_history(db: DbSession, current_user: AuthenticatedUser) -> list[OrderResponse]:
    return OrderService(db).list_orders(current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def order_details(
    order_id: str,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> OrderResponse:
    return OrderService(db).get_order(user_id=current_user.id, order_id=order_id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> OrderResponse:
    return OrderService(db).cancel_order(user_id=current_user.id, order_id=order_id)


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> OrderResponse:
    return OrderService(db).update_status(
        user_id=current_user.id,
        order_id=order_id,
        payload=payload,
    )
