# README — Developer Notes

Day-to-day workflow. Pairs with [README.md](README.md) (the *why*); this is the *how*.

## Three commands. That's the whole surface.

```bash
npm run setup     # first time on a laptop — conda env, deps, Docker infra. Idempotent.
npm start         # daily — auto-syncs deps, brings up Docker, starts every scaffolded
                  # service + portal in one terminal via concurrently. Ctrl+C kills all.
npm stop          # hard teardown — Docker containers + volumes + networks gone.
```

> **Migrating from older muscle memory?** `npm run dev:up` / `dev:down` / `infra:up` / `datasets:*` / `setup:*` are all gone — collapsed into the three above. Building blocks are still on disk if you ever need them ([see below](#fallbacks)).

**Data downloads do NOT run from the CLI.** They happen from the admin portal at <http://localhost:4201/administration/data-management/initial-downloads>, which calls `admin-api`, which triggers an Airflow DAG. See [ADR-0007](docs/adr/0007-no-adhoc-downloads-install-discipline.md), [ADR-0012](docs/adr/0012-airflow-for-initial-downloads.md), [ADR-0014](docs/adr/0014-local-dataset-cache-and-idempotent-loads.md).

---

## Prerequisites

| Tool | Version | Used for |
|---|---|---|
| Node | 20+ | Root task runner, favicon generator, Angular portals |
| Conda *(Miniconda / Anaconda)* | recent | Python 3.12 env at `$HOME/runtime_data/python_venvs/TresorAI` |
| Docker Desktop | recent *(daemon running)* | Local infra stacks |
| Java *(JDK 21)* | 21+ | Spring Boot services *(once scaffolded)* |
| Maven | 3.9+ | Build tool for Spring services |
| gcloud CLI | latest | Optional — only when you start working on Cloud Run / Composer (M2+) |

```bash
node --version && conda --version && docker --version
```

---

## First time on a laptop

```bash
npm run setup
```

What runs, in order:

1. Conda env at `$HOME/runtime_data/python_venvs/TresorAI`
2. Python deps for every Python service *(intelligence-service, admin-api)* via uv
3. npm deps at the root and in each portal *(in parallel)*
4. Brand favicon pack regenerated from `design-system/brand/*.svg`
5. Docker infra: Postgres+pgvector, Redis, Kafka *(Apache Kafka 3.9 KRaft mode)*

The script ends with a pointer to the admin portal so you can load datasets through Airflow.

**First run takes ~10–15 min** — most of it is the all-three-AI-tracks Python deps (sklearn, xgboost, torch, transformers, sentence-transformers, google-generativeai, …) and 500+ MB of node_modules per portal. Subsequent `npm start` is ~5–10 s.

> **`npm run setup` is idempotent** — re-run it any time. Conda env, deps, and infra are all "create-if-missing". Use it whenever you suspect your env is out of sync (e.g., a teammate added a new Python service).

---

## Daily

```bash
npm start
```

What runs:

1. **Step 0 — sync npm deps** at root + each portal *(catches teammate package.json changes; fast when nothing changed)*
2. **Step 1 — Docker infra** *(idempotent — already-running containers are fine)*
3. **Step 2/3 — auto-detect + spawn** every scaffolded backend service + portal in **one terminal** with colour-coded prefixes via [`concurrently`](https://www.npmjs.com/package/concurrently). Ctrl+C kills all.

| Colour | Service | URL | Tier |
|---|---|---|---|
| green | `portal-customer` | http://localhost:4200 | frontend |
| blue | `portal-admin` | http://localhost:4201 | frontend |
| white | `admin-api` *(FastAPI · dedicated admin ops)* | http://localhost:8091 | backend |
| yellow | `intelligence-service` *(FastAPI · AI brain)* | http://localhost:8090 | backend |
| cyan | `api-gateway` *(Spring Boot · BFF)* | http://localhost:8080 | backend |
| magenta | `ingest-service` *(Spring Boot · Kafka producer)* | http://localhost:8081 | backend |

Plus Docker (no foreground process — runs detached): `tresorai-postgres :5432`, `tresorai-redis :6379`, `tresorai-kafka :9092`.

If a service hasn't been scaffolded yet, it's silently skipped — `npm start` only spawns what's actually there.

---

## What you'll see in the admin portal

After `npm start`, open <http://localhost:4201>:

1. **Coral-red banner across the top** of every admin page — *"Initial setup required: N datasets must be loaded."* Expand "What's missing?" to see each dataset with its required/optional pill. Click **Run Initial Downloads →** to act.
2. **Initial Downloads page** *(/administration/data-management/initial-downloads)*: live state from `admin-api`. Each accordion shows current status, target table, DAG ID, last-run timestamp + row count. Click **Run download** → button switches to "Running…" with an emerald progress bar (0–100%). Re-clicking a completed dataset short-circuits to **already-present** in <100 ms.
3. **System Health page** *(/system, top nav)*: cloud-aware probe of every backend dependency. Polls every 5 s. Service cards bordered mint when up, coral when down, sand when not configured. Counts up/down/pending at the top. See [Cloud-aware health](#cloud-aware-system-health) below.

---

## Cloud-aware System Health

The System Health page works the same locally and in cloud — the **environment** + **per-service overrides** are env-vars on the `admin-api` container.

```bash
TAI_ENV=local    # local | gcp | aws | azure | hybrid
```

Each value picks a different default service URL set:

| Env | Postgres probe | Kafka probe | Orchestration probe |
|---|---|---|---|
| `local` | `localhost:5432` *(TCP)* | `localhost:9092` *(TCP)* | `localhost:8088/api/v1/health` *(Airflow)* |
| `gcp` | `cloud-sql-postgres` | `confluent-kafka` | `cloud-composer` |
| `aws` | `rds-postgres` | `msk-kafka` | `mwaa-airflow` |
| `azure` | `azure-postgres` | `event-hubs-kafka` | `data-factory` |
| `hybrid` | trust per-service overrides | trust per-service overrides | trust per-service overrides |

Override any single service via env var:

```bash
TAI_SVC_AIRFLOW=http://my-airflow.example.com:8088/api/v1/health
TAI_SVC_POSTGRES=staging-db.example.com:5432
```

`.env.example` has the full template.

---

## Loading datasets *(via admin portal — never CLI)*

1. `npm start` → open <http://localhost:4201/administration/data-management/initial-downloads>
2. Each accordion is a dataset. Click **Run download**.
3. Flow:
   - portal-admin → `POST http://localhost:8091/api/admin/initial-downloads/<key>/run`
   - admin-api → triggers Airflow DAG *(today: in-process simulator while we wire Airflow)*
   - DAG checks local cache at `$HOME/runtime_data/tresorai/datasets/<key>/`:
     - manifest + sha-256 + `_COMPLETE` marker match → status **already-present**, no fetch *(<1 s)*
     - mismatch → fetch from configured cloud storage *(`TAI_STORAGE_PROVIDER` = gcs / s3 / azure)*, verify checksums, write manifest, touch `_COMPLETE`
   - Run + final status persisted to Postgres `initial_downloads_runs` + `initial_downloads_datasets` *(per [data/sql/0001_initial_downloads.sql](data/sql/0001_initial_downloads.sql))*
4. UI polls every 1 s while anything is running; status pill flips to **success** + banner drops the entry.

**Per-tenant install footprint after first load:** ~30–55 GB. Lives at `$HOME/runtime_data/tresorai/datasets/`, outside the repo, survives `git clean -fdx` and reinstalls.

---

## Stopping

```bash
npm stop
```

Hard teardown — containers gone, named volumes wiped, per-project networks removed. **Postgres, Redis, Kafka data is wiped each time.** Datasets at `$HOME/runtime_data/tresorai/datasets/` are *not* touched.

If you want to preserve Postgres / Kafka data across stop/start cycles, run the soft variant directly:

```bash
bash infra/local/docker-all-down.sh    # containers down, volumes preserved
```

---

## Where to look when something fails

| Symptom | Most likely cause | Fix |
|---|---|---|
| `Could not reach admin-api at http://localhost:8091` | Your `dev:up` started before admin-api was scaffolded | `Ctrl+C` → `npm stop` → `npm start` |
| Initial Downloads page is blank / red | admin-api crashed or not in conda env | `npm run setup` to refresh deps, then `npm start` |
| System Health shows everything down | admin-api itself is down | Same as above |
| `Conda env not found at $HOME/...` from `npm start` | `npm run setup` was never run on this laptop | `npm run setup` |
| `npm error Missing script: "dev:up"` | Old muscle memory — script renamed | Use `npm start` |
| Portal compile errors after a teammate's PR | Their `package.json` change; your `npm start` Step 0 picked up new deps but Angular cached the old | Stop, delete `frontend/<portal>/.angular/`, `npm start` again |
| `connection refused` for Postgres / Kafka | Docker daemon not running, or you're on a fresh laptop pre-`npm run setup` | Start Docker Desktop, `npm run setup` |
| Banner says 7 datasets pending after a successful download | The polling didn't refresh — open System Health, confirm admin-api is up, refresh the page once |

For everything else: `npm start` output has prefixed logs per service. The yellow `[intel]`, white `[admin-api]`, etc. lines tell you which service is unhappy.

---

## Common gotchas

- **`conda activate` does not propagate** out of an npm subprocess. Python services are wired to the env's binaries directly *(via `$HOME/runtime_data/python_venvs/TresorAI/bin/uvicorn`)* so `npm start` works without an activated shell. You only need `source ./scripts/conda-activate.sh` if you want to run Python *interactively* in a terminal.
- **Conda env path is intentional** — `$HOME/runtime_data/python_venvs/TresorAI`, outside the repo. Survives `git clean -fdx`. Override with `TAI_DATASETS_ROOT` for `~/runtime_data/tresorai/datasets/` if you want a different disk for the data cache.
- **Kafka KRaft mode** uses port 9092 for clients, 9093 for the internal controller. Keep both free.
- **First `npm run setup`** pulls ~3–5 GB of dependencies (Python wheels for the all-three-AI-tracks stack + node_modules). Subsequent runs are seconds.
- **No ad-hoc downloads anywhere in this codebase** — see [ADR-0007](docs/adr/0007-no-adhoc-downloads-install-discipline.md). If you want `wget` / `curl` / `requests.get(...)` for a dataset, write a DAG instead.
- **`npm stop` is destructive.** It wipes Postgres rows, Kafka topics, Redis cache. If you're iterating on data you care about, use `bash infra/local/docker-all-down.sh` instead.

---

## Fallbacks

The simple-three-command surface covers 99% of daily work. Lower-level building blocks are still on disk for debugging:

| Need | Direct command |
|---|---|
| Bring up only Docker | `bash infra/local/docker-all-up.sh` |
| Stop Docker, **keep** volumes | `bash infra/local/docker-all-down.sh` |
| Hard-stop Docker *(same as `npm stop`)* | `bash infra/local/docker-all-down-hard.sh` |
| Show Docker stack status | `bash infra/local/docker-all-status.sh` |
| Re-create conda env | `bash scripts/conda-create.sh` *(prompts before overwrite)* |
| Re-install Python deps *(both services)* | `bash scripts/python-deps.sh` |
| Re-install portal deps *(parallel)* | `bash scripts/install-portals.sh` |
| Regenerate brand favicons | `node scripts/generate-favicons.js` |
| Activate conda env in your shell | `source ./scripts/conda-activate.sh` |
| Probe admin-api directly | `curl http://localhost:8091/health` |
| Probe System Health JSON | `curl http://localhost:8091/api/admin/system/health \| jq` |

These are the actions `npm run setup` and `npm start` orchestrate. Reach for them only when debugging the orchestration itself.
