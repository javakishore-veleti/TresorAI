# admin-api

Dedicated FastAPI service for portal-admin operations.

## Why a separate service

- **Talks to Airflow REST API** + Vertex AI Model Registry — surfaces api-gateway should never reach.
- **Different IAM boundary** — admin-only; api-gateway is customer-facing.
- **Different deploy cadence** — admin features can lag customer features safely.

## Stack

- Python 3.12 · FastAPI · SQLAlchemy 2 · psycopg 3 · Alembic · httpx
- Talks to: Postgres (initial_downloads_*, audit log), Airflow REST, future Vertex AI Model Registry

## Local

- Port: **8091**
- Health: `GET /health`
- OpenAPI: `GET /docs`

## Deploy

- Cloud Run · `.github/workflows/admin-api.yml` (path-filtered)

## Endpoints (current — stubbed; real Postgres wiring next)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Service + dependency-readiness check |
| GET | `/api/admin/initial-downloads/datasets` | Catalog + current status (powers the pending-setup banner) |
| POST | `/api/admin/initial-downloads/{key}/run` | Trigger Airflow DAG run for a dataset |
| POST | `/internal/airflow/dag-run-callback` | Receive on_success / on_failure callbacks from Airflow |

## Status

Scaffold + stubs. Next: wire Postgres via `data/sql/0001_initial_downloads.sql`, then implement the Airflow REST client.
