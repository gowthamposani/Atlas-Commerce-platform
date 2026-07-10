from collections.abc import Sequence

from app.models.marketplace import (
    CartItem,
    Category,
    Coupon,
    InventoryItem,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductStatus,
    ProductVariant,
    SellerProfile,
    Warehouse,
    WishlistItem,
)
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload


class CatalogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def slug_exists(
        self,
        model: type[Category] | type[Product] | type[SellerProfile],
        slug: str,
    ) -> bool:
        statement = select(model.id).where(model.slug == slug)
        return self.db.scalar(statement) is not None

    def list_categories(self, *, include_inactive: bool = False) -> list[Category]:
        statement = select(Category).order_by(Category.name)
        if not include_inactive:
            statement = statement.where(Category.is_active.is_(True))
        return list(self.db.scalars(statement))

    def get_category(self, category_id: str) -> Category | None:
        return self.db.get(Category, category_id)

    def create_category(self, *, slug: str, data: dict[str, object]) -> Category:
        category = Category(slug=slug, **data)
        self.db.add(category)
        return category

    def product_base_query(self):
        return select(Product).options(
            selectinload(Product.category),
            selectinload(Product.seller),
            selectinload(Product.images),
            selectinload(Product.variants),
        )

    def get_product(self, product_id: str, *, active_only: bool = True) -> Product | None:
        statement = self.product_base_query().where(Product.id == product_id)
        if active_only:
            statement = statement.where(Product.status == ProductStatus.ACTIVE)
        return self.db.scalar(statement)

    def list_products(
        self,
        *,
        search: str | None = None,
        category_id: str | None = None,
        seller_id: str | None = None,
        status: ProductStatus | None = ProductStatus.ACTIVE,
        min_price: float | None = None,
        max_price: float | None = None,
        page: int = 1,
        page_size: int = 12,
    ) -> tuple[list[Product], int]:
        filters = []
        if status is not None:
            filters.append(Product.status == status)
        if search:
            pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(Product.name).like(pattern),
                    func.lower(Product.description).like(pattern),
                ),
            )
        if category_id:
            filters.append(Product.category_id == category_id)
        if seller_id:
            filters.append(Product.seller_id == seller_id)
        if min_price is not None:
            filters.append(Product.base_price >= min_price)
        if max_price is not None:
            filters.append(Product.base_price <= max_price)

        count_statement = select(func.count(Product.id))
        statement = self.product_base_query().order_by(Product.created_at.desc())
        if filters:
            count_statement = count_statement.where(*filters)
            statement = statement.where(*filters)

        total = int(self.db.scalar(count_statement) or 0)
        items = list(
            self.db.scalars(
                statement.offset((page - 1) * page_size).limit(page_size),
            ),
        )
        return items, total


class SellerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: str) -> SellerProfile | None:
        statement = select(SellerProfile).where(SellerProfile.user_id == user_id)
        return self.db.scalar(statement)

    def get_by_id(self, seller_id: str) -> SellerProfile | None:
        return self.db.get(SellerProfile, seller_id)

    def create(self, *, user_id: str, slug: str, data: dict[str, object]) -> SellerProfile:
        seller = SellerProfile(user_id=user_id, slug=slug, **data)
        self.db.add(seller)
        return seller

    def list_products(self, seller_id: str) -> list[Product]:
        statement = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.seller),
                selectinload(Product.images),
                selectinload(Product.variants),
            )
            .where(Product.seller_id == seller_id)
            .order_by(Product.created_at.desc())
        )
        return list(self.db.scalars(statement))

    def get_product(self, *, seller_id: str, product_id: str) -> Product | None:
        statement = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.seller),
                selectinload(Product.images),
                selectinload(Product.variants),
            )
            .where(Product.seller_id == seller_id, Product.id == product_id)
        )
        return self.db.scalar(statement)

    def create_product(
        self,
        *,
        seller_id: str,
        slug: str,
        data: dict[str, object],
        images: Sequence[dict[str, object]],
        variants: Sequence[dict[str, object]],
    ) -> Product:
        product = Product(seller_id=seller_id, slug=slug, **data)
        product.images = [ProductImage(**image) for image in images]
        product.variants = [ProductVariant(**variant) for variant in variants]
        self.db.add(product)
        return product

    def replace_product_media(
        self,
        product: Product,
        *,
        images: Sequence[dict[str, object]] | None,
        variants: Sequence[dict[str, object]] | None,
    ) -> None:
        if images is not None:
            product.images = [ProductImage(**image) for image in images]
        if variants is not None:
            product.variants = [ProductVariant(**variant) for variant in variants]

    def dashboard_counts(self, seller_id: str) -> tuple[int, int, int, int]:
        product_count = int(
            self.db.scalar(
                select(func.count(Product.id)).where(Product.seller_id == seller_id),
            )
            or 0,
        )
        active_product_count = int(
            self.db.scalar(
                select(func.count(Product.id)).where(
                    Product.seller_id == seller_id,
                    Product.status == ProductStatus.ACTIVE,
                ),
            )
            or 0,
        )
        total_stock = int(
            self.db.scalar(
                select(func.coalesce(func.sum(InventoryItem.quantity), 0))
                .join(Product, Product.id == InventoryItem.product_id)
                .where(Product.seller_id == seller_id),
            )
            or 0,
        )
        order_count = int(
            self.db.scalar(
                select(func.count(func.distinct(OrderItem.order_id))).where(
                    OrderItem.seller_id == seller_id,
                ),
            )
            or 0,
        )
        return product_count, active_product_count, total_stock, order_count


class InventoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_warehouses(self, seller_id: str) -> list[Warehouse]:
        statement = (
            select(Warehouse)
            .where(Warehouse.seller_id == seller_id)
            .order_by(Warehouse.name)
        )
        return list(self.db.scalars(statement))

    def get_warehouse(self, *, seller_id: str, warehouse_id: str) -> Warehouse | None:
        statement = select(Warehouse).where(
            Warehouse.id == warehouse_id,
            Warehouse.seller_id == seller_id,
        )
        return self.db.scalar(statement)

    def create_warehouse(self, *, seller_id: str, data: dict[str, object]) -> Warehouse:
        warehouse = Warehouse(seller_id=seller_id, **data)
        self.db.add(warehouse)
        return warehouse

    def get_inventory_item(
        self,
        *,
        product_id: str,
        variant_id: str | None,
        warehouse_id: str,
    ) -> InventoryItem | None:
        statement = select(InventoryItem).where(
            InventoryItem.product_id == product_id,
            InventoryItem.warehouse_id == warehouse_id,
        )
        if variant_id is None:
            statement = statement.where(InventoryItem.variant_id.is_(None))
        else:
            statement = statement.where(InventoryItem.variant_id == variant_id)
        return self.db.scalar(statement)

    def list_inventory(self, seller_id: str) -> list[InventoryItem]:
        statement = (
            select(InventoryItem)
            .join(Product, Product.id == InventoryItem.product_id)
            .where(Product.seller_id == seller_id)
            .order_by(InventoryItem.updated_at.desc())
        )
        return list(self.db.scalars(statement))

    def available_quantity(self, *, product_id: str, variant_id: str | None = None) -> int:
        statement = select(
            func.coalesce(func.sum(InventoryItem.quantity - InventoryItem.reserved_quantity), 0),
        ).where(InventoryItem.product_id == product_id)
        if variant_id is None:
            statement = statement.where(InventoryItem.variant_id.is_(None))
        else:
            statement = statement.where(InventoryItem.variant_id == variant_id)
        return int(self.db.scalar(statement) or 0)

    def total_available_quantity(self, product_id: str) -> int:
        statement = select(
            func.coalesce(func.sum(InventoryItem.quantity - InventoryItem.reserved_quantity), 0),
        ).where(InventoryItem.product_id == product_id)
        return int(self.db.scalar(statement) or 0)

    def decrement_stock(self, *, product_id: str, variant_id: str | None, quantity: int) -> None:
        remaining = quantity
        statement = (
            select(InventoryItem)
            .where(InventoryItem.product_id == product_id)
            .order_by(InventoryItem.quantity.desc())
        )
        if variant_id is None:
            statement = statement.where(InventoryItem.variant_id.is_(None))
        else:
            statement = statement.where(InventoryItem.variant_id == variant_id)

        for item in self.db.scalars(statement):
            available = max(item.quantity - item.reserved_quantity, 0)
            if available <= 0:
                continue
            consumed = min(available, remaining)
            item.quantity -= consumed
            remaining -= consumed
            if remaining == 0:
                break


class ShoppingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_wishlist_item(
        self,
        *,
        user_id: str,
        product_id: str,
        variant_id: str | None,
    ) -> WishlistItem | None:
        statement = select(WishlistItem).where(
            WishlistItem.user_id == user_id,
            WishlistItem.product_id == product_id,
        )
        if variant_id is None:
            statement = statement.where(WishlistItem.variant_id.is_(None))
        else:
            statement = statement.where(WishlistItem.variant_id == variant_id)
        return self.db.scalar(statement)

    def get_wishlist_by_id(self, *, user_id: str, item_id: str) -> WishlistItem | None:
        statement = select(WishlistItem).where(
            WishlistItem.user_id == user_id,
            WishlistItem.id == item_id,
        )
        return self.db.scalar(statement)

    def list_wishlist(self, user_id: str) -> list[WishlistItem]:
        statement = (
            select(WishlistItem)
            .options(
                selectinload(WishlistItem.product).selectinload(Product.category),
                selectinload(WishlistItem.product).selectinload(Product.seller),
                selectinload(WishlistItem.product).selectinload(Product.images),
                selectinload(WishlistItem.variant),
            )
            .where(WishlistItem.user_id == user_id)
            .order_by(WishlistItem.created_at.desc())
        )
        return list(self.db.scalars(statement))

    def get_cart_item(
        self,
        *,
        user_id: str,
        product_id: str,
        variant_id: str | None,
    ) -> CartItem | None:
        statement = select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )
        if variant_id is None:
            statement = statement.where(CartItem.variant_id.is_(None))
        else:
            statement = statement.where(CartItem.variant_id == variant_id)
        return self.db.scalar(statement)

    def get_cart_by_id(self, *, user_id: str, item_id: str) -> CartItem | None:
        statement = select(CartItem).where(CartItem.user_id == user_id, CartItem.id == item_id)
        return self.db.scalar(statement)

    def list_cart(self, user_id: str) -> list[CartItem]:
        statement = (
            select(CartItem)
            .options(
                selectinload(CartItem.product).selectinload(Product.category),
                selectinload(CartItem.product).selectinload(Product.seller),
                selectinload(CartItem.product).selectinload(Product.images),
                selectinload(CartItem.variant),
            )
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.created_at)
        )
        return list(self.db.scalars(statement))

    def clear_cart(self, user_id: str) -> None:
        for item in self.list_cart(user_id):
            self.db.delete(item)


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_coupon(self, code: str) -> Coupon | None:
        statement = select(Coupon).where(Coupon.code == code.upper(), Coupon.is_active.is_(True))
        return self.db.scalar(statement)

    def create_order(self, order: Order) -> Order:
        self.db.add(order)
        return order

    def list_orders(self, user_id: str) -> list[Order]:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return list(self.db.scalars(statement))

    def get_order(self, *, user_id: str, order_id: str) -> Order | None:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id, Order.id == order_id)
        )
        return self.db.scalar(statement)

    def get_order_by_id(self, order_id: str) -> Order | None:
        statement = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        return self.db.scalar(statement)
