"""create marketplace and shopping tables

Revision ID: 20260710_0002
Revises: 20260710_0001
Create Date: 2026-07-10 00:00:01.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260710_0002"
down_revision: str | None = "20260710_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    product_status = sa.Enum("DRAFT", "ACTIVE", "INACTIVE", "ARCHIVED", name="product_status")
    order_status = sa.Enum(
        "PENDING",
        "CONFIRMED",
        "PACKED",
        "SHIPPED",
        "DELIVERED",
        "CANCELLED",
        name="order_status",
    )
    discount_type = sa.Enum("PERCENT", "FIXED", name="discount_type")
    product_status.create(op.get_bind(), checkfirst=True)
    order_status.create(op.get_bind(), checkfirst=True)
    discount_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=True)

    op.create_table(
        "seller_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("store_name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_seller_profiles_slug"), "seller_profiles", ["slug"], unique=True)
    op.create_index(
        op.f("ix_seller_profiles_user_id"),
        "seller_profiles",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("seller_id", sa.String(length=36), nullable=False),
        sa.Column("category_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("slug", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", product_status, nullable=False),
        sa.Column("base_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["seller_id"], ["seller_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_category_id"), "products", ["category_id"], unique=False)
    op.create_index(op.f("ix_products_seller_id"), "products", ["seller_id"], unique=False)
    op.create_index(op.f("ix_products_slug"), "products", ["slug"], unique=True)

    op.create_table(
        "product_images",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("alt_text", sa.String(length=180), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_images_product_id"), "product_images", ["product_id"])

    op.create_table(
        "product_variants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("price_delta", sa.Numeric(12, 2), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_variants_product_id"), "product_variants", ["product_id"])
    op.create_index(op.f("ix_product_variants_sku"), "product_variants", ["sku"], unique=True)

    op.create_table(
        "warehouses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("seller_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("country", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["seller_id"], ["seller_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_warehouses_code"), "warehouses", ["code"], unique=True)
    op.create_index(op.f("ix_warehouses_seller_id"), "warehouses", ["seller_id"])

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("variant_id", sa.String(length=36), nullable=True),
        sa.Column("warehouse_id", sa.String(length=36), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reserved_quantity", sa.Integer(), nullable=False),
        sa.Column("reorder_level", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "product_id",
            "variant_id",
            "warehouse_id",
            name="uq_inventory_product_variant_warehouse",
        ),
    )
    op.create_index(op.f("ix_inventory_items_product_id"), "inventory_items", ["product_id"])
    op.create_index(op.f("ix_inventory_items_variant_id"), "inventory_items", ["variant_id"])
    op.create_index(op.f("ix_inventory_items_warehouse_id"), "inventory_items", ["warehouse_id"])

    op.create_table(
        "wishlist_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("variant_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", "variant_id", name="uq_wishlist_user_product"),
    )
    op.create_index(op.f("ix_wishlist_items_product_id"), "wishlist_items", ["product_id"])
    op.create_index(op.f("ix_wishlist_items_user_id"), "wishlist_items", ["user_id"])
    op.create_index(op.f("ix_wishlist_items_variant_id"), "wishlist_items", ["variant_id"])

    op.create_table(
        "cart_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("variant_id", sa.String(length=36), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", "variant_id", name="uq_cart_user_product"),
    )
    op.create_index(op.f("ix_cart_items_product_id"), "cart_items", ["product_id"])
    op.create_index(op.f("ix_cart_items_user_id"), "cart_items", ["user_id"])
    op.create_index(op.f("ix_cart_items_variant_id"), "cart_items", ["variant_id"])

    op.create_table(
        "coupons",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=60), nullable=False),
        sa.Column("discount_type", discount_type, nullable=False),
        sa.Column("discount_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coupons_code"), "coupons", ["code"], unique=True)

    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("order_number", sa.String(length=40), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("shipping_address_id", sa.String(length=36), nullable=False),
        sa.Column("billing_address", sa.JSON(), nullable=False),
        sa.Column("status", order_status, nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("shipping_charge", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("coupon_code", sa.String(length=60), nullable=True),
        sa.Column("payment_method", sa.String(length=80), nullable=False),
        sa.Column("payment_status", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["shipping_address_id"], ["addresses.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_orders_order_number"), "orders", ["order_number"], unique=True)
    op.create_index(op.f("ix_orders_user_id"), "orders", ["user_id"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("order_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("variant_id", sa.String(length=36), nullable=True),
        sa.Column("seller_id", sa.String(length=36), nullable=False),
        sa.Column("product_name", sa.String(length=180), nullable=False),
        sa.Column("variant_name", sa.String(length=160), nullable=True),
        sa.Column("sku", sa.String(length=80), nullable=True),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["seller_id"], ["seller_profiles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_items_order_id"), "order_items", ["order_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_order_items_order_id"), table_name="order_items")
    op.drop_table("order_items")
    op.drop_index(op.f("ix_orders_user_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_order_number"), table_name="orders")
    op.drop_table("orders")
    op.drop_index(op.f("ix_coupons_code"), table_name="coupons")
    op.drop_table("coupons")
    op.drop_index(op.f("ix_cart_items_variant_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_user_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_product_id"), table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_index(op.f("ix_wishlist_items_variant_id"), table_name="wishlist_items")
    op.drop_index(op.f("ix_wishlist_items_user_id"), table_name="wishlist_items")
    op.drop_index(op.f("ix_wishlist_items_product_id"), table_name="wishlist_items")
    op.drop_table("wishlist_items")
    op.drop_index(op.f("ix_inventory_items_warehouse_id"), table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_variant_id"), table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_product_id"), table_name="inventory_items")
    op.drop_table("inventory_items")
    op.drop_index(op.f("ix_warehouses_seller_id"), table_name="warehouses")
    op.drop_index(op.f("ix_warehouses_code"), table_name="warehouses")
    op.drop_table("warehouses")
    op.drop_index(op.f("ix_product_variants_sku"), table_name="product_variants")
    op.drop_index(op.f("ix_product_variants_product_id"), table_name="product_variants")
    op.drop_table("product_variants")
    op.drop_index(op.f("ix_product_images_product_id"), table_name="product_images")
    op.drop_table("product_images")
    op.drop_index(op.f("ix_products_slug"), table_name="products")
    op.drop_index(op.f("ix_products_seller_id"), table_name="products")
    op.drop_index(op.f("ix_products_category_id"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_seller_profiles_user_id"), table_name="seller_profiles")
    op.drop_index(op.f("ix_seller_profiles_slug"), table_name="seller_profiles")
    op.drop_table("seller_profiles")
    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_table("categories")
    sa.Enum(name="discount_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="order_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="product_status").drop(op.get_bind(), checkfirst=True)
