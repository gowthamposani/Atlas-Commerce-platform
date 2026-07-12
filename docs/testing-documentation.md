# Testing Documentation

## Testing Objectives

- Confirm business-critical workflows function end to end.
- Validate API persistence, validation, authentication, and RBAC.
- Prevent regressions through CI.
- Confirm browser UI integrates with backend APIs.

## Manual Testing

### Customer Manual Tests

1. Register with valid account data.
2. Register with invalid email, weak password, numeric name, invalid phone, and duplicate email.
3. Login with valid and invalid credentials.
4. Update profile with valid and invalid phone.
5. Create, update, default, and delete address.
6. Browse categories and products.
7. Search with normal text, empty text, and whitespace text.
8. Apply price/category filters.
9. Open product detail.
10. Add product to wishlist.
11. Move wishlist item to cart.
12. Update cart quantity.
13. Checkout with invalid and valid billing/shipping data.
14. View order confirmation, order history, and order details.
15. Logout.

### Seller Manual Tests

1. Register seller profile.
2. Update seller profile.
3. Create product with image and variant.
4. Validate product form errors for missing category/name, invalid URL, invalid SKU, and non-positive price.
5. Create warehouse.
6. Upsert inventory.
7. Validate inventory errors for negative quantity and reserved quantity greater than quantity.
8. Confirm seller dashboard metrics update.

### Admin Manual Tests

1. Login as admin.
2. Verify overview dashboard metrics.
3. Search/list users and suspend/activate user.
4. Approve/reject seller.
5. Approve/hide/feature product.
6. Review orders and update order status.
7. Create shipment and verify tracking/status fields.
8. Moderate reviews.
9. Generate JSON, CSV, and PDF-placeholder reports.
10. Create notification.
11. Create sandbox payment intent and update payment status.
12. Use AI recommendation, description, and review summary helpers.

## API Testing

API tests should validate:

- Status codes.
- Response schema shape.
- Database persistence.
- Ownership boundaries.
- RBAC restrictions.
- Input validation.
- Duplicate prevention.
- Inventory and checkout calculations.

Current backend tests are stored in `backend/tests/api/`:

- `test_auth_customer.py`
- `test_marketplace_shopping.py`
- `test_admin_enterprise.py`

Run:

```text
pytest backend/tests
```

or, in the local virtual environment:

```text
.venv/bin/python -m pytest
```

## Pytest

Pytest uses FastAPI test client and test database configuration. It covers:

- Auth register/login/profile/address validation.
- Marketplace shopping flow.
- Admin enterprise APIs including reports, moderation, payments, and AI helpers.

Recommended additions for future hardening:

- More negative RBAC tests.
- More duplicate SKU/coupon/warehouse-code tests.
- Checkout financial calculation matrix.
- PostgreSQL-specific integration test job.

## Playwright

Playwright tests are stored in `frontend/tests/`.

Current flows:

- `auth-profile.spec.ts`: landing -> register -> login -> profile update -> logout.
- `marketplace-flow.spec.ts`: login -> browse -> wishlist -> cart -> checkout -> order history -> logout.

Run:

```text
cd frontend
npx playwright test
```

## Frontend Quality

Run:

```text
cd frontend
npm run lint
npm run build
```

The lint command performs TypeScript no-emit checking. The build command runs TypeScript build and Vite production build.

## Backend Quality

Run:

```text
python -m compileall backend/app
ruff check backend/app backend/tests
pytest backend/tests
```

## Docker Verification

Run:

```text
docker compose build
docker compose up -d
```

Verify:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8001/docs`
- Health: `http://localhost:8001/health`

## CI Pipeline

Backend CI:

1. Checkout.
2. Set up Python 3.12.
3. Install backend dependencies.
4. Compile backend.
5. Run Ruff.
6. Validate Alembic migrations.
7. Run Pytest.

Frontend CI:

1. Checkout.
2. Set up Node 20.
3. Set up Python 3.12 for Playwright backend.
4. Install backend dependencies.
5. Install frontend dependencies.
6. Run frontend lint/typecheck.
7. Build frontend.
8. Install Playwright Chromium.
9. Run Playwright tests.

## Release Acceptance Criteria

- Backend compiles.
- Ruff passes.
- Pytest passes.
- Frontend lint passes.
- Frontend build passes.
- Playwright passes.
- Docker Compose starts frontend, backend, and database.
- Health endpoint returns success.
- Swagger docs are accessible.
- Manual customer, seller, and admin smoke flows pass.
