# Atlas Commerce Platform Architecture

This file is the concise architecture reference. Detailed design is available in:

- [High Level Design](high-level-design.md)
- [Low Level Design](low-level-design.md)
- [System Architecture](system-architecture.md)
- [Database Design](database-design.md)
- [API Documentation](api-contract.md)

## Architectural Style

Atlas Commerce Platform uses a layered full-stack architecture:

```text
Frontend Route/Page
  -> API service
  -> Axios client
  -> FastAPI router
  -> Service
  -> Repository / SQLAlchemy query
  -> PostgreSQL
```

## Backend Domains

- Authentication and RBAC.
- Customer profile and addresses.
- Catalog categories and products.
- Seller profile and seller product management.
- Inventory warehouses and stock.
- Wishlist and cart.
- Checkout and orders.
- Admin operations, reports, notifications, payments, AI helpers, and review moderation.

## Frontend Domains

- Public marketplace browsing.
- Authentication.
- Customer dashboard/profile/wishlist/cart/checkout/orders.
- Seller dashboard.
- Admin operations dashboard.

## Persistence

PostgreSQL is the source of truth. SQLAlchemy models represent domain tables. Alembic migrations evolve schema. All implemented business APIs persist through the database.

## Security

- Passlib password hashing.
- JWT access tokens.
- Persisted refresh-token hashes.
- Refresh-token rotation.
- Role-based dependencies.
- Ownership checks in service methods.

## Runtime

- Frontend: React static build served by Nginx on port `3000`.
- Backend: FastAPI served on port `8001`.
- Database: PostgreSQL inside Docker Compose.

## Quality Gates

- `python -m compileall backend/app`
- `ruff check backend/app backend/tests`
- `pytest backend/tests`
- `npm run lint`
- `npm run build`
- `npx playwright test`
- `docker compose build`
- `docker compose up`
