from pathlib import Path

from alembic import command
from alembic.config import Config
from app.core.config import get_settings
from app.database.session import engine
from sqlalchemy import inspect

AUTH_REVISION = "20260710_0001"
MARKETPLACE_REVISION = "20260710_0002"
HEAD_REVISION = "20260711_0003"

AUTH_TABLES = frozenset({"users", "customer_profiles", "addresses", "refresh_tokens"})
MARKETPLACE_TABLES = frozenset(
    {
        "categories",
        "seller_profiles",
        "products",
        "product_images",
        "product_variants",
        "warehouses",
        "inventory_items",
        "wishlist_items",
        "cart_items",
        "coupons",
        "orders",
        "order_items",
    },
)


def _alembic_config() -> Config:
    backend_dir = Path(__file__).resolve().parents[2]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", get_settings().database_url)
    return config


def _legacy_revision() -> str | None:
    with engine.connect() as connection:
        inspector = inspect(connection)
        if inspector.has_table("alembic_version"):
            return None

        tables = set(inspector.get_table_names())
        if AUTH_TABLES.union(MARKETPLACE_TABLES).issubset(tables):
            product_columns = {column["name"] for column in inspector.get_columns("products")}
            seller_columns = {column["name"] for column in inspector.get_columns("seller_profiles")}
            order_columns = {column["name"] for column in inspector.get_columns("orders")}
            has_admin_columns = (
                {"brand", "is_visible", "is_featured"}.issubset(product_columns)
                and "moderation_status" in seller_columns
                and {"shipment_status", "tracking_number"}.issubset(order_columns)
            )
            return HEAD_REVISION if has_admin_columns else MARKETPLACE_REVISION

        if AUTH_TABLES.issubset(tables):
            return AUTH_REVISION

        return None


def migrate_to_head() -> None:
    config = _alembic_config()
    revision = _legacy_revision()
    if revision is not None:
        command.stamp(config, revision)
    command.upgrade(config, "head")


if __name__ == "__main__":
    migrate_to_head()
