from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.api import (
    auth_router,
    catalog_router,
    customer_router,
    inventory_router,
    orders_router,
    seller_router,
    shopping_router,
)
from app.core.config import get_settings
from app.database.session import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title=settings.project_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(customer_router, prefix=settings.api_prefix)
app.include_router(catalog_router, prefix=settings.api_prefix)
app.include_router(seller_router, prefix=settings.api_prefix)
app.include_router(inventory_router, prefix=settings.api_prefix)
app.include_router(shopping_router, prefix=settings.api_prefix)
app.include_router(orders_router, prefix=settings.api_prefix)
