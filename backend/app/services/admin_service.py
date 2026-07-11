import csv
from decimal import Decimal
from io import StringIO
from uuid import uuid4

from app.core.exceptions import not_found
from app.core.security import utc_now
from app.models.marketplace import (
    AuditLog,
    Category,
    Coupon,
    DiscountType,
    InventoryItem,
    Notification,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    PaymentTransaction,
    Product,
    ProductReview,
    ProductStatus,
    ReviewStatus,
    SellerModerationStatus,
    SellerProfile,
    Shipment,
)
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminStatsResponse,
    BrandPayload,
    CouponPayload,
    GeneratedDescriptionResponse,
    NotificationPayload,
    PaymentIntentPayload,
    PaymentUpdatePayload,
    ProductModerationUpdate,
    RecommendationResponse,
    ReportResponse,
    ReviewCreate,
    ReviewModerationUpdate,
    ReviewSummaryResponse,
    SellerModerationUpdate,
    ShipmentPayload,
    UserStatusUpdate,
)
from app.schemas.marketplace import OrderResponse, ProductListResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def dashboard(self) -> AdminDashboardResponse:
        recent_orders = list(
            self.db.scalars(
                select(Order)
                .options(selectinload(Order.items))
                .order_by(Order.created_at.desc())
                .limit(5),
            ),
        )
        pending_products = int(
            self.db.scalar(
                select(func.count(Product.id)).where(Product.status == ProductStatus.DRAFT),
            )
            or 0,
        )
        pending_sellers = int(
            self.db.scalar(
                select(func.count(SellerProfile.id)).where(
                    SellerProfile.moderation_status == SellerModerationStatus.PENDING,
                ),
            )
            or 0,
        )
        return AdminDashboardResponse(
            stats=self.stats(),
            recent_orders=[OrderResponse.model_validate(order) for order in recent_orders],
            pending_sellers=pending_sellers,
            pending_products=pending_products,
        )

    def stats(self) -> AdminStatsResponse:
        total_customers = self._count(User, User.role == UserRole.CUSTOMER)
        total_sellers = self._count(SellerProfile)
        total_products = self._count(Product)
        total_orders = self._count(Order)
        revenue = self.db.scalar(
            select(func.coalesce(func.sum(Order.total_amount), 0)).where(
                Order.payment_status.in_(["paid", "succeeded", PaymentStatus.SUCCEEDED.value]),
                Order.status != OrderStatus.CANCELLED,
            ),
        )
        pending_orders = self._count(Order, Order.status == OrderStatus.PENDING)
        pending_sellers = self._count(
            SellerProfile,
            SellerProfile.moderation_status == SellerModerationStatus.PENDING,
        )
        return AdminStatsResponse(
            total_customers=total_customers,
            total_sellers=total_sellers,
            total_products=total_products,
            total_orders=total_orders,
            revenue_summary=float(revenue or 0),
            pending_orders=pending_orders,
            pending_seller_approvals=pending_sellers,
        )

    def list_users(self, search: str | None = None) -> list[User]:
        statement = select(User).order_by(User.created_at.desc())
        if search:
            statement = statement.where(func.lower(User.email).like(f"%{search.lower()}%"))
        return list(self.db.scalars(statement))

    def update_user_status(self, user_id: str, payload: UserStatusUpdate, actor_id: str) -> User:
        user = self._require(User, user_id, "User was not found")
        user.is_active = payload.is_active
        action = "user.activated" if payload.is_active else "user.suspended"
        self._audit(actor_id, action, "user", user.id)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: str, actor_id: str) -> None:
        user = self._require(User, user_id, "User was not found")
        user.is_active = False
        self._audit(actor_id, "user.deleted", "user", user.id)
        self.db.commit()

    def list_sellers(self) -> list[SellerProfile]:
        statement = select(SellerProfile).order_by(SellerProfile.created_at.desc())
        return list(self.db.scalars(statement))

    def moderate_seller(
        self,
        seller_id: str,
        payload: SellerModerationUpdate,
        actor_id: str,
    ) -> SellerProfile:
        seller = self._require(SellerProfile, seller_id, "Seller was not found")
        seller.moderation_status = payload.status
        seller.is_active = payload.status == SellerModerationStatus.APPROVED
        self._audit(actor_id, f"seller.{payload.status.value}", "seller", seller.id)
        self.db.commit()
        self.db.refresh(seller)
        return seller

    def seller_analytics(self, seller_id: str) -> dict[str, int | float | str]:
        seller = self._require(SellerProfile, seller_id, "Seller was not found")
        product_count = self._count(Product, Product.seller_id == seller.id)
        order_count = int(
            self.db.scalar(
                select(func.count(func.distinct(OrderItem.order_id))).where(
                    OrderItem.seller_id == seller.id,
                ),
            )
            or 0,
        )
        revenue = self.db.scalar(
            select(func.coalesce(func.sum(OrderItem.line_total), 0)).where(
                OrderItem.seller_id == seller.id,
            ),
        )
        return {
            "seller_id": seller.id,
            "store_name": seller.store_name,
            "product_count": product_count,
            "order_count": order_count,
            "revenue": float(revenue or 0),
        }

    def list_products(self, status: ProductStatus | None = None) -> list[Product]:
        statement = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.seller),
                selectinload(Product.images),
            )
            .order_by(Product.created_at.desc())
        )
        if status is not None:
            statement = statement.where(Product.status == status)
        return list(self.db.scalars(statement))

    def moderate_product(
        self,
        product_id: str,
        payload: ProductModerationUpdate,
        actor_id: str,
    ) -> Product:
        product = self._product(product_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        self._audit(actor_id, "product.moderated", "product", product.id)
        self.db.commit()
        return self._product(product.id)

    def manage_brand(self, product_id: str, payload: BrandPayload, actor_id: str) -> Product:
        product = self._product(product_id)
        product.brand = payload.brand
        self._audit(actor_id, "product.brand_updated", "product", product.id)
        self.db.commit()
        return self._product(product.id)

    def list_catalog_admin(self) -> tuple[list[Category], list[str], list[Coupon]]:
        categories = list(self.db.scalars(select(Category).order_by(Category.name)))
        brands = [
            str(value)
            for value in self.db.scalars(
                select(Product.brand).where(Product.brand.is_not(None)).distinct().order_by(Product.brand),
            )
        ]
        coupons = list(self.db.scalars(select(Coupon).order_by(Coupon.created_at.desc())))
        return categories, brands, coupons

    def create_coupon(self, payload: CouponPayload, actor_id: str) -> Coupon:
        coupon = Coupon(
            code=payload.code.upper(),
            discount_type=DiscountType(payload.discount_type),
            discount_value=Decimal(str(payload.discount_value)),
            is_active=payload.is_active,
        )
        self.db.add(coupon)
        self._audit(actor_id, "coupon.created", "coupon", coupon.id)
        self.db.commit()
        self.db.refresh(coupon)
        return coupon

    def list_orders(self) -> list[Order]:
        return list(
            self.db.scalars(
                select(Order)
                .options(selectinload(Order.items))
                .order_by(Order.created_at.desc()),
            ),
        )

    def update_order_status(self, order_id: str, status: OrderStatus, actor_id: str) -> Order:
        order = self._order(order_id)
        order.status = status
        if status == OrderStatus.CANCELLED:
            order.payment_status = PaymentStatus.FAILED.value
        if status == OrderStatus.REFUNDED:
            order.payment_status = PaymentStatus.REFUNDED.value
        self._audit(actor_id, f"order.{status.value}", "order", order.id)
        self.db.commit()
        return self._order(order.id)

    def refund_order(self, order_id: str, actor_id: str) -> Order:
        return self.update_order_status(order_id, OrderStatus.REFUNDED, actor_id)

    def create_review(self, user_id: str, payload: ReviewCreate) -> ProductReview:
        product = self._product(payload.product_id)
        review = ProductReview(
            product_id=product.id,
            user_id=user_id,
            **payload.model_dump(exclude={"product_id"}),
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def list_reviews(self) -> list[ProductReview]:
        statement = select(ProductReview).order_by(ProductReview.created_at.desc())
        return list(self.db.scalars(statement))

    def moderate_review(
        self,
        review_id: str,
        payload: ReviewModerationUpdate,
        actor_id: str,
    ) -> ProductReview:
        review = self._require(ProductReview, review_id, "Review was not found")
        review.status = payload.status
        review.report_reason = payload.report_reason
        self._audit(actor_id, f"review.{payload.status.value}", "review", review.id)
        self.db.commit()
        self.db.refresh(review)
        return review

    def report(self, name: str) -> ReportResponse:
        rows: list[dict[str, str | int | float | None]]
        if name == "sales":
            rows = [
                {
                    "order_number": order.order_number,
                    "status": order.status.value,
                    "total": float(order.total_amount),
                    "created_at": order.created_at.isoformat(),
                }
                for order in self.list_orders()
            ]
        elif name == "inventory":
            rows = [
                {
                    "product_id": item.product_id,
                    "warehouse_id": item.warehouse_id,
                    "quantity": item.quantity,
                    "reserved_quantity": item.reserved_quantity,
                }
                for item in self.db.scalars(select(InventoryItem))
            ]
        elif name == "sellers":
            rows = [
                {
                    "seller_id": seller.id,
                    "store_name": seller.store_name,
                    "status": seller.moderation_status.value,
                    "is_active": str(seller.is_active),
                }
                for seller in self.list_sellers()
            ]
        else:
            rows = [
                {
                    "user_id": user.id,
                    "email": user.email,
                    "role": user.role.value,
                    "is_active": str(user.is_active),
                }
                for user in self.list_users()
            ]
        return ReportResponse(name=name, generated_at=utc_now(), rows=rows)

    def report_csv(self, name: str) -> str:
        report = self.report(name)
        if not report.rows:
            return ""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=list(report.rows[0].keys()))
        writer.writeheader()
        writer.writerows(report.rows)
        return output.getvalue()

    def report_pdf_placeholder(self, name: str) -> bytes:
        report = self.report(name)
        lines = [f"Atlas Commerce Platform {name.title()} Report", report.generated_at.isoformat()]
        lines.extend(str(row) for row in report.rows)
        return ("\n".join(lines) + "\n").encode()

    def create_notification(self, payload: NotificationPayload, actor_id: str) -> Notification:
        notification = Notification(**payload.model_dump())
        self.db.add(notification)
        self._audit(actor_id, "notification.created", "notification", notification.id)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_notifications(self) -> list[Notification]:
        return list(self.db.scalars(select(Notification).order_by(Notification.created_at.desc())))

    def create_payment_intent(
        self,
        payload: PaymentIntentPayload,
        actor_id: str,
    ) -> PaymentTransaction:
        order = self._order(payload.order_id)
        transaction = PaymentTransaction(
            order_id=order.id,
            provider_reference=payload.provider_reference or f"stripe_test_{uuid4().hex}",
            amount=order.total_amount,
            status=PaymentStatus.PENDING,
            raw_response={"mode": "sandbox"},
        )
        self.db.add(transaction)
        self._audit(actor_id, "payment.intent_created", "payment", transaction.id)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update_payment(
        self,
        payment_id: str,
        payload: PaymentUpdatePayload,
        actor_id: str,
    ) -> PaymentTransaction:
        transaction = self._require(PaymentTransaction, payment_id, "Payment was not found")
        transaction.status = payload.status
        transaction.order.payment_status = payload.status.value
        self._audit(actor_id, f"payment.{payload.status.value}", "payment", transaction.id)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def list_payments(self) -> list[PaymentTransaction]:
        statement = select(PaymentTransaction).order_by(PaymentTransaction.created_at.desc())
        return list(self.db.scalars(statement))

    def create_shipment(self, order_id: str, payload: ShipmentPayload, actor_id: str) -> Shipment:
        order = self._order(order_id)
        shipment = Shipment(order_id=order.id, **payload.model_dump())
        order.shipment_status = payload.status.value
        order.tracking_number = payload.tracking_number
        self.db.add(shipment)
        self._audit(actor_id, "shipment.created", "shipment", shipment.id)
        self.db.commit()
        self.db.refresh(shipment)
        return shipment

    def list_shipments(self) -> list[Shipment]:
        return list(self.db.scalars(select(Shipment).order_by(Shipment.created_at.desc())))

    def recommendations(self, product_id: str) -> RecommendationResponse:
        product = self._product(product_id)
        statement = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.seller),
                selectinload(Product.images),
            )
            .where(
                Product.id != product.id,
                Product.status == ProductStatus.ACTIVE,
                Product.is_visible.is_(True),
                or_(Product.category_id == product.category_id, Product.brand == product.brand),
            )
            .limit(6)
        )
        return RecommendationResponse(
            product_id=product.id,
            recommendations=[
                ProductListResponse.model_validate(item) for item in self.db.scalars(statement)
            ],
        )

    def generate_description(self, product_id: str) -> GeneratedDescriptionResponse:
        product = self._product(product_id)
        brand = f" from {product.brand}" if product.brand else ""
        description = (
            f"{product.name}{brand} is curated for Atlas Commerce customers with reliable "
            f"quality, clear value, and fast fulfillment. Ideal for shoppers comparing trusted "
            f"marketplace products in {product.category.name}."
        )
        return GeneratedDescriptionResponse(product_id=product.id, description=description)

    def review_summary(self, product_id: str) -> ReviewSummaryResponse:
        self._product(product_id)
        count = self._count(ProductReview, ProductReview.product_id == product_id)
        average = self.db.scalar(
            select(func.coalesce(func.avg(ProductReview.rating), 0)).where(
                ProductReview.product_id == product_id,
                ProductReview.status == ReviewStatus.APPROVED,
            ),
        )
        summary = "No approved reviews yet."
        if count:
            summary = (
                "Customers highlight product quality, fulfillment reliability, "
                "and overall value."
            )
        return ReviewSummaryResponse(
            product_id=product_id,
            average_rating=float(average or 0),
            review_count=count,
            summary=summary,
        )

    def _product(self, product_id: str) -> Product:
        statement = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.seller),
                selectinload(Product.images),
            )
            .where(Product.id == product_id)
        )
        product = self.db.scalar(statement)
        if product is None:
            raise not_found("Product was not found")
        return product

    def _order(self, order_id: str) -> Order:
        statement = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        order = self.db.scalar(statement)
        if order is None:
            raise not_found("Order was not found")
        return order

    def _require(
        self,
        model: type[User] | type[SellerProfile] | type[ProductReview] | type[PaymentTransaction],
        item_id: str,
        message: str,
    ):
        item = self.db.get(model, item_id)
        if item is None:
            raise not_found(message)
        return item

    def _count(
        self,
        model: type[User] | type[SellerProfile] | type[Product] | type[Order] | type[ProductReview],
        *filters: object,
    ) -> int:
        statement = select(func.count(model.id))
        if filters:
            statement = statement.where(*filters)
        return int(self.db.scalar(statement) or 0)

    def _audit(
        self,
        actor_id: str | None,
        action: str,
        entity_type: str,
        entity_id: str | None,
    ) -> None:
        self.db.add(
            AuditLog(
                actor_user_id=actor_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                metadata_json={},
            ),
        )
