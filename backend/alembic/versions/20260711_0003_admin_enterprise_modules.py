"""add admin enterprise modules

Revision ID: 20260711_0003
Revises: 20260710_0002
Create Date: 2026-07-11 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260711_0003"
down_revision: str | None = "20260710_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE product_status ADD VALUE IF NOT EXISTS 'REJECTED'")
        op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'REFUNDED'")

    seller_status = sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        "SUSPENDED",
        name="seller_moderation_status",
    )
    review_status = sa.Enum("PENDING", "APPROVED", "REPORTED", "DELETED", name="review_status")
    notification_type = sa.Enum("ORDER", "SELLER", "ADMIN", "PAYMENT", name="notification_type")
    payment_status = sa.Enum("PENDING", "SUCCEEDED", "FAILED", "REFUNDED", name="payment_status")
    shipment_status = sa.Enum(
        "PENDING",
        "LABEL_CREATED",
        "IN_TRANSIT",
        "DELIVERED",
        "FAILED",
        name="shipment_status",
    )
    for enum_type in (seller_status, review_status, notification_type, payment_status, shipment_status):
        enum_type.create(bind, checkfirst=True)

    op.add_column(
        "seller_profiles",
        sa.Column("moderation_status", seller_status, nullable=False, server_default="PENDING"),
    )
    op.add_column("products", sa.Column("brand", sa.String(length=120), nullable=True))
    op.add_column(
        "products",
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "products",
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "orders",
        sa.Column("shipment_status", sa.String(length=80), nullable=False, server_default="pending"),
    )
    op.add_column("orders", sa.Column("tracking_number", sa.String(length=120), nullable=True))

    op.create_table(
        "product_reviews",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", review_status, nullable=False),
        sa.Column("report_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_reviews_product_id"), "product_reviews", ["product_id"])
    op.create_index(op.f("ix_product_reviews_user_id"), "product_reviews", ["user_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"])

    op.create_table(
        "payment_transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("order_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("provider_reference", sa.String(length=160), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", payment_status, nullable=False),
        sa.Column("raw_response", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_reference"),
    )
    op.create_index(op.f("ix_payment_transactions_order_id"), "payment_transactions", ["order_id"])

    op.create_table(
        "shipments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("order_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("label_url", sa.String(length=500), nullable=True),
        sa.Column("tracking_number", sa.String(length=120), nullable=True),
        sa.Column("status", shipment_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shipments_order_id"), "shipments", ["order_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=160), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_actor_user_id"), "audit_logs", ["actor_user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_actor_user_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_shipments_order_id"), table_name="shipments")
    op.drop_table("shipments")
    op.drop_index(op.f("ix_payment_transactions_order_id"), table_name="payment_transactions")
    op.drop_table("payment_transactions")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_product_reviews_user_id"), table_name="product_reviews")
    op.drop_index(op.f("ix_product_reviews_product_id"), table_name="product_reviews")
    op.drop_table("product_reviews")
    op.drop_column("orders", "tracking_number")
    op.drop_column("orders", "shipment_status")
    op.drop_column("products", "is_featured")
    op.drop_column("products", "is_visible")
    op.drop_column("products", "brand")
    op.drop_column("seller_profiles", "moderation_status")
