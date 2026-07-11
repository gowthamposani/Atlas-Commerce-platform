from typing import Annotated

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.marketplace import (
    CartAdd,
    CartQuantityUpdate,
    CartSummaryResponse,
    WishlistAdd,
    WishlistItemResponse,
)
from app.services.marketplace_service import ShoppingService
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["Shopping"])

DbSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_current_user)]


@router.get("/wishlist", response_model=list[WishlistItemResponse])
def list_wishlist(
    db: DbSession,
    current_user: AuthenticatedUser,
) -> list[WishlistItemResponse]:
    return ShoppingService(db).list_wishlist(current_user.id)


@router.post("/wishlist", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    payload: WishlistAdd,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> WishlistItemResponse:
    return ShoppingService(db).add_to_wishlist(user_id=current_user.id, payload=payload)


@router.delete("/wishlist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_wishlist_item(
    item_id: str,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> Response:
    ShoppingService(db).remove_wishlist_item(user_id=current_user.id, item_id=item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/wishlist/{item_id}/move-to-cart", response_model=CartSummaryResponse)
def move_wishlist_to_cart(
    item_id: str,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> CartSummaryResponse:
    return ShoppingService(db).move_wishlist_to_cart(user_id=current_user.id, item_id=item_id)


@router.get("/cart", response_model=CartSummaryResponse)
def cart_summary(db: DbSession, current_user: AuthenticatedUser) -> CartSummaryResponse:
    return ShoppingService(db).cart_summary(current_user.id)


@router.post("/cart/items", response_model=CartSummaryResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    payload: CartAdd,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> CartSummaryResponse:
    return ShoppingService(db).add_to_cart(user_id=current_user.id, payload=payload)


@router.put("/cart/items/{item_id}", response_model=CartSummaryResponse)
def update_cart_item(
    item_id: str,
    payload: CartQuantityUpdate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> CartSummaryResponse:
    return ShoppingService(db).update_cart_item(
        user_id=current_user.id,
        item_id=item_id,
        payload=payload,
    )


@router.delete("/cart/items/{item_id}", response_model=CartSummaryResponse)
def remove_cart_item(
    item_id: str,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> CartSummaryResponse:
    return ShoppingService(db).remove_cart_item(user_id=current_user.id, item_id=item_id)
