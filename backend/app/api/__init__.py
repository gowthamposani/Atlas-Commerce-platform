from app.api.auth import router as auth_router
from app.api.catalog import router as catalog_router
from app.api.customer import router as customer_router
from app.api.inventory import router as inventory_router
from app.api.orders import router as orders_router
from app.api.seller import router as seller_router
from app.api.shopping import router as shopping_router

__all__ = [
    "auth_router",
    "catalog_router",
    "customer_router",
    "inventory_router",
    "orders_router",
    "seller_router",
    "shopping_router",
]
