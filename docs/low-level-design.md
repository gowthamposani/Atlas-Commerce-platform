# Low Level Design

## Folder Structure

```text
backend/
  alembic/                  Database migrations
  app/
    api/                    FastAPI routers
    core/                   config, dependencies, exceptions, security
    database/               session, base, migration helper, demo seed
    models/                 SQLAlchemy models
    repositories/           database access classes
    schemas/                Pydantic request/response schemas
    services/               business logic
    utils/                  shared utility helpers
  tests/                    Pytest API and integration tests

frontend/
  src/
    components/             reusable UI components
    context/                auth context
    layouts/                app layout
    pages/                  route-level pages
    routes/                 protected route wrapper
    services/               Axios API service modules
    types/                  API TypeScript types
    utils/                  display helpers
  tests/                    Playwright tests

docker/                     backend and frontend Dockerfiles, nginx config
.github/workflows/          backend and frontend CI
docs/                       enterprise documentation
```

## API Layer

API files define HTTP routes, dependency injection, response models, and status codes.

- `auth.py`: registration, login, refresh, logout, current user.
- `customer.py`: profile, dashboard, addresses.
- `catalog.py`: categories, product search, product detail.
- `seller.py`: seller profile, dashboard, seller products, public store.
- `inventory.py`: warehouses, stock, validation.
- `shopping.py`: wishlist and cart.
- `orders.py`: checkout/order creation, history, details, cancel, status.
- `admin.py`: admin dashboard, moderation, reports, notifications, payments, AI, reviews.

Routers delegate business behavior to services and avoid embedding database logic directly.

## Service Layer

Services enforce business rules and coordinate repository/model operations.

- `AuthService`: account creation, password verification, token issuance, refresh rotation, logout.
- `CustomerService`: profile lookup/update, addresses, default shipping, customer dashboard metrics.
- `CatalogService`: category management, product search, product detail, available quantity.
- `SellerService`: seller profile lifecycle, seller dashboard, product CRUD.
- `InventoryService`: warehouses, stock upsert, stock validation.
- `ShoppingService`: wishlist, cart, cart totals, inventory validation.
- `OrderService`: checkout, tax/shipping/discount calculations, order creation and status changes.
- `AdminService`: dashboards, users, moderation, reports, notifications, payments, shipments, AI helpers, audit logs.

## Repository Layer

Repository classes encapsulate repeated persistence access:

- `UserRepository`: user lookup and creation.
- `RefreshTokenRepository`: refresh token hash persistence, lookup, revocation.
- `CustomerRepository`: profile and address access.
- `MarketplaceRepository`: shared marketplace data access.

Services also use direct SQLAlchemy statements where aggregate or domain-specific queries are clearer.

## Models

SQLAlchemy models define table structure, relationships, and constraints.

- Identity: `User`, `RefreshToken`.
- Customer: `CustomerProfile`, `Address`.
- Marketplace: `Category`, `SellerProfile`, `Product`, `ProductImage`, `ProductVariant`.
- Inventory: `Warehouse`, `InventoryItem`.
- Shopping: `WishlistItem`, `CartItem`.
- Orders: `Order`, `OrderItem`.
- Engagement and operations: `ProductReview`, `Notification`, `PaymentTransaction`, `Shipment`, `AuditLog`, `Coupon`.

## Schemas

Pydantic schemas define request and response contracts.

- `auth.py`: auth payloads and token/current-user responses.
- `customer.py`: profile, address, customer dashboard.
- `marketplace.py`: category, seller, product, image, variant, inventory, wishlist, cart, checkout, order, seller dashboard.
- `admin.py`: admin dashboard, moderation, coupons, reviews, reports, notifications, payments, shipments, AI responses.
- `validation.py`: reusable validation helpers.

## Utilities

- `app.utils.slug.slugify`: converts names to stable URL-friendly slugs.
- `app.core.security`: password hashing, JWT encode/decode, refresh token hashing, UTC timestamps.
- `app.core.exceptions`: standardized FastAPI HTTP exceptions.
- `app.core.config`: environment-backed settings.

## Validation

Validation occurs at multiple layers:

- Frontend forms perform immediate user feedback.
- Pydantic schemas enforce API request validity.
- SQLAlchemy constraints enforce database integrity.
- Services enforce ownership, inventory, order, moderation, and status rules.

Important validation examples:

- Names: required, trimmed, reasonable length, no numeric characters where person names are expected.
- Phone: optional leading `+`, digits only, configurable 10-15 digit default.
- Password: minimum length plus uppercase, lowercase, number, and special character.
- Price: positive decimal-compatible numbers.
- Quantity: positive for cart/checkout requests and non-negative for stock.
- Discount: percent discount must be between 0 and 100.
- SKU/code: normalized allowed characters.
- Postal code: country-aware validation helper.
- Search: trimmed; empty search treated as no filter.

## JWT Flow

```text
Register/Login
  -> validate payload
  -> verify credentials or create user
  -> create access JWT with type=access and sub=user_id
  -> create refresh token value
  -> persist refresh token hash
  -> return tokens and user

Protected request
  -> HTTP Bearer token
  -> decode JWT
  -> require type=access
  -> load active user
  -> inject user into route

Refresh
  -> hash incoming refresh token
  -> find active persisted token
  -> revoke old token
  -> issue new access and refresh token

Logout
  -> hash incoming refresh token
  -> revoke persisted token
```

## RBAC

- `get_current_user` authenticates bearer tokens and rejects inactive users.
- `require_roles(...)` wraps route dependencies for role-gated APIs.
- Admin APIs require `UserRole.ADMIN`.
- Customer profile APIs allow customer/admin.
- Seller APIs require authentication and seller-profile ownership in services.
- Resource ownership checks prevent cross-user access to addresses, carts, wishlists, orders, products, and inventory.

## Database Flow

```text
HTTP request
  -> FastAPI route
  -> Pydantic validation
  -> get_db dependency opens SQLAlchemy session
  -> service executes business logic
  -> repository/model queries PostgreSQL
  -> service commits or rolls back through request lifecycle
  -> Pydantic response model serializes output
```

## Error Handling

- Invalid payloads return FastAPI/Pydantic `422`.
- Authentication failures return unauthorized errors.
- RBAC failures return forbidden errors.
- Missing resources return not found errors.
- Business rule violations return bad request errors.

## Frontend Data Flow

```text
Page/component
  -> service function
  -> Axios client
  -> FastAPI endpoint
  -> React Query cache invalidation
  -> refreshed UI state
```

The auth context stores current session information and adds protected-route behavior.
