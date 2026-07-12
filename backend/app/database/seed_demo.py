from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from uuid import UUID, uuid5

from app.core.security import hash_password, utc_now
from app.database.session import SessionLocal
from app.models.address import Address
from app.models.customer_profile import CustomerProfile
from app.models.marketplace import (
    CartItem,
    Category,
    InventoryItem,
    Notification,
    NotificationType,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductImage,
    ProductReview,
    ProductStatus,
    ReviewStatus,
    SellerModerationStatus,
    SellerProfile,
    Warehouse,
    WishlistItem,
)
from app.models.user import User, UserRole
from app.utils.slug import slugify
from sqlalchemy import func, select
from sqlalchemy.orm import Session

DEMO_NAMESPACE = UUID("2cd56926-4c74-4ff0-b68a-cd0405abf60c")
DEMO_PASSWORD = "DemoPass123!"
DEMO_EMAIL_DOMAIN = "atlasdemo.com"

FIRST_NAMES = [
    "Avery",
    "Jordan",
    "Morgan",
    "Riley",
    "Quinn",
    "Taylor",
    "Casey",
    "Parker",
    "Reese",
    "Rowan",
]
LAST_NAMES = [
    "Rivera",
    "Morgan",
    "Patel",
    "Chen",
    "Nguyen",
    "Williams",
    "Garcia",
    "Brown",
    "Wilson",
    "Johnson",
]
CITIES = [
    ("Austin", "TX", "78701"),
    ("Denver", "CO", "80202"),
    ("Seattle", "WA", "98101"),
    ("Portland", "OR", "97205"),
    ("Chicago", "IL", "60601"),
    ("Atlanta", "GA", "30303"),
    ("Boston", "MA", "02108"),
    ("Phoenix", "AZ", "85004"),
]
CATEGORIES = [
    "Outdoor Gear",
    "Running Shoes",
    "Smart Home",
    "Kitchen Essentials",
    "Travel Bags",
    "Fitness Tech",
    "Office Furniture",
    "Audio",
    "Pet Supplies",
    "Cycling",
    "Home Decor",
    "Coffee",
    "Skincare",
    "Baby Care",
    "Garden",
    "Gaming",
    "Books",
    "Tools",
    "Apparel",
    "Wellness",
]
BRANDS = [
    "Atlas",
    "Northline",
    "SummitWorks",
    "UrbanPeak",
    "TerraCraft",
    "NovaNest",
    "BlueTrail",
    "HarborCo",
    "Cedar & Stone",
    "PulseLab",
]
PRODUCT_NOUNS = [
    "Backpack",
    "Jacket",
    "Speaker",
    "Desk",
    "Bottle",
    "Lamp",
    "Mat",
    "Organizer",
    "Headphones",
    "Cookware Set",
]
PRODUCT_ADJECTIVES = [
    "Trail",
    "Everyday",
    "Compact",
    "Premium",
    "Pro",
    "Lightweight",
    "Urban",
    "Classic",
    "Performance",
    "Eco",
]
IMAGE_URLS = [
    "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1540574163026-643ea20ade25?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1517705008128-361805f42e86?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
]
REVIEW_TITLES = [
    "Excellent quality",
    "Reliable daily choice",
    "Fast delivery",
    "Exactly as described",
    "Strong value",
]


def demo_id(key: str) -> str:
    return str(uuid5(DEMO_NAMESPACE, key))


def index_from_key(key: str) -> int:
    return sum((position + 1) * ord(character) for position, character in enumerate(key))


