from datetime import datetime

from app.models.marketplace import OrderStatus, ProductStatus, SellerModerationStatus
from app.schemas.validation import (
    clean_optional_required_text,
    clean_optional_text,
    clean_text,
    validate_code,
    validate_person_name,
    validate_postal_code,
    validate_sku,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return clean_text(value, field_name="Category name") or ""

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Category description")


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        return clean_optional_required_text(value, field_name="Category name")

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Category description")


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SellerCreate(BaseModel):
    store_name: str = Field(min_length=2, max_length=160)
    description: str | None = None

    @field_validator("store_name")
    @classmethod
    def validate_store_name(cls, value: str) -> str:
        return clean_text(value, field_name="Store name") or ""

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Store description")


class SellerUpdate(BaseModel):
    store_name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = None
    is_active: bool | None = None

    @field_validator("store_name")
    @classmethod
    def validate_store_name(cls, value: str | None) -> str | None:
        return clean_optional_required_text(value, field_name="Store name")

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Store description")


class SellerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    store_name: str
    slug: str
    description: str | None
    moderation_status: SellerModerationStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductImagePayload(BaseModel):
    url: str = Field(min_length=1, max_length=500)
    alt_text: str | None = Field(default=None, max_length=180)
    sort_order: int = Field(default=0, ge=0)
    is_primary: bool = False

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        cleaned = clean_text(value, field_name="Image URL") or ""
        has_invalid_scheme = not cleaned.startswith(("http://", "https://"))
        has_whitespace = any(char.isspace() for char in cleaned)
        if has_invalid_scheme or has_whitespace:
            raise ValueError("Image URL must be a valid http or https URL without whitespace")
        return cleaned

    @field_validator("alt_text")
    @classmethod
    def validate_alt_text(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Image alt text")


class ProductImageResponse(ProductImagePayload):
    model_config = ConfigDict(from_attributes=True)

    id: str


class ProductVariantPayload(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    price_delta: float = Field(default=0, ge=0, allow_inf_nan=False)
    attributes: dict[str, str] = Field(default_factory=dict)
    is_active: bool = True

    @field_validator("sku")
    @classmethod
    def validate_variant_sku(cls, value: str) -> str:
        return validate_sku(value)

    @field_validator("name")
    @classmethod
    def validate_variant_name(cls, value: str) -> str:
        return clean_text(value, field_name="Variant name") or ""


class ProductVariantResponse(ProductVariantPayload):
    model_config = ConfigDict(from_attributes=True)

    id: str


class ProductCreate(BaseModel):
    category_id: str
    name: str = Field(min_length=1, max_length=180)
    description: str = Field(min_length=1)
    brand: str | None = Field(default=None, max_length=120)
    base_price: float = Field(gt=0, allow_inf_nan=False)
    status: ProductStatus = ProductStatus.ACTIVE
    images: list[ProductImagePayload] = Field(default_factory=list)
    variants: list[ProductVariantPayload] = Field(default_factory=list)

    @field_validator("category_id", "name", "description")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return clean_text(value, field_name=str(info.field_name).replace("_", " ").title()) or ""

    @field_validator("brand")
    @classmethod
    def validate_brand(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Brand")

    @model_validator(mode="after")
    def validate_variant_skus(self) -> "ProductCreate":
        skus = [variant.sku for variant in self.variants]
        if len(skus) != len(set(skus)):
            raise ValueError("Variant SKUs must be unique")
        return self


class ProductUpdate(BaseModel):
    category_id: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = None
    brand: str | None = Field(default=None, max_length=120)
    base_price: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    status: ProductStatus | None = None
    is_visible: bool | None = None
    is_featured: bool | None = None
    images: list[ProductImagePayload] | None = None
    variants: list[ProductVariantPayload] | None = None

    @field_validator("category_id", "name", "description")
    @classmethod
    def validate_optional_text_fields(cls, value: str | None, info) -> str | None:
        return clean_optional_required_text(
            value,
            field_name=str(info.field_name).replace("_", " ").title(),
        )

    @field_validator("brand")
    @classmethod
    def validate_brand(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Brand")

    @model_validator(mode="after")
    def validate_variant_skus(self) -> "ProductUpdate":
        if self.variants is None:
            return self
        skus = [variant.sku for variant in self.variants]
        if len(skus) != len(set(skus)):
            raise ValueError("Variant SKUs must be unique")
        return self


class ProductListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    seller_id: str
    category_id: str
    name: str
    slug: str
    description: str
    brand: str | None
    status: ProductStatus
    is_visible: bool
    is_featured: bool
    base_price: float
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse
    seller: SellerResponse
    images: list[ProductImageResponse]


class ProductDetailResponse(ProductListResponse):
    variants: list[ProductVariantResponse]
    available_quantity: int


class ProductPageResponse(BaseModel):
    items: list[ProductListResponse]
    total: int
    page: int
    page_size: int


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    code: str = Field(min_length=1, max_length=80)
    city: str = Field(min_length=1, max_length=120)
    state: str = Field(min_length=1, max_length=120)
    country: str = Field(default="US", min_length=2, max_length=80)

    @field_validator("name", "city", "state", "country")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return clean_text(value, field_name=str(info.field_name).replace("_", " ").title()) or ""

    @field_validator("code")
    @classmethod
    def validate_warehouse_code(cls, value: str) -> str:
        return validate_code(value, field_name="Warehouse code")

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return value.upper()


class WarehouseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    state: str | None = Field(default=None, min_length=1, max_length=120)
    country: str | None = Field(default=None, min_length=2, max_length=80)
    is_active: bool | None = None

    @field_validator("name", "city", "state", "country")
    @classmethod
    def validate_optional_text_fields(cls, value: str | None, info) -> str | None:
        cleaned = clean_optional_required_text(
            value,
            field_name=str(info.field_name).replace("_", " ").title(),
        )
        if info.field_name == "country" and cleaned is not None:
            return cleaned.upper()
        return cleaned


class WarehouseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    seller_id: str
    name: str
    code: str
    city: str
    state: str
    country: str
    is_active: bool
    created_at: datetime


class InventoryUpsert(BaseModel):
    product_id: str
    variant_id: str | None = None
    warehouse_id: str
    quantity: int = Field(ge=0)
    reserved_quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_reserved_quantity(self) -> "InventoryUpsert":
        if self.reserved_quantity > self.quantity:
            raise ValueError("Reserved quantity cannot exceed total quantity")
        return self


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    variant_id: str | None
    warehouse_id: str
    quantity: int
    reserved_quantity: int
    reorder_level: int
    updated_at: datetime


class InventoryValidationRequest(BaseModel):
    product_id: str
    variant_id: str | None = None
    quantity: int = Field(gt=0)


class InventoryValidationResponse(BaseModel):
    product_id: str
    variant_id: str | None
    requested_quantity: int
    available_quantity: int
    is_available: bool


class WishlistAdd(BaseModel):
    product_id: str
    variant_id: str | None = None


class WishlistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    variant_id: str | None
    created_at: datetime
    product: ProductListResponse


class CartAdd(BaseModel):
    product_id: str
    variant_id: str | None = None
    quantity: int = Field(default=1, gt=0)


class CartQuantityUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    variant_id: str | None
    quantity: int
    unit_price: float
    line_total: float
    product: ProductListResponse
    variant: ProductVariantResponse | None = None


class CartSummaryResponse(BaseModel):
    items: list[CartItemResponse]
    subtotal: float
    item_count: int
    is_inventory_valid: bool


class BillingAddressPayload(BaseModel):
    recipient_name: str = Field(min_length=1, max_length=160)
    line1: str = Field(min_length=1, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=120)
    state: str = Field(min_length=1, max_length=120)
    postal_code: str = Field(min_length=1, max_length=30)
    country: str = Field(default="US", min_length=2, max_length=80)

    @field_validator("recipient_name")
    @classmethod
    def validate_recipient(cls, value: str) -> str:
        return validate_person_name(value, field_name="Recipient name")

    @field_validator("line1", "city", "state", "country")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return clean_text(value, field_name=str(info.field_name).replace("_", " ").title()) or ""

    @field_validator("line2")
    @classmethod
    def validate_optional_line2(cls, value: str | None) -> str | None:
        return clean_optional_text(value, field_name="Address line 2")

    @model_validator(mode="after")
    def validate_postal(self) -> "BillingAddressPayload":
        self.country = self.country.upper()
        self.postal_code = validate_postal_code(self.postal_code, country=self.country)
        return self


class CheckoutCreate(BaseModel):
    shipping_address_id: str
    billing_address: BillingAddressPayload
    coupon_code: str | None = Field(default=None, max_length=60)
    payment_method: str = Field(default="placeholder", max_length=80)

    @field_validator("shipping_address_id", "payment_method")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return clean_text(value, field_name=str(info.field_name).replace("_", " ").title()) or ""

    @field_validator("coupon_code")
    @classmethod
    def validate_coupon_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_code(value, field_name="Coupon code")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    variant_id: str | None
    seller_id: str
    product_name: str
    variant_name: str | None
    sku: str | None
    unit_price: float
    quantity: int
    line_total: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_number: str
    user_id: str
    shipping_address_id: str
    billing_address: dict[str, str | None]
    status: OrderStatus
    subtotal: float
    tax_amount: float
    shipping_charge: float
    discount_amount: float
    total_amount: float
    coupon_code: str | None
    payment_method: str
    payment_status: str
    shipment_status: str
    tracking_number: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class SellerTopProductResponse(BaseModel):
    product_id: str
    name: str
    units_sold: int
    revenue: float


class SellerDashboardResponse(BaseModel):
    seller: SellerResponse
    product_count: int
    active_product_count: int
    total_stock: int
    order_count: int
    revenue: float = 0
    low_stock_count: int = 0
    inventory_alerts: int = 0
    recent_orders: list[OrderResponse] = Field(default_factory=list)
    top_products: list[SellerTopProductResponse] = Field(default_factory=list)
