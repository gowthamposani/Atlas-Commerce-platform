# Deployment Guide

## Deployment Model

Atlas Commerce Platform is designed for containerized deployment. The local release model uses Docker Compose with three services:

- PostgreSQL database.
- FastAPI backend.
- Nginx-served React frontend.

Production deployment can use the same container boundaries with managed PostgreSQL and an orchestrator such as Kubernetes, ECS, or a VM-based Docker runtime.

## Environment Variables

### Backend

| Variable | Purpose | Production Guidance |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database connection | Use managed PostgreSQL with SSL where required |
| `JWT_SECRET_KEY` | JWT signing secret | Use a long random secret from a secret manager |
| `JWT_ALGORITHM` | JWT algorithm | Keep `HS256` unless security architecture changes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime | Keep short, e.g. 15 minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh-token lifetime | Tune to business policy |
| `PHONE_MIN_DIGITS` | Minimum phone digit count | Default 10 |
| `PHONE_MAX_DIGITS` | Maximum phone digit count | Default 15 |
| `CORS_ORIGINS` | Allowed browser origins | Restrict to production frontend domains |

### Frontend

| Variable | Purpose | Production Guidance |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Backend API URL embedded at build time | Set to production API origin plus `/api` |

## Docker Compose Deployment

Build and start:

```text
docker compose up --build -d
```

Check status:

```text
docker compose ps
```

Check logs:

```text
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

Stop:

```text
docker compose down
```

## Startup Steps

1. Provision PostgreSQL.
2. Configure environment variables.
3. Build backend image.
4. Build frontend image with correct `VITE_API_BASE_URL`.
5. Run migrations before serving traffic.
6. Start backend.
7. Start frontend.
8. Verify health and smoke flows.

## Database Migration

Alembic migrations are located under `backend/alembic`. Migration validation is part of backend CI. In production, run:

```text
cd backend
alembic -c alembic.ini upgrade head
```

Use backup and rollback procedures before applying migrations in production.

## Production Notes

- Replace all default secrets.
- Enforce HTTPS through load balancer or reverse proxy.
- Restrict CORS to known production origins.
- Use a managed PostgreSQL instance with backups and monitoring.
- Run containers as non-root where possible.
- Configure centralized logs.
- Use health checks for backend and frontend.
- Keep demo seed data out of production unless explicitly needed for a demo environment.
- Treat sandbox payments and internal AI helpers as demo features, not production integrations.
- Consider separate admin domain or network policy for admin routes.

## Post-deployment Verification

- `GET /health` returns `{"status":"ok"}`.
- `/docs` loads for authorized internal environments.
- Registration/login works.
- Product listing loads.
- Cart and checkout persist data.
- Admin dashboard loads with admin account.
- CI pipeline is green for the release commit.
