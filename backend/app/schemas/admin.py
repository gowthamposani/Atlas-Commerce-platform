from datetime import datetime

from app.models.marketplace import (
    NotificationType,
    OrderStatus,
    PaymentStatus,
    ProductStatus,
    ReviewStatus,
    SellerModerationStatus,
    ShipmentStatus,
)
from app.models.user import UserRole
from app.schemas.marketplace import CategoryResponse, OrderResponse, ProductListResponse
from app.schemas.validation import clean_optional_text, clean_text, validate_code
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AdminStatsResponse(BaseModel):
    total_customers: int
    total_sellers: int
    total_products: int
    total_categories: int = 0
    total_orders: int
    revenue: float = 0
    revenue_summary: float
    pending_orders: int
    pending_seller_approvals: int
    pending_products: int = 0
    pending_reviews: int = 0
    inventory_alerts: int = 0


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserStatusUpdate(BaseModel):
    is_active: bool


class SellerModerationUpdate(BaseModel):
    status: SellerModerationStatus


class ProductModerationUpdate(BaseModel):
    status: ProductStatus | None = None
    is_visible: bool | None = None
    is_featured: bool | None = None
    brand: str | None = Field(default=None, max_length=120)

    @field_validator("brand")
    @classmethod
    def validate_brand(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Brand")


class BrandPayload(BaseModel):
    brand: str = Field(min_length=1, max_length=120)

    @field_validator("brand")
    @classmethod
    def validate_brand(cls, value: str) -> str:
        return clean_text(value, field_name="Brand") or ""


class CouponPayload(BaseModel):
    code: str = Field(min_length=2, max_length=60)
    discount_type: str = Field(pattern="^(percent|fixed)$")
    discount_value: float = Field(gt=0, allow_inf_nan=False)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def validate_coupon_code(cls, value: str) -> str:
        return validate_code(value, field_name="Coupon code")

    @model_validator(mode="after")
    def validate_discount_value(self) -> "CouponPayload":
        if self.discount_type == "percent" and self.discount_value > 100:
            raise ValueError("Percent discount must be between 0 and 100")
        return self


class CouponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    discount_type: str
    discount_value: float
    is_active: bool
    created_at: datetime


class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=160)
    body: str = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Review title")

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        return clean_text(value, field_name="Review body") or ""


class ReviewModerationUpdate(BaseModel):
    status: ReviewStatus
    report_reason: str | None = None

    @field_validator("report_reason")
    @classmethod
    def validate_report_reason(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Report reason")


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    user_id: str
    rating: int
    title: str | None
    body: str
    status: ReviewStatus
    report_reason: str | None
    created_at: datetime
    updated_at: datetime


class ReportResponse(BaseModel):
    name: str
    generated_at: datetime
    rows: list[dict[str, str | int | float | None]]


class NotificationPayload(BaseModel):
    user_id: str | None = None
    type: NotificationType = NotificationType.ADMIN
    title: str = Field(min_length=1, max_length=180)
    message: str = Field(min_length=1)

    @field_validator("title", "message")
    @classmethod
    def validate_text(cls, value: str, info) -> str:
        return clean_text(value, field_name=str(info.field_name).title()) or ""


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime


class PaymentIntentPayload(BaseModel):
    order_id: str
    provider_reference: str | None = Field(default=None, max_length=160)

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, value: str) -> str:
        return clean_text(value, field_name="Order ID") or ""

    @field_validator("provider_reference")
    @classmethod
    def validate_provider_reference(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Provider reference")


class PaymentUpdatePayload(BaseModel):
    status: PaymentStatus


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_id: str
    provider: str
    provider_reference: str
    amount: float
    currency: str
    status: PaymentStatus
    raw_response: dict[str, str]
    created_at: datetime
    updated_at: datetime


class ShipmentPayload(BaseModel):
    provider: str = Field(default="manual", max_length=80)
    label_url: str | None = Field(default=None, max_length=500)
    tracking_number: str | None = Field(default=None, max_length=120)
    status: ShipmentStatus = ShipmentStatus.LABEL_CREATED

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        return clean_text(value, field_name="Shipment provider") or ""

    @field_validator("label_url", "tracking_number")
    @classmethod
    def validate_optional_text_fields(cls, value: str | None, info) -> str | None:
        return clean_optional_text(value, field_name=str(info.field_name).replace("_", " ").title())


class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_id: str
    provider: str
    label_url: str | None
    tracking_number: str | None
    status: ShipmentStatus
    created_at: datetime
    updated_at: datetime


class RecommendationResponse(BaseModel):
    product_id: str
    recommendations: list[ProductListResponse]


class GeneratedDescriptionResponse(BaseModel):
    product_id: str
    description: str


class ReviewSummaryResponse(BaseModel):
    product_id: str
    average_rating: float
    review_count: int
    summary: str


class AdminOrderStatusUpdate(BaseModel):
    status: OrderStatus


class AdminDashboardResponse(BaseModel):
    stats: AdminStatsResponse
    recent_orders: list[OrderResponse]
    pending_sellers: int
    pending_products: int
    pending_reviews: int = 0
    inventory_alerts: int = 0
    top_selling_products: list[dict[str, str | int | float]] = Field(default_factory=list)
    top_sellers: list[dict[str, str | int | float]] = Field(default_factory=list)


class CatalogAdminResponse(BaseModel):
    categories: list[CategoryResponse]
    brands: list[str]
    coupons: list[CouponResponse]
