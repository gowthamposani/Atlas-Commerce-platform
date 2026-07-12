# System Architecture

## Component Summary

Atlas Commerce Platform is composed of:

- React: browser application and route-level user interface.
- FastAPI: REST API and business process entry point.
- PostgreSQL: transactional system of record.
- SQLAlchemy: ORM mapping and query layer.
- Alembic: schema migration engine.
- Docker: repeatable local runtime and image builds.
- GitHub Actions: automated CI quality gates.
- Playwright: browser-level end-to-end testing.
- Pytest: backend API and integration testing.

## Communication Model

```text
Browser
  |
  | HTTP requests through Axios
  v
FastAPI app on /api
  |
  | SQLAlchemy sessions
  v
PostgreSQL

GitHub Actions
  |-- backend compile/lint/test/migration validation
  |-- frontend typecheck/build/playwright

Docker Compose
  |-- db: postgres
  |-- backend: uvicorn/FastAPI
  |-- frontend: nginx static React app
```

## React

React owns the interactive experience. Pages are organized by domain: authentication, customer, seller, shared marketplace, and admin. React Router maps browser paths to pages. React Query manages API request state, cache invalidation, loading states, and mutation refreshes. Axios centralizes HTTP communication with the backend API base URL.

## FastAPI

FastAPI exposes REST endpoints under `/api`. Routers group endpoints by domain and use dependency injection for database sessions and authenticated users. Response models are declared with Pydantic schemas, producing OpenAPI documentation at `/docs`.

## PostgreSQL

PostgreSQL stores users, profiles, addresses, refresh tokens, seller profiles, categories, products, inventory, wishlists, carts, orders, reviews, notifications, payments, shipments, audit logs, and coupons.

## SQLAlchemy

SQLAlchemy 2 maps Python classes to database tables. Services use sessions to query, create, update, and delete entities. Relationships support eager loading for product, order, and dashboard responses.

## Alembic

Alembic tracks schema migrations. Backend CI validates migrations by upgrading a CI database to the latest revision. The backend Docker startup runs application migration logic before serving traffic.

## Docker

Docker Compose starts three services:

- `db`: PostgreSQL with health check.
- `backend`: FastAPI app exposed on host port `8001`.
- `frontend`: Nginx static server exposed on host port `3000`.

Dockerfiles are stored under `docker/` and use Python 3.12 slim and Node 20 Alpine/Nginx images.

## GitHub Actions

Two workflows validate release readiness:

- Backend CI: compile, Ruff, Alembic upgrade, Pytest.
- Frontend CI: npm install, lint/typecheck, build, Playwright.

Both workflows run on pushes and pull requests to `main` and `develop`.

## Playwright

Playwright validates high-value browser journeys using a real browser. The current tests cover authentication/profile and marketplace checkout/order flows.

## Pytest

Pytest validates backend APIs through FastAPI test client and test database configuration. Current tests cover auth/customer validation, marketplace shopping, and admin enterprise operations.

## Security Architecture

- Passwords are hashed with Passlib.
- Access tokens are signed JWTs.
- Refresh tokens are stored as hashes and rotated.
- Protected APIs require bearer authentication.
- Admin APIs require admin RBAC.
- CORS is configured from environment.
- Security headers are applied by backend middleware.

## Data Integrity Architecture

- Pydantic validates request payloads.
- Services validate business rules and ownership.
- SQLAlchemy relationships and database constraints enforce referential integrity.
- Unique constraints prevent duplicate emails, slugs, SKUs, cart rows, wishlist rows, warehouse codes, coupons, and payment references.

## Operational Architecture

Local operation:

1. Docker Compose starts PostgreSQL.
2. Backend waits for database health.
3. Backend migrates/starts FastAPI.
4. Frontend serves built React assets through Nginx.
5. Browser connects to frontend and calls backend APIs.

Production operation should externalize secrets, use managed database backups, enforce HTTPS, configure restricted CORS, and run migrations during deployment.
