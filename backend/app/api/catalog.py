from typing import Annotated

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.marketplace import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductDetailResponse,
    ProductPageResponse,
)
from app.services.marketplace_service import CatalogService
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/catalog", tags=["Catalog"])

DbSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_current_user)]


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: DbSession) -> list[CategoryResponse]:
    return CatalogService(db).list_categories()


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    db: DbSession,
    _: AuthenticatedUser,
) -> CategoryResponse:
    return CatalogService(db).create_category(payload)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    payload: CategoryUpdate,
    db: DbSession,
    _: AuthenticatedUser,
) -> CategoryResponse:
    return CatalogService(db).update_category(category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    db: DbSession,
    _: AuthenticatedUser,
) -> Response:
    CatalogService(db).delete_category(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/products", response_model=ProductPageResponse)
def search_products(
    db: DbSession,
    search: str | None = None,
    category_id: str | None = None,
    seller_id: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
) -> ProductPageResponse:
    return CatalogService(db).search_products(
        search=search,
        category_id=category_id,
        seller_id=seller_id,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size,
    )


@router.get("/products/{product_id}", response_model=ProductDetailResponse)
def product_details(product_id: str, db: DbSession) -> ProductDetailResponse:
    return CatalogService(db).product_details(product_id)
