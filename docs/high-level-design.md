# High Level Design

## Architecture Overview

Atlas Commerce Platform follows a layered enterprise architecture:

```text
React TypeScript UI
  |
Axios API client + React Query
  |
FastAPI routers
  |
Services
  |
Repositories
  |
SQLAlchemy ORM
  |
PostgreSQL
```

The frontend owns presentation, routing, form handling, and browser interactions. The backend owns authentication, authorization, validation, business rules, persistence, and API responses. PostgreSQL is the source of truth. Docker Compose orchestrates local runtime. GitHub Actions validates backend and frontend quality gates.

## Frontend

- Framework: React with TypeScript.
- Routing: React Router.
- Data fetching: Axios client wrapped by service modules and React Query.
- Styling: Tailwind CSS.
- Protected routes: authenticated pages are wrapped in a protected route component.
- Primary pages:
  - `/` landing page.
  - `/categories`, `/products`, `/products/:productId`, `/stores/:sellerId`.
  - `/login`, `/register`.
  - `/dashboard`, `/profile`, `/wishlist`, `/cart`, `/checkout`, `/orders`.
  - `/seller`, `/admin`.

## Backend

- Framework: FastAPI.
- Language: Python 3.12.
- API structure: route modules by domain.
- Business structure: Router -> Service -> Repository -> Database.
- Validation: Pydantic v2 schemas and custom validation utilities.
- Persistence: SQLAlchemy 2 ORM with PostgreSQL.
- Migration: Alembic.
- Security: JWT access tokens, persisted refresh token hashes, Passlib password hashing, RBAC dependencies.

## Database

- PostgreSQL stores all persistent application state.
- SQLAlchemy models define domain tables and relationships.
- Alembic migrations maintain schema evolution.
- UUID-style string primary keys are used across tables.
- Foreign keys enforce ownership and lifecycle relationships.
- Unique constraints enforce data integrity for users, slugs, SKUs, cart/wishlist uniqueness, warehouse codes, coupons, and payment references.

## Authentication

Authentication uses access tokens and refresh tokens:

1. User registers or logs in.
2. Backend validates credentials.
3. Backend issues a short-lived JWT access token.
4. Backend stores a hashed refresh token.
5. Client sends bearer access token on protected API calls.
6. Refresh endpoint rotates refresh tokens.
7. Logout revokes refresh token.

## Authorization

- `customer` and `admin` are persisted roles.
- Admin endpoints require `admin` role through `require_roles(UserRole.ADMIN)`.
- Customer endpoints permit customer/admin where implemented.
- Seller capability is derived from a seller profile owned by the authenticated user.
- Resource ownership is enforced in services for profile, address, cart, wishlist, seller product, inventory, and order operations.

## Docker

Docker Compose provides:

- `db`: PostgreSQL 16 Alpine with health check and persistent volume.
- `backend`: FastAPI app on host port `8001`.
- `frontend`: Nginx-served React build on host port `3000`.

The backend waits for database health before startup.

## CI/CD

GitHub Actions are split by concern:

- Backend CI:
  - Python 3.12 setup.
  - Dependency install.
  - Compile backend.
  - Ruff lint.
  - Alembic migration validation.
  - Pytest.
- Frontend CI:
  - Node 20 setup.
  - Python setup for Playwright backend.
  - Dependency install.
  - TypeScript lint/typecheck.
  - Vite production build.
  - Playwright Chromium tests.

## Testing

- Pytest validates backend APIs and service behavior through FastAPI test client.
- Playwright validates browser journeys:
  - landing -> register -> login -> profile update -> logout.
  - login -> browse -> wishlist -> cart -> checkout -> order history -> logout.
- Frontend `npm run lint` performs TypeScript no-emit checking.
- Frontend `npm run build` validates production build.

## Deployment

The local deployment path is Docker Compose:

```text
docker compose up --build -d
```

Production deployment should externalize secrets, set a production-grade `JWT_SECRET_KEY`, configure managed PostgreSQL, restrict CORS origins, enable HTTPS at the edge, and run migrations as part of release orchestration.
