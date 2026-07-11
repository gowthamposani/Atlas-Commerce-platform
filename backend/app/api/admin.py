from typing import Annotated

from app.core.dependencies import get_current_user, require_roles
from app.database.session import get_db
from app.models.marketplace import ProductStatus
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminOrderStatusUpdate,
    AdminStatsResponse,
    AdminUserResponse,
    BrandPayload,
    CatalogAdminResponse,
    CouponPayload,
    CouponResponse,
    GeneratedDescriptionResponse,
    NotificationPayload,
    NotificationResponse,
    PaymentIntentPayload,
    PaymentResponse,
    PaymentUpdatePayload,
    ProductModerationUpdate,
    RecommendationResponse,
    ReportResponse,
    ReviewCreate,
    ReviewModerationUpdate,
    ReviewResponse,
    ReviewSummaryResponse,
    SellerModerationUpdate,
    ShipmentPayload,
    ShipmentResponse,
    UserStatusUpdate,
)
from app.schemas.marketplace import OrderResponse, ProductListResponse, SellerResponse
from app.services.admin_service import AdminService
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin", tags=["Admin"])
review_router = APIRouter(prefix="/reviews", tags=["Reviews"])

DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
AuthenticatedUser = Annotated[User, Depends(get_current_user)]


@router.get("/dashboard", response_model=AdminDashboardResponse)
def dashboard(db: DbSession, _: AdminUser) -> AdminDashboardResponse:
    return AdminService(db).dashboard()