def money(value: Decimal | float | int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def ensure_user(
    db: Session,
    *,
    key: str,
    email: str,
    first_name: str,
    last_name: str,
    password_hash: str,
    role: UserRole = UserRole.CUSTOMER,
) -> User:
    user = db.get(User, demo_id(f"user:{key}"))
    if user is None:
        user = User(
            id=demo_id(f"user:{key}"),
            email=email,
            hashed_password=password_hash,
            role=role,
            is_active=True,
        )
        db.add(user)
    else:
        user.email = email
        user.role = role
        user.is_active = True

    profile = db.get(CustomerProfile, demo_id(f"profile:{key}"))
    if profile is None:
        db.add(
            CustomerProfile(
                id=demo_id(f"profile:{key}"),
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                phone=f"555{1000000 + (index_from_key(key) % 9000000)}",
            ),
        )
    else:
        profile.first_name = first_name
        profile.last_name = last_name
        profile.phone = f"555{1000000 + (index_from_key(key) % 9000000)}"
    return user


def ensure_address(db: Session, *, key: str, user: User, name: str, index: int) -> Address:
    city, state, postal_code = CITIES[index % len(CITIES)]
    address = db.get(Address, demo_id(f"address:{key}"))
    if address is None:
        address = Address(
            id=demo_id(f"address:{key}"),
            user_id=user.id,
            label="Home",
            recipient_name=name,
            line1=f"{100 + index} Commerce Street",
            city=city,
            state=state,
            postal_code=postal_code,
            country="US",
            phone="5550100100",
            is_default_shipping=True,
        )
        db.add(address)
    else:
        address.recipient_name = name
        address.city = city
        address.state = state
        address.postal_code = postal_code
        address.phone = "5550100100"
        address.is_default_shipping = True
    return address


def seed_customers(db: Session, password_hash: str) -> list[User]:
    customers: list[User] = []
    for index in range(1, 101):
        key = f"customer-{index:03d}"
        first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
        last_name = LAST_NAMES[index % len(LAST_NAMES)]
        user = ensure_user(
            db,
            key=key,
            email=f"demo.customer{index:03d}@{DEMO_EMAIL_DOMAIN}",
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
        )
        ensure_address(db, key=key, user=user, name=f"{first_name} {last_name}", index=index)
        customers.append(user)
    return customers


def seed_admin(db: Session, password_hash: str) -> User:
    return ensure_user(
        db,
        key="admin",
        email=f"demo.admin@{DEMO_EMAIL_DOMAIN}",
        first_name="Demo",
        last_name="Admin",
        password_hash=password_hash,
        role=UserRole.ADMIN,
    )


def seed_categories(db: Session) -> list[Category]:
    categories: list[Category] = []
    for index, name in enumerate(CATEGORIES, start=1):
        category = db.get(Category, demo_id(f"category:{index:02d}"))
        slug = f"demo-{slugify(name)}"
        if category is None:
            category = Category(
                id=demo_id(f"category:{index:02d}"),
                name=name,
                slug=slug,
                description=f"Curated {name.lower()} for Atlas Commerce demo shoppers.",
                is_active=True,
            )
            db.add(category)
        else:
            category.name = name
            category.slug = slug
            category.description = f"Curated {name.lower()} for Atlas Commerce demo shoppers."
            category.is_active = True
        categories.append(category)
    return categories


def seed_sellers(
    db: Session,
    password_hash: str,
) -> tuple[list[User], list[SellerProfile], list[Warehouse]]:
    seller_users: list[User] = []
    sellers: list[SellerProfile] = []
    warehouses: list[Warehouse] = []
    for index in range(1, 21):
        key = f"seller-{index:03d}"
        user = ensure_user(
            db,
            key=key,
            email=f"demo.seller{index:03d}@{DEMO_EMAIL_DOMAIN}",
            first_name="Seller",
            last_name=f"{index:02d}",
            password_hash=password_hash,
        )
        seller_users.append(user)
        store_name = f"{BRANDS[(index - 1) % len(BRANDS)]} Marketplace Co. {index:02d}"
        seller = db.get(SellerProfile, demo_id(f"seller-profile:{index:03d}"))
        if seller is None:
            seller = SellerProfile(
                id=demo_id(f"seller-profile:{index:03d}"),
                user_id=user.id,
                store_name=store_name,
                slug=f"demo-{slugify(store_name)}",
                description=f"{store_name} supplies verified demo catalog products.",
                moderation_status=SellerModerationStatus.APPROVED,
                is_active=True,
            )
            db.add(seller)
        else:
            seller.store_name = store_name
            seller.description = f"{store_name} supplies verified demo catalog products."
            seller.moderation_status = SellerModerationStatus.APPROVED
            seller.is_active = True
        sellers.append(seller)

        warehouse = db.get(Warehouse, demo_id(f"warehouse:{index:03d}"))
        if warehouse is None:
            warehouse = Warehouse(
                id=demo_id(f"warehouse:{index:03d}"),
                seller_id=seller.id,
                name=f"{store_name} Fulfillment",
                code=f"DEMO-WH-{index:03d}",
                city=CITIES[index % len(CITIES)][0],
                state=CITIES[index % len(CITIES)][1],
                country="US",
                is_active=True,
            )
            db.add(warehouse)
        else:
            warehouse.seller_id = seller.id
            warehouse.name = f"{store_name} Fulfillment"
            warehouse.is_active = True
        warehouses.append(warehouse)
    return seller_users, sellers, warehouses


def seed_products(
    db: Session,
    *,
    categories: list[Category],
    sellers: list[SellerProfile],
    warehouses: list[Warehouse],
) -> list[Product]:
    products: list[Product] = []
    for index in range(1, 201):
        seller = sellers[(index - 1) % len(sellers)]
        category = categories[(index - 1) % len(categories)]
        brand = BRANDS[(index - 1) % len(BRANDS)]
        name = (
            f"{brand} {PRODUCT_ADJECTIVES[index % len(PRODUCT_ADJECTIVES)]} "
            f"{PRODUCT_NOUNS[index % len(PRODUCT_NOUNS)]} {index:03d}"
        )
        base_price = money(18 + ((index * 7) % 220) + Decimal(f"0.{index % 99:02d}"))
        product = db.get(Product, demo_id(f"product:{index:03d}"))
        if product is None:
            product = Product(
                id=demo_id(f"product:{index:03d}"),
                seller_id=seller.id,
                category_id=category.id,
                name=name,
                slug=f"demo-{slugify(name)}",
                description=(
                    f"{name} combines practical design, dependable materials, "
                    "and marketplace-ready fulfillment for demo shoppers."
                ),
                brand=brand,
                status=ProductStatus.ACTIVE if index % 17 else ProductStatus.DRAFT,
                is_visible=index % 19 != 0,
                is_featured=index % 11 == 0,
                base_price=base_price,
            )
            db.add(product)
        else:
            product.seller_id = seller.id
            product.category_id = category.id
            product.name = name
            product.slug = f"demo-{slugify(name)}"
            product.description = (
                f"{name} combines practical design, dependable materials, "
                "and marketplace-ready fulfillment for demo shoppers."
            )
            product.brand = brand
            product.status = ProductStatus.ACTIVE if index % 17 else ProductStatus.DRAFT
            product.is_visible = index % 19 != 0
            product.is_featured = index % 11 == 0
            product.base_price = base_price
        products.append(product)

        image = db.get(ProductImage, demo_id(f"product-image:{index:03d}"))
        if image is None:
            db.add(
                ProductImage(
                    id=demo_id(f"product-image:{index:03d}"),
                    product_id=product.id,
                    url=IMAGE_URLS[index % len(IMAGE_URLS)],
                    alt_text=name,
                    sort_order=0,
                    is_primary=True,
                ),
            )
        else:
            image.product_id = product.id
            image.url = IMAGE_URLS[index % len(IMAGE_URLS)]
            image.alt_text = name
            image.is_primary = True

        warehouse = warehouses[(index - 1) % len(warehouses)]
        inventory = db.get(InventoryItem, demo_id(f"inventory:{index:03d}"))
        if inventory is None:
            inventory = InventoryItem(
                id=demo_id(f"inventory:{index:03d}"),
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity=8 + ((index * 13) % 90),
                reserved_quantity=index % 4,
                reorder_level=10 if index % 9 == 0 else 4,
            )
            db.add(inventory)
        else:
            inventory.product_id = product.id
            inventory.warehouse_id = warehouse.id
            inventory.quantity = 8 + ((index * 13) % 90)
            inventory.reserved_quantity = index % 4
            inventory.reorder_level = 10 if index % 9 == 0 else 4
    return products


def default_address(db: Session, user: User) -> Address:
    address = db.scalar(
        select(Address)
        .where(Address.user_id == user.id)
        .order_by(Address.is_default_shipping.desc(), Address.created_at.desc()),
    )
    if address is None:
        raise RuntimeError(f"Demo user {user.email} does not have an address")
    return address


def seed_orders(db: Session, *, customers: list[User], products: list[Product]) -> list[Order]:
    orders: list[Order] = []
    statuses = [
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.PACKED,
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
    ]
    now = utc_now()
    for index in range(1, 201):
        user = customers[(index - 1) % len(customers)]
        address = default_address(db, user)
        order = db.get(Order, demo_id(f"order:{index:03d}"))
        item_count = 1 + (index % 3)
        chosen_products = [
            products[(index + offset * 17) % len(products)] for offset in range(item_count)
        ]
        subtotal = sum(money(product.base_price) for product in chosen_products)
        tax_amount = money(subtotal * Decimal("0.08"))
        shipping_charge = Decimal("0.00") if subtotal >= Decimal("75.00") else Decimal("8.99")
        discount_amount = Decimal("5.00") if index % 12 == 0 else Decimal("0.00")
        total_amount = money(subtotal + tax_amount + shipping_charge - discount_amount)
        created_at = now - timedelta(days=index % 90, hours=index % 12)
        if order is None:
            order = Order(
                id=demo_id(f"order:{index:03d}"),
                order_number=f"DEMO-{index:05d}",
                user_id=user.id,
                shipping_address_id=address.id,
                billing_address={
                    "recipient_name": address.recipient_name,
                    "line1": address.line1,
                    "line2": address.line2,
                    "city": address.city,
                    "state": address.state,
                    "postal_code": address.postal_code,
                    "country": address.country,
                },
                status=statuses[index % len(statuses)],
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_charge=shipping_charge,
                discount_amount=discount_amount,
                total_amount=total_amount,
                coupon_code="DEMO5" if discount_amount else None,
                payment_method="placeholder",
                payment_status="succeeded" if index % 5 else "pending",
                shipment_status="delivered" if index % 5 == 4 else "pending",
                tracking_number=f"DEMO-TRK-{index:05d}" if index % 5 == 4 else None,
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(order)
        else:
            order.user_id = user.id
            order.shipping_address_id = address.id
            order.status = statuses[index % len(statuses)]
            order.subtotal = subtotal
            order.tax_amount = tax_amount
            order.shipping_charge = shipping_charge
            order.discount_amount = discount_amount
            order.total_amount = total_amount
            order.payment_status = "succeeded" if index % 5 else "pending"
            order.updated_at = created_at
        orders.append(order)

        for item_index, product in enumerate(chosen_products, start=1):
            item = db.get(OrderItem, demo_id(f"order-item:{index:03d}:{item_index}"))
            if item is None:
                db.add(
                    OrderItem(
                        id=demo_id(f"order-item:{index:03d}:{item_index}"),
                        order_id=order.id,
                        product_id=product.id,
                        seller_id=product.seller_id,
                        product_name=product.name,
                        unit_price=money(product.base_price),
                        quantity=1,
                        line_total=money(product.base_price),
                    ),
                )
            else:
                item.order_id = order.id
                item.product_id = product.id
                item.seller_id = product.seller_id
                item.product_name = product.name
                item.unit_price = money(product.base_price)
                item.quantity = 1
                item.line_total = money(product.base_price)
    return orders


def seed_reviews(
    db: Session,
    *,
    customers: list[User],
    products: list[Product],
) -> list[ProductReview]:
    reviews: list[ProductReview] = []
    now = utc_now()
    for index in range(1, 501):
        product = products[(index - 1) % len(products)]
        user = customers[(index - 1) % len(customers)]
        status = ReviewStatus.APPROVED
        if index % 31 == 0:
            status = ReviewStatus.REPORTED
        elif index % 13 == 0:
            status = ReviewStatus.PENDING
        review = db.get(ProductReview, demo_id(f"review:{index:03d}"))
        if review is None:
            review = ProductReview(
                id=demo_id(f"review:{index:03d}"),
                product_id=product.id,
                user_id=user.id,
                rating=3 + (index % 3),
                title=REVIEW_TITLES[index % len(REVIEW_TITLES)],
                body=(
                    f"Verified purchase review for {product.name}. "
                    "The item arrived as expected and felt presentation-ready."
                ),
                status=status,
                report_reason=(
                    "Needs moderation review" if status == ReviewStatus.REPORTED else None
                ),
                created_at=now - timedelta(days=index % 120),
                updated_at=now - timedelta(days=index % 120),
            )
            db.add(review)
        else:
            review.product_id = product.id
            review.user_id = user.id
            review.status = status
            review.report_reason = (
                "Needs moderation review" if status == ReviewStatus.REPORTED else None
            )
        reviews.append(review)
    return reviews


def seed_shopping_state(db: Session, *, customers: list[User], products: list[Product]) -> None:
    for index, user in enumerate(customers[:40], start=1):
        product = products[(index * 3) % len(products)]
        wishlist = db.get(WishlistItem, demo_id(f"wishlist:{index:03d}"))
        if wishlist is None:
            db.add(
                WishlistItem(
                    id=demo_id(f"wishlist:{index:03d}"),
                    user_id=user.id,
                    product_id=product.id,
                ),
            )
        cart = db.get(CartItem, demo_id(f"cart:{index:03d}"))
        if cart is None:
            db.add(
                CartItem(
                    id=demo_id(f"cart:{index:03d}"),
                    user_id=user.id,
                    product_id=products[(index * 5) % len(products)].id,
                    quantity=1 + (index % 2),
                ),
            )
        else:
            cart.quantity = 1 + (index % 2)


def seed_notifications(
    db: Session,
    *,
    customers: list[User],
    sellers: list[User],
) -> list[Notification]:
    notifications: list[Notification] = []
    for index, user in enumerate(customers, start=1):
        notification = db.get(Notification, demo_id(f"notification:customer:{index:03d}"))
        if notification is None:
            notification = Notification(
                id=demo_id(f"notification:customer:{index:03d}"),
                user_id=user.id,
                type=NotificationType.ORDER,
                title="Order update",
                message="Your Atlas demo order is moving through fulfillment.",
                is_read=index % 4 == 0,
            )
            db.add(notification)
        notifications.append(notification)
    for index, user in enumerate(sellers, start=1):
        notification = db.get(Notification, demo_id(f"notification:seller:{index:03d}"))
        if notification is None:
            notification = Notification(
                id=demo_id(f"notification:seller:{index:03d}"),
                user_id=user.id,
                type=NotificationType.SELLER,
                title="Seller performance summary",
                message="Your demo store has fresh marketplace activity.",
                is_read=False,
            )
            db.add(notification)
        notifications.append(notification)
    for index in range(1, 11):
        notification = db.get(Notification, demo_id(f"notification:admin:{index:03d}"))
        if notification is None:
            notification = Notification(
                id=demo_id(f"notification:admin:{index:03d}"),
                user_id=None,
                type=NotificationType.ADMIN,
                title="Admin operations digest",
                message="Demo marketplace metrics are ready for review.",
                is_read=False,
            )
            db.add(notification)
        notifications.append(notification)
    return notifications


def demo_count(db: Session, model, prefix: str, field) -> int:
    return int(db.scalar(select(func.count(model.id)).where(field.like(prefix))) or 0)


def seed_demo_data() -> dict[str, int]:
    password_hash = hash_password(DEMO_PASSWORD)
    with SessionLocal() as db:
        seed_admin(db, password_hash)
        customers = seed_customers(db, password_hash)
        categories = seed_categories(db)
        seller_users, sellers, warehouses = seed_sellers(db, password_hash)
        db.flush()
        products = seed_products(db, categories=categories, sellers=sellers, warehouses=warehouses)
        db.flush()
        orders = seed_orders(db, customers=customers, products=products)
        reviews = seed_reviews(db, customers=customers, products=products)
        seed_shopping_state(db, customers=customers, products=products)
        notifications = seed_notifications(db, customers=customers, sellers=seller_users)
        db.commit()

        return {
            "customers": len(customers),
            "sellers": len(sellers),
            "categories": len(categories),
            "products": len(products),
            "orders": len(orders),
            "reviews": len(reviews),
            "notifications": len(notifications),
        }


if __name__ == "__main__":
    summary = seed_demo_data()
    for key, value in summary.items():
        print(f"{key}: {value}")
    print(f"demo_password: {DEMO_PASSWORD}")
