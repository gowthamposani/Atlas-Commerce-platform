# Business Requirements Document

## Executive Summary

Atlas Commerce Platform is an enterprise marketplace application that supports customer shopping, seller operations, and administrative governance. The platform combines a React TypeScript frontend, FastAPI backend, PostgreSQL persistence, JWT authentication, role-based access control, Docker deployment, and automated testing.

The completed product demonstrates an end-to-end commerce journey: customers register, manage profiles and addresses, browse products, maintain wishlists and carts, check out, and track orders. Sellers manage stores, products, and inventory. Administrators monitor platform health, moderate users/sellers/products/reviews, generate reports, issue notifications, manage sandbox payments, and use internal AI-style product assistance.

## Business Problem

Marketplace operators need a reliable platform that can centralize product discovery, seller catalog management, inventory tracking, order processing, and administrative control. Without an integrated system, teams face fragmented customer data, manual moderation, inconsistent inventory visibility, weak validation, and limited operational reporting.

Atlas Commerce Platform addresses these issues by providing a single persisted system of record for commerce operations and an enterprise-ready architecture suitable for phased production hardening.

## Objectives

- Provide secure authentication, refresh-token rotation, logout, and current-user discovery.
- Support customer profile and address management with default shipping addresses.
- Enable product discovery through categories, search, filters, pagination, and product detail pages.
- Enable seller registration, dashboards, product management, and inventory management.
- Support wishlist, cart, checkout, order history, order details, cancellation, and status tracking.
- Provide admin dashboards, moderation, reports, notifications, payment sandbox operations, and internal AI demo endpoints.
- Persist all business data in PostgreSQL through SQLAlchemy models and repositories/services.
- Provide automated confidence through Pytest, Playwright, frontend build/type checks, Docker, and GitHub Actions.

## Scope

In scope:

- Customer web experience.
- Seller web experience.
- Admin web experience.
- REST APIs for authentication, customer, catalog, seller, inventory, shopping, orders, reviews, admin, reports, notifications, payments, and AI demo helpers.
- PostgreSQL-backed persistence.
- Alembic migrations.
- Docker Compose local deployment.
- CI workflows for backend and frontend validation.
- Demo data generation for presentation scenarios.

Out of scope for the current release:

- Real payment gateway settlement.
- Real email/SMS/push delivery.
- External AI provider integration.
- Advanced analytics warehouse.
- Mobile native apps.
- Multi-tenant enterprise organization management.

## Stakeholders

- Business sponsor: owns marketplace launch goals and success metrics.
- Product owner: prioritizes customer, seller, and admin workflows.
- Customers: browse, purchase, review, and manage account data.
- Sellers: manage store profiles, catalog data, stock, and order visibility.
- Administrators: govern marketplace operations, moderation, reporting, notifications, and payments.
- Engineering: maintains architecture, quality gates, security, and deployment.
- QA: validates functional, API, UI, and regression flows.
- DevOps/release engineering: manages Docker, CI/CD, and environment configuration.

## User Roles

- Guest: can view landing page, categories, product listing, product details, and seller store pages.
- Customer: can manage profile/addresses, wishlist, cart, checkout, orders, reviews, and dashboard.
- Seller: an authenticated user with a seller profile; can manage seller dashboard, products, warehouses, and stock.
- Admin: can access administrative dashboards, moderation, users, sellers, products, reports, notifications, payments, and AI helper endpoints.

## Functional Scope

- Authentication: register, login, refresh token, logout, current user, password hashing, JWT access tokens.
- Customer: profile, dashboard, address CRUD, default shipping address.
- Marketplace: category listing, product search/filter/pagination, product details, seller stores.
- Seller: seller registration, seller profile, dashboard, product CRUD.
- Inventory: warehouses, stock upsert, stock listing, stock validation.
- Wishlist: add, remove, list, move item to cart.
- Cart: add, remove, update quantity, summary, inventory validation.
- Checkout/orders: shipping address selection, billing address, tax, shipping charge, coupon support, order creation, history, details, cancel, status updates.
- Admin: stats, dashboard, user status, seller moderation, product moderation, brands, catalog/coupons, orders, shipments, reviews, reports, notifications, payments, AI helpers.
- Testing: backend unit/integration tests and Playwright E2E flows.

## Non-functional Scope

- Security: JWT bearer auth, password hashing, refresh token persistence/revocation, RBAC, input validation, CORS configuration, security headers.
- Reliability: Dockerized services, database health checks, startup migrations.
- Maintainability: Router -> Service -> Repository -> Database architecture.
- Data integrity: SQLAlchemy relationships, primary keys, foreign keys, uniqueness, Pydantic validation.
- Performance baseline: pagination for product search and focused dashboard queries.
- Observability baseline: health endpoint and structured app startup.
- Portability: local Docker Compose and CI workflows.

## Assumptions

- PostgreSQL is the production persistence store.
- Docker Compose is the primary local demonstration runtime.
- Admin accounts are created/promoted operationally or through seeded demo data.
- Payment functionality is a sandbox placeholder and does not settle real funds.
- AI functionality uses deterministic internal business logic and does not call external AI providers.
- Email/notification delivery is persisted in database but not sent externally.

## Constraints

- Existing application architecture must remain unchanged.
- Existing API contracts should remain stable unless a future release explicitly versions them.
- Authentication and RBAC are role-based around `customer` and `admin`; seller capability is derived from seller profile ownership.
- Browser application consumes APIs through Axios and React Query.
- Migrations must stay compatible with SQLAlchemy model state.
- Demo data must remain clearly identifiable and idempotent.

## Risks

- Admin-only capabilities require careful credential control.
- Product/category write APIs currently require authentication and should be reviewed for stricter admin-only policy in a production authorization hardening phase.
- Sandbox payments and internal AI helpers could be misrepresented as production integrations if not clearly disclosed.
- Demo data can mask empty-state behavior if not also tested with clean databases.
- SQLite usage in tests requires continued compatibility checks against PostgreSQL behavior.
- As catalog/order volume grows, reporting queries may need indexes, caching, or asynchronous exports.

## Success Criteria

- Users can complete the customer journey from registration to order history.
- Sellers can create a store, manage products, and maintain inventory.
- Admins can view operational metrics and moderate marketplace entities.
- All frontend forms call backend APIs.
- Backend APIs persist data to PostgreSQL.
- Validation rejects malformed or unsafe input at API and UI layers.
- Pytest, frontend lint/build, Playwright, Docker Compose build/start, and CI workflows pass.
- Documentation allows a new developer, QA engineer, or presenter to understand the platform quickly.