@router.get("/stats", response_model=AdminStatsResponse)
def stats(db: DbSession, _: AdminUser) -> AdminStatsResponse:
    return AdminService(db).stats()


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(db: DbSession, _: AdminUser, search: str | None = None) -> list[AdminUserResponse]:
    return AdminService(db).list_users(search)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: str,
    payload: UserStatusUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> AdminUserResponse:
    return AdminService(db).update_user_status(user_id, payload, current_user.id)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: DbSession, current_user: AdminUser) -> Response:
    AdminService(db).delete_user(user_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/sellers", response_model=list[SellerResponse])
def list_sellers(db: DbSession, _: AdminUser) -> list[SellerResponse]:
    return AdminService(db).list_sellers()


@router.patch("/sellers/{seller_id}", response_model=SellerResponse)
def moderate_seller(
    seller_id: str,
    payload: SellerModerationUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> SellerResponse:
    return AdminService(db).moderate_seller(seller_id, payload, current_user.id)


@router.get("/sellers/{seller_id}/analytics")
def seller_analytics(seller_id: str, db: DbSession, _: AdminUser) -> dict[str, int | float | str]:
    return AdminService(db).seller_analytics(seller_id)


@router.get("/products", response_model=list[ProductListResponse])
def list_products(
    db: DbSession,
    _: AdminUser,
    status_filter: ProductStatus | None = None,
) -> list[ProductListResponse]:
    return AdminService(db).list_products(status_filter)


@router.patch("/products/{product_id}", response_model=ProductListResponse)
def moderate_product(
    product_id: str,
    payload: ProductModerationUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> ProductListResponse:
    return AdminService(db).moderate_product(product_id, payload, current_user.id)


@router.patch("/products/{product_id}/brand", response_model=ProductListResponse)
def manage_brand(
    product_id: str,
    payload: BrandPayload,
    db: DbSession,
    current_user: AdminUser,
) -> ProductListResponse:
    return AdminService(db).manage_brand(product_id, payload, current_user.id)


@router.get("/catalog", response_model=CatalogAdminResponse)
def catalog_admin(db: DbSession, _: AdminUser) -> CatalogAdminResponse:
    categories, brands, coupons = AdminService(db).list_catalog_admin()
    return CatalogAdminResponse(categories=categories, brands=brands, coupons=coupons)


@router.post("/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(payload: CouponPayload, db: DbSession, current_user: AdminUser) -> CouponResponse:
    return AdminService(db).create_coupon(payload, current_user.id)


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(db: DbSession, _: AdminUser) -> list[OrderResponse]:
    return AdminService(db).list_orders()


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    payload: AdminOrderStatusUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> OrderResponse:
    return AdminService(db).update_order_status(order_id, payload.status, current_user.id)


@router.post("/orders/{order_id}/refund", response_model=OrderResponse)
def refund_order(order_id: str, db: DbSession, current_user: AdminUser) -> OrderResponse:
    return AdminService(db).refund_order(order_id, current_user.id)


@router.post("/orders/{order_id}/shipments", response_model=ShipmentResponse)
def create_shipment(
    order_id: str,
    payload: ShipmentPayload,
    db: DbSession,
    current_user: AdminUser,
) -> ShipmentResponse:
    return AdminService(db).create_shipment(order_id, payload, current_user.id)


@router.get("/shipments", response_model=list[ShipmentResponse])
def list_shipments(db: DbSession, _: AdminUser) -> list[ShipmentResponse]:
    return AdminService(db).list_shipments()


@router.get("/reviews", response_model=list[ReviewResponse])
def list_reviews(db: DbSession, _: AdminUser) -> list[ReviewResponse]:
    return AdminService(db).list_reviews()


@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
def moderate_review(
    review_id: str,
    payload: ReviewModerationUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> ReviewResponse:
    return AdminService(db).moderate_review(review_id, payload, current_user.id)


@router.get("/reports/{name}", response_model=ReportResponse)
def report(name: str, db: DbSession, _: AdminUser) -> ReportResponse:
    return AdminService(db).report(name)


@router.get("/reports/{name}.csv")
def report_csv(name: str, db: DbSession, _: AdminUser) -> Response:
    return Response(AdminService(db).report_csv(name), media_type="text/csv")


@router.get("/reports/{name}.pdf")
def report_pdf(name: str, db: DbSession, _: AdminUser) -> Response:
    return Response(AdminService(db).report_pdf_placeholder(name), media_type="application/pdf")


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(db: DbSession, _: AdminUser) -> list[NotificationResponse]:
    return AdminService(db).list_notifications()


@router.post("/notifications", response_model=NotificationResponse)
def create_notification(
    payload: NotificationPayload,
    db: DbSession,
    current_user: AdminUser,
) -> NotificationResponse:
    return AdminService(db).create_notification(payload, current_user.id)


@router.get("/payments", response_model=list[PaymentResponse])
def list_payments(db: DbSession, _: AdminUser) -> list[PaymentResponse]:
    return AdminService(db).list_payments()


@router.post("/payments/stripe-sandbox", response_model=PaymentResponse)
def create_payment_intent(
    payload: PaymentIntentPayload,
    db: DbSession,
    current_user: AdminUser,
) -> PaymentResponse:
    return AdminService(db).create_payment_intent(payload, current_user.id)


@router.patch("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: str,
    payload: PaymentUpdatePayload,
    db: DbSession,
    current_user: AdminUser,
) -> PaymentResponse:
    return AdminService(db).update_payment(payment_id, payload, current_user.id)


@router.get("/ai/products/{product_id}/recommendations", response_model=RecommendationResponse)
def recommendations(product_id: str, db: DbSession, _: AdminUser) -> RecommendationResponse:
    return AdminService(db).recommendations(product_id)


@router.post(
    "/ai/products/{product_id}/description",
    response_model=GeneratedDescriptionResponse,
)
def generate_description(
    product_id: str,
    db: DbSession,
    _: AdminUser,
) -> GeneratedDescriptionResponse:
    return AdminService(db).generate_description(product_id)


@router.get("/ai/products/{product_id}/reviews", response_model=ReviewSummaryResponse)
def review_summary(product_id: str, db: DbSession, _: AdminUser) -> ReviewSummaryResponse:
    return AdminService(db).review_summary(product_id)


@review_router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    db: DbSession,
    current_user: AuthenticatedUser,
) -> ReviewResponse:
    return AdminService(db).create_review(current_user.id, payload)
