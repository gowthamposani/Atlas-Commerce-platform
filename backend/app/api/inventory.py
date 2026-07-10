from typing import Annotated

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.marketplace import (
    InventoryResponse,
    InventoryUpsert,
    InventoryValidationRequest,
    InventoryValidationResponse,
    WarehouseCreate,
    WarehouseResponse,
    WarehouseUpdate,
)
from app.services.marketplace_service import InventoryService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/inventory", tags=["Inventory"])

DbSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_current_user)]


@router.get("/warehouses", response_model=list[WarehouseResponse])
def list_warehouses(db: DbSession, current_user: AuthenticatedUser) -> list[WarehouseResponse]:
    return InventoryService(db).list_warehouses(current_user.id)


@router.post(
    "/warehouses",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_warehouse(
    payload: WarehouseCreate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> WarehouseResponse:
    return InventoryService(db).create_warehouse(user_id=current_user.id, payload=payload)


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: str,
    payload: WarehouseUpdate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> WarehouseResponse:
    return InventoryService(db).update_warehouse(
        user_id=current_user.id,
        warehouse_id=warehouse_id,
        payload=payload,
    )


@router.get("/stock", response_model=list[InventoryResponse])
def list_stock(db: DbSession, current_user: AuthenticatedUser) -> list[InventoryResponse]:
    return InventoryService(db).list_stock(current_user.id)


@router.post("/stock", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def upsert_stock(
    payload: InventoryUpsert,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> InventoryResponse:
    return InventoryService(db).upsert_stock(user_id=current_user.id, payload=payload)


@router.post("/validate", response_model=InventoryValidationResponse)
def validate_stock(
    payload: InventoryValidationRequest,
    db: DbSession,
) -> InventoryValidationResponse:
    return InventoryService(db).validate_stock(payload)
