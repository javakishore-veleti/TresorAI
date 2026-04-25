# infra/local

Local development infrastructure. **One docker-compose.yaml per tool**, orchestrated by three sibling scripts.

## Layout

```
infra/local/
├── docker-all-up.sh        # bring up all active stacks (in dep order)
├── docker-all-down.sh      # stop all active stacks (reverse order)
├── docker-all-status.sh    # `docker compose ps` for each active stack
├── postgres/
│   ├── docker-compose.yaml # pgvector/pgvector:pg16
│   └── init.sql            # CREATE EXTENSION vector; pg_trgm
├── redis/
│   └── docker-compose.yaml # redis:7-alpine
├── kafka/
│   └── docker-compose.yaml # apache/kafka:3.9.0 (KRaft, no Zookeeper)
├── qdrant/                 # COMMENTED OUT — pgvector is primary (ADR-003)
│   └── docker-compose.yaml
└── mlflow/                 # COMMENTED OUT — XGBoost tracking (M5 scope)
    └── docker-compose.yaml
```

## Usage

```bash
# from repo root
npm run infra:up
npm run infra:status
npm run infra:down

# or directly
./infra/local/docker-all-up.sh
./infra/local/docker-all-status.sh
./infra/local/docker-all-down.sh
```

## Why per-tool compose files (not one mega-compose)

- **Independent lifecycle** — start postgres without booting kafka while iterating.
- **Independent versioning** — bump kafka without touching postgres compose.
- **Easier mental model** — one tool's config in one place; matches how the project's CI/CD also runs per-module.
- **Selective enablement** — keep heavyweight stacks (qdrant, mlflow) defined but commented out in the orchestrator until needed.

## Adding a new stack

1. Create `infra/local/<name>/docker-compose.yaml`.
2. Add `<name>` to the `STACKS` array in all three `docker-all-*.sh` scripts (in the right dependency order; up/status share order, down is reversed).
3. Document the image, port, and any one-time setup here.

## Image policy

Pin to a specific tag — never `:latest`. Where possible, prefer images already pulled on the developer's machine to avoid registry round-trips. Current pins reflect what is locally cached as of 2026-04-25.

## Active vs commented stacks

The locked plan (ADRs 002–003) calls for postgres + redis + kafka. Anything beyond that is staged in commented form so the structure is ready when scope expands. To enable, uncomment the stack in all three orchestrator scripts.
