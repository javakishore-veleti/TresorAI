# README — Developer Notes

Day-to-day workflow for working on TrésorAI locally. Pairs with the main [README.md](README.md), which covers the *why*; this file covers the *how*.

## Table of contents

1. [Prerequisites](#1-prerequisites)
2. [First time](#2-first-time)
3. [Starting daily](#3-starting-daily) — Docker → env → middleware → apps → UI
4. [Running the apps](#4-running-the-apps)
5. [Shutting down daily](#5-shutting-down-daily) — UI → apps → middleware → env → Docker
6. [npm command cheatsheet](#6-npm-command-cheatsheet)
7. [Common gotchas](#7-common-gotchas)

---

## 1. Prerequisites

Install once on the laptop.

| Tool | Version | Used for |
|---|---|---|
| **Node** | 20+ | Root task runner (`npm run …`), favicon generator, Angular portals |
| **Conda** *(Miniconda / Anaconda)* | recent | Python 3.12 env at `$HOME/runtime_data/python_venvs/TresorAI` |
| **Docker Desktop** | recent | Local infra stacks (Postgres+pgvector, Redis, Kafka) |
| **Java** *(JDK 21)* | 21+ | Spring Boot services *(scaffolded later)* |
| **Maven** | 3.9+ | Build tool for the Spring services |
| **gcloud CLI** | latest | Optional — only needed once you start on Cloud Run (M2) |

Verify:

```bash
node --version          # >= 20
conda --version
docker --version        # daemon must be running
java -version           # >= 21
mvn --version           # >= 3.9
```

---

## 2. First time

Run these once after cloning the repo. **You are roughly here right now** if you just ran `setup:conda:create`.

```bash
# 1. Install root npm deps (sharp + png-to-ico for the favicon generator)
npm install

# 2. Create the conda env at $HOME/runtime_data/python_venvs/TresorAI
npm run setup:conda:create

# 3. Activate the env (must be sourced — npm cannot do this for you)
source ./scripts/conda-activate.sh

# 4. Install Python deps for intelligence-service
#    Today: a no-op — service not scaffolded yet. Will install real deps after T06.
npm run setup:python:deps

# 5. Start local infra (Postgres+pgvector, Redis, Kafka)
npm run infra:up
npm run infra:status

# 6. (Only if you edited design-system/brand/*.svg) regenerate the favicons
npm run generate:favicons
```

Or just one command for the whole sequence:

```bash
npm run setup:initial:all
```

> `setup:initial:all` runs steps 2 → 4 → 5 → 6 → the Initial Downloads placeholder. Activation in step 3 must still be done by you because shell state cannot leak out of an npm subprocess.

---

## 3. Starting daily

### One-command flow *(recommended)*

```bash
# Brings up Docker infra AND every backend service / portal that has been scaffolded.
# Today: only Docker comes up (services not scaffolded yet). The same command grows
# automatically as T02 / T03 / T03b / T04 / T05 / T06 land — no script changes needed.
npm run dev:up

# Activate conda env in your terminal (separate step — shell state cannot
# leak out of an npm subprocess; the spawned Python services are wired to
# the env's binaries directly, so they don't need this).
source ./scripts/conda-activate.sh
```

`dev:up` runs all services in **one terminal** with colour-coded prefixes via [`concurrently`](https://www.npmjs.com/package/concurrently). Ctrl+C kills them all.

### Step-by-step flow *(if you want to start things selectively)*

Order: **Docker → conda env → middleware → backend services → frontend portals.**

```bash
# A. Docker — local infra stacks
npm run infra:up
npm run infra:status                          # verify all containers healthy

# B. Conda env (in every terminal where you'll run Python)
source ./scripts/conda-activate.sh

# C. Middleware — none today (contracts tooling lands at T02)

# D. Backend services — each in its own terminal, after they're scaffolded
#    intelligence-service (Python / FastAPI)               [available after T06]
cd backend/intelligence-service && uvicorn app.main:app --reload --port 8090

#    api-gateway (Java / Spring Boot)                      [available after T04]
cd backend/api-gateway     && mvn spring-boot:run

#    ingest-service (Java / Spring Boot)                   [available after T05]
cd backend/ingest-service  && mvn spring-boot:run

# E. Frontend portals — each in its own terminal
#    portal-customer                                       [available after T03]
cd frontend/portal-customer && npm install && npm run start    # http://localhost:4200

#    portal-admin                                          [available after T03b]
cd frontend/portal-admin    && npm install && npm run start    # http://localhost:4201
```

**Today's reality:** only steps A and B run end-to-end. Steps C–E activate as we land T02, T03, T03b, T04, T05, T06.

---

## 4. Running the apps

Once steps A–E above are up, these endpoints exist:

| URL | Service |
|---|---|
| http://localhost:4200 | `portal-customer` — SMB CFO UX |
| http://localhost:4201 | `portal-admin` — ops + install UX |
| http://localhost:8080 | `api-gateway` — REST + WebSocket |
| http://localhost:8080/actuator/health | `api-gateway` health |
| http://localhost:8081/actuator/health | `ingest-service` health |
| http://localhost:8090/health | `intelligence-service` health |
| http://localhost:8090/docs | `intelligence-service` Swagger UI |
| `postgres://localhost:5432/tresorai` | Postgres + pgvector — user `tresorai`, pwd `tresorai` |
| `redis://localhost:6379` | Redis |
| `kafka://localhost:9092` | Apache Kafka 3.9 (KRaft mode, no Zookeeper) |

Quick smoke checks:

```bash
# Postgres + pgvector extension
psql postgresql://tresorai:tresorai@localhost:5432/tresorai -c "SELECT extname FROM pg_extension;"
# Expect: vector, pg_trgm, plpgsql

# Redis
docker exec -it tresorai-redis redis-cli ping
# Expect: PONG

# Kafka — list topics
docker exec -it tresorai-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

---

## 5. Shutting down daily

### One-command flow *(if you started with `npm run dev:up`)*

```bash
# Step 1: in the dev:up terminal, press Ctrl+C — this kills every running
# service and portal that concurrently spawned.

# Step 2: stop the Docker stacks.
npm run dev:down

# Step 3: deactivate the conda env (in every terminal where you sourced activate).
source ./scripts/conda-deactivate.sh
```

### Step-by-step flow *(reverse the startup order)*

Order: **UI → apps → middleware → conda env → Docker.**

```bash
# A. Frontend portals
#    Ctrl+C in each terminal running `ng serve` / `npm run start`.

# B. Backend services
#    Ctrl+C in each terminal running `mvn spring-boot:run` / `uvicorn`.

# C. Middleware — none today.

# D. Conda env (in every shell where you sourced activate)
source ./scripts/conda-deactivate.sh

# E. Docker stacks
npm run infra:down
```

To fully wipe local data (use sparingly — destroys Postgres / Kafka volumes):

```bash
npm run infra:down
docker volume rm tresorai_pg_data tresorai_redis_data tresorai_kafka_data
```

---

## 6. npm command cheatsheet

| Command | What it does |
|---|---|
| `npm run setup:initial:all` | Full first-time setup: conda → python deps → infra → favicons → Initial Downloads placeholder |
| `npm run setup:conda:create` | Create the conda env at `$HOME/runtime_data/python_venvs/TresorAI` |
| `npm run setup:conda:remove` | Remove the conda env (confirms first) |
| `npm run env:activate` | Print the `source` command for activation |
| `npm run env:deactivate` | Print the `source` command for deactivation |
| `npm run setup:python:deps` | Install / upgrade `intelligence-service` Python deps (uv → pip fallback) |
| `npm run infra:up` | Start Docker stacks (Postgres+pgvector, Redis, Kafka) |
| `npm run infra:status` | `docker compose ps` for each active stack |
| `npm run infra:down` | Stop Docker stacks |
| `npm run dev:up` | **One-shot dev start** — Docker + every scaffolded service + both portals, multiplexed via `concurrently`. Ctrl+C kills all. |
| `npm run dev:down` | Stop Docker stacks (run after Ctrl+C in `dev:up`) |
| `npm run generate:favicons` | Regenerate favicon pack from `design-system/brand/*.svg` |
| `npm run setup:initial:downloads` | Placeholder — real Initial Downloads runs from `portal-admin` (T22b) |

---

## 7. Common gotchas

- **`conda activate` cannot run from inside an npm script.** Shell state from a subprocess never propagates to your terminal. That is why activate / deactivate are sourced shell scripts, not npm scripts. Always run `source ./scripts/conda-activate.sh` *directly* in each terminal that needs the env.
- **Docker images are pinned to versions already cached locally.** A fresh laptop will pull on the first `infra:up`. See `infra/local/README.md` for the locked tags.
- **Kafka uses KRaft mode** — port 9092 for clients, 9093 for the internal controller. Keep both free.
- **Per-module `npm install`** lives in each portal directory after `T03` / `T03b`. Root-level `npm install` only pulls in the favicon generator's deps.
- **Conda env path is deliberate.** `$HOME/runtime_data/python_venvs/TresorAI` lives outside the repo so `git clean -fdx` cannot wipe it. See ADR-0009.
- **No ad-hoc downloads.** Reference data is only seeded through the admin portal Initial Downloads UI (or its scripted CLI counterpart). See ADR-0007. Do **not** add `wget` / `curl` data-load scripts anywhere outside that flow.
- **macOS Docker first-pull** for Postgres + Kafka can take a few minutes; later runs are instant.
- **Add a new local infra stack** by creating `infra/local/<tool>/docker-compose.yaml` and adding `<tool>` to the `STACKS` array in all three `docker-all-*.sh` scripts. See ADR-0008.
