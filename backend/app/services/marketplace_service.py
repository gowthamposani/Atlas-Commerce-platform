from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4

from app.core.exceptions import bad_request, forbidden, not_found
from app.models.address import Address
from app.models.marketplace import (
    CartItem,
    Category,
    Coupon,
    DiscountType,
    InventoryItem,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductStatus,
    SellerProfile,
    Warehouse,
    WishlistItem,
)
from app.repositories.marketplace_repository import (
    CatalogRepository,
    InventoryRepository,
    OrderRepository,
    SellerRepository,
    ShoppingRepository,
)
from app.schemas.marketplace import (
    CartAdd,
    CartItemResponse,
    CartQuantityUpdate,
    CartSummaryResponse,
    CategoryCreate,
    CategoryUpdate,
    CheckoutCreate,
    InventoryUpsert,
    InventoryValidationRequest,
    InventoryValidationResponse,
    OrderResponse,
    OrderStatusUpdate,
    ProductCreate,
    ProductDetailResponse,
    ProductPageResponse,
    ProductUpdate,
    SellerCreate,
    SellerDashboardResponse,
    SellerUpdate,
    WarehouseCreate,
    WarehouseUpdate,
    WishlistAdd,
)
from app.utils.slug import slugify
from sqlalchemy.orm import Session

Money = Decimal


def to_money(value: float | Decimal | int) -> Money:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def unique_slug(base_value: str, exists: Callable[[str], bool]) -> str:
    base_slug = slugify(base_value)
    slug = base_slug
    counter = 2
    while exists(slug):
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class CatalogService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.catalog = CatalogRepository(db)
        self.inventory = InventoryRepository(db)

    def list_categories(self) -> list[Category]:
        return self.catalog.list_categories()

    def create_category(self, payload: CategoryCreate) -> Category:
        slug = unique_slug(payload.name, lambda value: self.catalog.slug_exists(Category, value))
        category = self.catalog.create_category(slug=slug, data=payload.model_dump())
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category(self, category_id: str, payload: CategoryUpdate) -> Category:
        category = self.catalog.get_category(category_id)
        if category is None:
            raise not_found("Category was not found")
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != category.name:
            data["slug"] = unique_slug(
                str(data["name"]),
                lambda value: self.catalog.slug_exists(Category, value),
            )
        for field, value in data.items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: str) -> None:
        category = self.catalog.get_category(category_id)
        if category is None:
            raise not_found("Category was not found")
        self.db.delete(category)
        self.db.commit()

    def search_products(
        self,
        *,
        search: str | None,
        category_id: str | None,
        seller_id: str | None,
        min_price: float | None,
        max_price: float | None,
        page: int,
        page_size: int,
    ) -> ProductPageResponse:
        items, total = self.catalog.list_products(
            search=search,
            category_id=category_id,
            seller_id=seller_id,
            min_price=min_price,
            max_price=max_price,
            page=page,
            page_size=page_size,
        )
        return ProductPageResponse(items=items, total=total, page=page, page_size=page_size)

    def product_details(self, product_id: str) -> ProductDetailResponse:
        product = self.catalog.get_product(product_id)
        if product is None:
            raise not_found("Product was not found")
        return ProductDetailResponse.model_validate(
            {
                **product.__dict__,
                "category": product.category,
                "seller": product.seller,
                "images": product.images,
                "variants": product.variants,
                "available_quantity": self.inventory.total_available_quantity(product.id),
            },
        )


class SellerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.catalog = CatalogRepository(db)
        self.sellers = SellerRepository(db)

    def get_or_create_profile(self, *, user_id: str, payload: SellerCreate) -> SellerProfile:
        existing = self.sellers.get_by_user_id(user_id)
        if existing is not None:
            return existing
        slug = unique_slug(
            payload.store_name,
            lambda value: self.catalog.slug_exists(SellerProfile, value),
        )
        seller = self.sellers.create(user_id=user_id, slug=slug, data=payload.model_dump())
        self.db.commit()
        self.db.refresh(seller)
        return seller

    def update_profile(self, *, user_id: str, payload: SellerUpdate) -> SellerProfile:
        seller = self.require_seller(user_id)
        data = payload.model_dump(exclude_unset=True)
        if "store_name" in data and data["store_name"] != seller.store_name:
            data["slug"] = unique_slug(
                str(data["store_name"]),
                lambda value: self.catalog.slug_exists(SellerProfile, value),
            )
        for field, value in data.items():
            setattr(seller, field, value)
        self.db.commit()
        self.db.refresh(seller)
        return seller

    def dashboard(self, user_id: str) -> SellerDashboardResponse:
        seller = self.require_seller(user_id)
        product_count, active_count, total_stock, order_count = self.sellers.dashboard_counts(
            seller.id,
        )
        return SellerDashboardResponse(
            seller=seller,
            product_count=product_count,
            active_product_count=active_count,
            total_stock=total_stock,
            order_count=order_count,
        )

    def public_store(self, seller_id: str) -> SellerProfile:
        seller = self.sellers.get_by_id(seller_id)
        if seller is None or not seller.is_active:
            raise not_found("Seller store was not found")
        return seller

    def list_products(self, user_id: str) -> list[Product]:
        seller = self.require_seller(user_id)
        return self.sellers.list_products(seller.id)

    def create_product(self, *, user_id: str, payload: ProductCreate) -> Product:
        seller = self.require_seller(user_id)
        category = self.catalog.get_category(payload.category_id)
        if category is None or not category.is_active:
            raise bad_request("A valid active category is required")
        slug = unique_slug(payload.name, lambda value: self.catalog.slug_exists(Product, value))
        data = payload.model_dump(exclude={"images", "variants"})
        data["base_price"] = to_money(data["base_price"])
        product = self.sellers.create_product(
            seller_id=seller.id,
            slug=slug,
            data=data,
            images=[image.model_dump() for image in payload.images],
            variants=[
                {**variant.model_dump(), "price_delta": to_money(variant.price_delta)}
                for variant in payload.variants
            ],
        )
        self.db.commit()
        self.db.refresh(product)
        return self.sellers.get_product(seller_id=seller.id, product_id=product.id) or product

    def update_product(self, *, user_id: str, product_id: str, payload: ProductUpdate) -> Product:
        seller = self.require_seller(user_id)
        product = self.sellers.get_product(seller_id=seller.id, product_id=product_id)
        if product is None:
            raise not_found("Product was not found")
        data = payload.model_dump(exclude_unset=True, exclude={"images", "variants"})
        if "category_id" in data:
            category = self.catalog.get_category(str(data["category_id"]))
            if category is None or not category.is_active:
                raise bad_request("A valid active category is required")
        if "name" in data and data["name"] != product.name:
            data["slug"] = unique_slug(
                str(data["name"]),
                lambda value: self.catalog.slug_exists(Product, value),
            )
        if "base_price" in data:
            data["base_price"] = to_money(data["base_price"])
        for field, value in data.items():
            setattr(product, field, value)
        self.sellers.replace_product_media(
            product,
            images=(
                [image.model_dump() for image in payload.images]
                if payload.images is not None
                else None
            ),
            variants=[
                {**variant.model_dump(), "price_delta": to_money(variant.price_delta)}
                for variant in payload.variants
            ]
            if payload.variants is not None
            else None,
        )
        self.db.commit()
        refreshed = self.sellers.get_product(seller_id=seller.id, product_id=product.id)
        if refreshed is None:
            raise not_found("Product was not found")
        return refreshed

    def delete_product(self, *, user_id: str, product_id: str) -> None:
        seller = self.require_seller(user_id)
        product = self.sellers.get_product(seller_id=seller.id, product_id=product_id)
        if product is None:
            raise not_found("Product was not found")
        product.status = ProductStatus.ARCHIVED
        self.db.commit()

    def require_seller(self, user_id: str) -> SellerProfile:
        seller = self.sellers.get_by_user_id(user_id)
        if seller is None:
            raise bad_request("Register as a seller before using seller features")
        if not seller.is_active:
            raise forbidden("Seller profile is inactive")
        return seller


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.inventory = InventoryRepository(db)
        self.sellers = SellerRepository(db)

    def list_warehouses(self, user_id: str) -> list[Warehouse]:
        seller = SellerService(self.db).require_seller(user_id)
        return self.inventory.list_warehouses(seller.id)

    def create_warehouse(self, *, user_id: str, payload: WarehouseCreate) -> Warehouse:
        seller = SellerService(self.db).require_seller(user_id)
        warehouse = self.inventory.create_warehouse(seller_id=seller.id, data=payload.model_dump())
        self.db.commit()
        self.db.refresh(warehouse)
        return warehouse

    def update_warehouse(
        self,
        *,
        user_id: str,
        warehouse_id: str,
        payload: WarehouseUpdate,
    ) -> Warehouse:
        seller = SellerService(self.db).require_seller(user_id)
        warehouse = self.inventory.get_warehouse(seller_id=seller.id, warehouse_id=warehouse_id)
        if warehouse is None:
            raise not_found("Warehouse was not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(warehouse, field, value)
        self.db.commit()
        self.db.refresh(warehouse)
        return warehouse

    def upsert_stock(self, *, user_id: str, payload: InventoryUpsert) -> InventoryItem:
        seller = SellerService(self.db).require_seller(user_id)
        product = self.sellers.get_product(seller_id=seller.id, product_id=payload.product_id)
        if product is None:
            raise bad_request("Product must belong to the current seller")
        if payload.variant_id and not any(
            variant.id == payload.variant_id for variant in product.variants
        ):
            raise bad_request("Variant must belong to the product")
        warehouse = self.inventory.get_warehouse(
            seller_id=seller.id,
            warehouse_id=payload.warehouse_id,
        )
        if warehouse is None:
            raise bad_request("Warehouse must belong to the current seller")

        item = self.inventory.get_inventory_item(
            product_id=payload.product_id,
            variant_id=payload.variant_id,
            warehouse_id=payload.warehouse_id,
        )
        if item is None:
            item = InventoryItem(**payload.model_dump())
            self.db.add(item)
        else:
            item.quantity = payload.quantity
            item.reserved_quantity = payload.reserved_quantity
            item.reorder_level = payload.reorder_level
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_stock(self, user_id: str) -> list[InventoryItem]:
        seller = SellerService(self.db).require_seller(user_id)
        return self.inventory.list_inventory(seller.id)

    def validate_stock(self, payload: InventoryValidationRequest) -> InventoryValidationResponse:
        available = self.inventory.available_quantity(
            product_id=payload.product_id,
            variant_id=payload.variant_id,
        )
        return InventoryValidationResponse(
            product_id=payload.product_id,
            variant_id=payload.variant_id,
            requested_quantity=payload.quantity,
            available_quantity=available,
            is_available=available >= payload.quantity,
        )


class ShoppingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.catalog = CatalogRepository(db)
        self.inventory = InventoryRepository(db)
        self.shopping = ShoppingRepository(db)

    def add_to_wishlist(self, *, user_id: str, payload: WishlistAdd) -> WishlistItem:
        product = self._active_product(payload.product_id)
        self._validate_variant(product, payload.variant_id)
        existing = self.shopping.get_wishlist_item(
            user_id=user_id,
            product_id=payload.product_id,
            variant_id=payload.variant_id,
        )
        if existing is not None:
            return existing
        item = WishlistItem(user_id=user_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_wishlist(self, user_id: str) -> list[WishlistItem]:
        return self.shopping.list_wishlist(user_id)

    def remove_wishlist_item(self, *, user_id: str, item_id: str) -> None:
        item = self.shopping.get_wishlist_by_id(user_id=user_id, item_id=item_id)
        if item is None:
            raise not_found("Wishlist item was not found")
        self.db.delete(item)
        self.db.commit()

    def move_wishlist_to_cart(self, *, user_id: str, item_id: str) -> CartSummaryResponse:
        item = self.shopping.get_wishlist_by_id(user_id=user_id, item_id=item_id)
        if item is None:
            raise not_found("Wishlist item was not found")
        self.add_to_cart(
            user_id=user_id,
            payload=CartAdd(product_id=item.product_id, variant_id=item.variant_id, quantity=1),
        )
        self.db.delete(item)
        self.db.commit()
        return self.cart_summary(user_id)

    def add_to_cart(self, *, user_id: str, payload: CartAdd) -> CartSummaryResponse:
        product = self._active_product(payload.product_id)
        self._validate_variant(product, payload.variant_id)
        available = self.inventory.available_quantity(
            product_id=payload.product_id,
            variant_id=payload.variant_id,
        )
        existing = self.shopping.get_cart_item(
            user_id=user_id,
            product_id=payload.product_id,
            variant_id=payload.variant_id,
        )
        requested_quantity = payload.quantity + (existing.quantity if existing else 0)
        if available < requested_quantity:
            raise bad_request("Not enough inventory for the requested quantity")
        if existing is None:
            self.db.add(CartItem(user_id=user_id, **payload.model_dump()))
        else:
            existing.quantity = requested_quantity
        self.db.commit()
        return self.cart_summary(user_id)

    def update_cart_item(
        self,
        *,
        user_id: str,
        item_id: str,
        payload: CartQuantityUpdate,
    ) -> CartSummaryResponse:
        item = self.shopping.get_cart_by_id(user_id=user_id, item_id=item_id)
        if item is None:
            raise not_found("Cart item was not found")
        available = self.inventory.available_quantity(
            product_id=item.product_id,
            variant_id=item.variant_id,
        )
        if available < payload.quantity:
            raise bad_request("Not enough inventory for the requested quantity")
        item.quantity = payload.quantity
        self.db.commit()
        return self.cart_summary(user_id)

    def remove_cart_item(self, *, user_id: str, item_id: str) -> CartSummaryResponse:
        item = self.shopping.get_cart_by_id(user_id=user_id, item_id=item_id)
        if item is None:
            raise not_found("Cart item was not found")
        self.db.delete(item)
        self.db.commit()
        return self.cart_summary(user_id)

    def cart_summary(self, user_id: str) -> CartSummaryResponse:
        items = self.shopping.list_cart(user_id)
        response_items = [self._cart_item_response(item) for item in items]
        subtotal = sum(to_money(item.line_total) for item in response_items)
        is_inventory_valid = all(
            self.inventory.available_quantity(
                product_id=item.product_id,
                variant_id=item.variant_id,
            )
            >= item.quantity
            for item in items
        )
        return CartSummaryResponse(
            items=response_items,
            subtotal=float(subtotal),
            item_count=sum(item.quantity for item in items),
            is_inventory_valid=is_inventory_valid,
        )

    def _active_product(self, product_id: str) -> Product:
        product = self.catalog.get_product(product_id)
        if product is None:
            raise not_found("Product was not found")
        return product

    @staticmethod
    def _validate_variant(product: Product, variant_id: str | None) -> None:
        if variant_id is None:
            return
        if not any(variant.id == variant_id and variant.is_active for variant in product.variants):
            raise bad_request("Variant is not available for this product")

    @staticmethod
    def _unit_price(item: CartItem) -> Money:
        price = to_money(item.product.base_price)
        if item.variant is not None:
            price += to_money(item.variant.price_delta)
        return price

    def _cart_item_response(self, item: CartItem) -> CartItemResponse:
        unit_price = self._unit_price(item)
        line_total = unit_price * item.quantity
        return CartItemResponse.model_validate(
            {
                **item.__dict__,
                "unit_price": float(unit_price),
                "line_total": float(line_total),
                "product": item.product,
                "variant": item.variant,
            },
        )


class OrderService:
    TAX_RATE = Decimal("0.08")
    SHIPPING_CHARGE = Decimal("8.99")
    FREE_SHIPPING_MINIMUM = Decimal("75.00")
    STATUS_FLOW = [
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.PACKED,
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
    ]

    def __init__(self, db: Session) -> None:
        self.db = db
        self.inventory = InventoryRepository(db)
        self.orders = OrderRepository(db)
        self.shopping = ShoppingRepository(db)

    def create_order(self, *, user_id: str, payload: CheckoutCreate) -> OrderResponse:
        shipping_address = self._shipping_address(user_id, payload.shipping_address_id)
        cart_summary = ShoppingService(self.db).cart_summary(user_id)
        if not cart_summary.items:
            raise bad_request("Cart is empty")
        if not cart_summary.is_inventory_valid:
            raise bad_request("Cart inventory is no longer available")

        subtotal = to_money(cart_summary.subtotal)
        tax_amount = (subtotal * self.TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        shipping_charge = (
            Decimal("0.00") if subtotal >= self.FREE_SHIPPING_MINIMUM else self.SHIPPING_CHARGE
        )
        coupon = self._coupon(payload.coupon_code)
        discount_amount = self._discount_amount(coupon, subtotal)
        total_amount = max(
            subtotal + tax_amount + shipping_charge - discount_amount,
            Decimal("0.00"),
        )

        order = Order(
            order_number=f"ATL-{uuid4().hex[:10].upper()}",
            user_id=user_id,
            shipping_address_id=shipping_address.id,
            billing_address=payload.billing_address.model_dump(),
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_charge=shipping_charge,
            discount_amount=discount_amount,
            total_amount=total_amount,
            coupon_code=coupon.code if coupon else None,
            payment_method=payload.payment_method,
            payment_status="pending",
            status=OrderStatus.PENDING,
        )

        cart_items = self.shopping.list_cart(user_id)
        for item in cart_items:
            unit_price = ShoppingService._unit_price(item)
            line_total = unit_price * item.quantity
            order.items.append(
                OrderItem(
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    seller_id=item.product.seller_id,
                    product_name=item.product.name,
                    variant_name=item.variant.name if item.variant else None,
                    sku=item.variant.sku if item.variant else None,
                    unit_price=unit_price,
                    quantity=item.quantity,
                    line_total=line_total,
                ),
            )
            self.inventory.decrement_stock(
                product_id=item.product_id,
                variant_id=item.variant_id,
                quantity=item.quantity,
            )

        self.orders.create_order(order)
        self.shopping.clear_cart(user_id)
        self.db.commit()
        self.db.refresh(order)
        stored_order = self.orders.get_order(user_id=user_id, order_id=order.id)
        if stored_order is None:
            raise not_found("Order was not found")
        return OrderResponse.model_validate(stored_order)

    def list_orders(self, user_id: str) -> list[Order]:
        return self.orders.list_orders(user_id)

    def get_order(self, *, user_id: str, order_id: str) -> Order:
        order = self.orders.get_order(user_id=user_id, order_id=order_id)
        if order is None:
            raise not_found("Order was not found")
        return order

    def cancel_order(self, *, user_id: str, order_id: str) -> Order:
        order = self.get_order(user_id=user_id, order_id=order_id)
        if order.status not in {OrderStatus.PENDING, OrderStatus.CONFIRMED}:
            raise bad_request("Only pending or confirmed orders can be cancelled")
        order.status = OrderStatus.CANCELLED
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_status(self, *, user_id: str, order_id: str, payload: OrderStatusUpdate) -> Order:
        seller = SellerService(self.db).require_seller(user_id)
        order = self.orders.get_order_by_id(order_id)
        if order is None:
            raise not_found("Order was not found")
        if not any(item.seller_id == seller.id for item in order.items):
            raise forbidden("Only the seller assigned to this order can update fulfillment status")
        if order.status == OrderStatus.CANCELLED:
            raise bad_request("Cancelled orders cannot move through fulfillment")
        current_index = self.STATUS_FLOW.index(order.status)
        next_index = current_index + 1
        if next_index >= len(self.STATUS_FLOW) or payload.status != self.STATUS_FLOW[next_index]:
            raise bad_request("Invalid order status transition")
        order.status = payload.status
        self.db.commit()
        self.db.refresh(order)
        return order

    def _shipping_address(self, user_id: str, address_id: str) -> Address:
        address = self.db.get(Address, address_id)
        if address is None or address.user_id != user_id:
            raise bad_request("A valid shipping address is required")
        return address

    def _coupon(self, coupon_code: str | None) -> Coupon | None:
        if not coupon_code:
            return None
        coupon = self.orders.get_coupon(coupon_code)
        if coupon is None:
            raise bad_request("Coupon is invalid or inactive")
        return coupon

    @staticmethod
    def _discount_amount(coupon: Coupon | None, subtotal: Money) -> Money:
        if coupon is None:
            return Decimal("0.00")
        if coupon.discount_type == DiscountType.PERCENT:
            return (subtotal * (to_money(coupon.discount_value) / Decimal("100"))).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        return min(to_money(coupon.discount_value), subtotal)
