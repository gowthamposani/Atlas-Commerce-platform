from typing import Annotated

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.marketplace import (
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductUpdate,
    SellerCreate,
    SellerDashboardResponse,
    SellerResponse,
    SellerUpdate,
)
from app.services.marketplace_service import SellerService
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/seller", tags=["Seller"])

DbSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_current_user)]


@router.post("/profile", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
def register_seller(
    payload: SellerCreate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> SellerResponse:
    return SellerService(db).get_or_create_profile(user_id=current_user.id, payload=payload)


@router.get("/profile", response_model=SellerResponse)
def get_seller_profile(db: DbSession, current_user: AuthenticatedUser) -> SellerResponse:
    return SellerService(db).require_seller(current_user.id)


@router.put("/profile", response_model=SellerResponse)
def update_seller_profile(
    payload: SellerUpdate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> SellerResponse:
    return SellerService(db).update_profile(user_id=current_user.id, payload=payload)


@router.get("/dashboard", response_model=SellerDashboardResponse)
def seller_dashboard(
    db: DbSession,
    current_user: AuthenticatedUser,
) -> SellerDashboardResponse:
    return SellerService(db).dashboard(current_user.id)


@router.get("/stores/{seller_id}", response_model=SellerResponse)
def seller_store(seller_id: str, db: DbSession) -> SellerResponse:
    return SellerService(db).public_store(seller_id)


@router.get("/products", response_model=list[ProductListResponse])
def list_seller_products(
    db: DbSession,
    current_user: AuthenticatedUser,
) -> list[ProductListResponse]:
    return SellerService(db).list_products(current_user.id)


@router.post("/products", response_model=ProductDetailResponse, status_code=status.HTTP_201_CREATED)
def create_seller_product(
    payload: ProductCreate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> ProductDetailResponse:
    product = SellerService(db).create_product(user_id=current_user.id, payload=payload)
    return ProductDetailResponse.model_validate(
        {
            **product.__dict__,
            "category": product.category,
            "seller": product.seller,
            "images": product.images,
            "variants": product.variants,
            "available_quantity": 0,
        },
    )


@router.put("/products/{product_id}", response_model=ProductDetailResponse)
def update_seller_product(
    product_id: str,
    payload: ProductUpdate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> ProductDetailResponse:
    product = SellerService(db).update_product(
        user_id=current_user.id,
        product_id=product_id,
        payload=payload,
    )
    return ProductDetailResponse.model_validate(
        {
            **product.__dict__,
            "category": product.category,
            "seller": product.seller,
            "images": product.images,
            "variants": product.variants,
            "available_quantity": 0,
        },
    )


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_seller_product(
    product_id: str,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> Response:
    SellerService(db).delete_product(user_id=current_user.id, product_id=product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
