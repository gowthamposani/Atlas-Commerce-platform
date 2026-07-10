from datetime import datetime

from app.models.marketplace import OrderStatus, ProductStatus
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    is_active: bool | None = None


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


class SellerUpdate(BaseModel):
    store_name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = None
    is_active: bool | None = None


class SellerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    store_name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductImagePayload(BaseModel):
    url: str = Field(min_length=1, max_length=500)
    alt_text: str | None = Field(default=None, max_length=180)
    sort_order: int = Field(default=0, ge=0)
    is_primary: bool = False


class ProductImageResponse(ProductImagePayload):
    model_config = ConfigDict(from_attributes=True)

    id: str


class ProductVariantPayload(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    price_delta: float = Field(default=0, ge=0)
    attributes: dict[str, str] = Field(default_factory=dict)
    is_active: bool = True


class ProductVariantResponse(ProductVariantPayload):
    model_config = ConfigDict(from_attributes=True)

    id: str


class ProductCreate(BaseModel):
    category_id: str
    name: str = Field(min_length=1, max_length=180)
    description: str = Field(min_length=1)
    base_price: float = Field(gt=0)
    status: ProductStatus = ProductStatus.ACTIVE
    images: list[ProductImagePayload] = Field(default_factory=list)
    variants: list[ProductVariantPayload] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    category_id: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = None
    base_price: float | None = Field(default=None, gt=0)
    status: ProductStatus | None = None
    images: list[ProductImagePayload] | None = None
    variants: list[ProductVariantPayload] | None = None


class ProductListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    seller_id: str
    category_id: str
    name: str
    slug: str
    description: str
    status: ProductStatus
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


class WarehouseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    state: str | None = Field(default=None, min_length=1, max_length=120)
    country: str | None = Field(default=None, min_length=2, max_length=80)
    is_active: bool | None = None


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


class CheckoutCreate(BaseModel):
    shipping_address_id: str
    billing_address: BillingAddressPayload
    coupon_code: str | None = Field(default=None, max_length=60)
    payment_method: str = Field(default="placeholder", max_length=80)


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
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class SellerDashboardResponse(BaseModel):
    seller: SellerResponse
    product_count: int
    active_product_count: int
    total_stock: int
    order_count: int
