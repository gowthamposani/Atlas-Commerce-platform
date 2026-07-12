# Presentation Guide

## Goal

This guide supports a 10-15 minute product demonstration of Atlas Commerce Platform. It is written for a technical/business audience and highlights architecture, customer flow, seller flow, admin flow, AI demo helpers, testing, CI/CD, and future scope.

## 10-15 Minute Script

### 1. Introduction - 1 minute

"Atlas Commerce Platform is an enterprise marketplace application built with React, TypeScript, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Docker, Pytest, and Playwright. It supports three primary audiences: customers, sellers, and administrators. The goal is to demonstrate a full commerce lifecycle from account creation and product discovery to checkout, seller operations, and admin governance."

Key points:

- Full-stack marketplace.
- PostgreSQL-backed persistence.
- Real API calls from every frontend workflow.
- Automated tests and Dockerized runtime.

### 2. Architecture - 2 minutes

"The system follows a layered architecture: React pages call Axios services, services call FastAPI routers, routers delegate to service classes, services use repositories or SQLAlchemy queries, and all business data is persisted in PostgreSQL."

Show:

- `docs/high-level-design.md`
- Swagger at `http://localhost:8001/docs`
- UI at `http://localhost:3000`

Mention:

- JWT authentication.
- Refresh-token rotation.
- RBAC for admin.
- Seller ownership via seller profiles.
- Alembic migrations.
- Docker Compose services.

### 3. Customer Demo - 3 minutes

Demo flow:

1. Open landing page.
2. Register or log in as demo customer.
3. Show dashboard counts.
4. Open profile and update phone/address.
5. Browse products.
6. Search/filter products.
7. Open product details.
8. Add to wishlist and cart.
9. Checkout.
10. Show order confirmation and order history.

Talking points:

- Customer profile and address data persist in PostgreSQL.
- Product search uses backend filters and pagination.
- Cart totals and inventory validation come from backend logic.
- Checkout creates order and order items.

### 4. Seller Demo - 2 minutes

Demo flow:

1. Log in as seller.
2. Open `/seller`.
3. Show seller dashboard metrics.
4. Create or update product.
5. Create warehouse/stock if visible in the current UI.
6. Confirm product appears in marketplace after catalog rules allow it.

Talking points:

- Seller profile is tied to authenticated user.
- Products, variants, images, and inventory are persisted.
- Seller dashboard uses real database queries.
- Stock and low-stock metrics are operational signals.

### 5. Admin Demo - 3 minutes

Demo flow:

1. Log in as admin.
2. Open `/admin`.
3. Show dashboard metrics.
4. Open Users tab: suspend/activate.
5. Open Sellers tab: approve/reject.
6. Open Products tab: approve/hide/feature.
7. Open Orders/Payments: status, shipment, sandbox payment.
8. Open Reviews: approve/delete.
9. Open Reports: JSON/CSV/PDF placeholder.
10. Open Notifications: create broadcast.

Talking points:

- Admin APIs are RBAC-protected.
- Moderation actions create audit logs.
- Reports are generated from persisted data.
- Payments are sandbox records and do not call a live gateway.

### 6. AI Demo - 1 minute

"The AI section is intentionally implemented as internal deterministic demo helpers, not an external AI provider. The platform can recommend related products, generate an enterprise-style product description, and summarize review sentiment using existing backend data."

Show:

- Admin AI tab or Product Details as admin.
- Recommendation endpoint.
- Product description endpoint.
- Review summary endpoint.

Disclosure:

- No OpenAI, Claude, Gemini, LangChain, RAG, vector database, or streaming integration is present.

### 7. Testing and CI/CD - 1 minute

"Quality gates include backend compile, Ruff, Pytest, frontend typecheck, Vite build, Playwright E2E, Docker build/start, and GitHub Actions for backend and frontend."

Show:

- `backend/tests/api/`
- `frontend/tests/`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`

### 8. Future Scope - 1 minute

Recommended next phases:

- Real payment gateway integration.
- Email/SMS notification delivery.
- Advanced analytics and reporting exports.
- Stronger admin policy around category/product write permissions.
- Production observability, tracing, and monitoring.
- External AI integration only after security and compliance review.
- Performance indexing and caching for high-volume catalogs.

### 9. Conclusion - 30 seconds

"Atlas Commerce Platform demonstrates an enterprise-ready commerce foundation with customer, seller, and admin workflows, persisted data, validation, automated tests, and Dockerized deployment. It is structured for future production hardening without changing the core architecture."

## Demo Accounts

For seeded demo environments:

```text
Admin: demo.admin@atlasdemo.com / DemoPass123!
Customer: demo.customer001@atlasdemo.com / DemoPass123!
Seller: demo.seller001@atlasdemo.com / DemoPass123!
```

Use demo credentials only in local/demo environments.

## Presentation Checklist

- Docker Compose stack is running.
- `http://localhost:3000` loads.
- `http://localhost:8001/health` returns success.
- `http://localhost:8001/docs` loads.
- Demo accounts are available.
- Product catalog has demo data.
- Checkout flow has at least one valid address and product with stock.
- Admin user has admin role.
- Browser zoom is presentation-friendly.
