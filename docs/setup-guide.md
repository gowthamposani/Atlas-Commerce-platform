# Setup Guide

## Prerequisites

- Docker Desktop or Docker Engine with Compose.
- Python 3.12 for local backend development.
- Node.js 20 for local frontend development.
- PostgreSQL client tools are optional for inspection.

## Repository Layout

```text
backend/      FastAPI, SQLAlchemy, Alembic, Pytest
frontend/     React, TypeScript, Tailwind, Playwright
docker/       Dockerfiles and Nginx config
docs/         Enterprise documentation
```

## Docker Compose Startup

From the repository root:

```text
docker compose up --build -d
```

Services:

- Frontend: `http://localhost:3000`
- Backend API docs: `http://localhost:8001/docs`
- Health endpoint: `http://localhost:8001/health`
- PostgreSQL: internal Docker network service `db:5432`

Stop services:

```text
docker compose down
```

## Backend Local Development

Install dependencies:

```text
python -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
```

Run quality gates:

```text
.venv/bin/python -m compileall backend/app
.venv/bin/ruff check backend/app backend/tests
.venv/bin/python -m pytest
```

Run Alembic from `backend/` when needed:

```text
cd backend
alembic -c alembic.ini upgrade head
```

## Frontend Local Development

Install dependencies:

```text
cd frontend
npm install
```

Run checks:

```text
npm run lint
npm run build
npx playwright test
```

## Environment Variables

Backend:

- `DATABASE_URL`: SQLAlchemy database URL. Docker default is `postgresql+psycopg://atlas:atlas@db:5432/atlas_commerce`.
- `JWT_SECRET_KEY`: secret key for JWT signing. Must be replaced in production.
- `JWT_ALGORITHM`: default `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: default `15`.
- `REFRESH_TOKEN_EXPIRE_DAYS`: default `7`.
- `PHONE_MIN_DIGITS`: default `10`.
- `PHONE_MAX_DIGITS`: default `15`.
- `CORS_ORIGINS`: JSON list of allowed frontend origins.

Frontend:

- `VITE_API_BASE_URL`: API base URL. Docker build arg defaults to `http://localhost:8001/api`.

## Demo Data

The repository contains an idempotent demo seed module in `backend/app/database/seed_demo.py`. It creates demo customers, sellers, categories, products, orders, reviews, notifications, and an admin account using deterministic IDs. Demo credentials are intentionally for local demonstration only and must not be used in production.

## Common URLs

- UI: `http://localhost:3000`
- Swagger: `http://localhost:8001/docs`
- Health: `http://localhost:8001/health`

## Troubleshooting

- If frontend cannot call backend, verify `VITE_API_BASE_URL` and CORS origins.
- If backend cannot start, verify PostgreSQL health and `DATABASE_URL`.
- If login fails for demo users, confirm demo data was seeded into the active database volume.
- If Playwright cannot start, install browsers with `npx playwright install chromium`.
- If Docker ports are occupied, stop the conflicting process or remap ports in Compose for local-only testing.
