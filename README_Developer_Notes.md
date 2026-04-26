# README — Developer Notes

Day-to-day workflow. Pairs with [README.md](README.md) (the *why*); this is the *how*.

## The only three commands you need

```bash
npm run setup     # first time on a laptop — conda env, deps, Docker infra. Idempotent.
npm start         # daily — auto-syncs deps, brings up Docker, starts every scaffolded
                  # service + portal in one terminal via concurrently. Ctrl+C kills all.
npm stop          # hard teardown — Docker containers + volumes + networks gone.
```

That's it. **Data downloads do NOT run from the CLI** — they happen from the admin
portal *(http://localhost:4201/administration/data-management/initial-downloads)*
which triggers Airflow DAGs. See [ADR-0007](docs/adr/0007-no-adhoc-downloads-install-discipline.md) and [ADR-0012](docs/adr/0012-airflow-for-initial-downloads.md).

---

## Prerequisites

| Tool | Version |
|---|---|
| Node | 20+ |
| Conda | recent (Miniconda or Anaconda) |
| Docker Desktop | recent (daemon must be running) |
| Java | 21+ *(once Spring Boot services are scaffolded)* |
| Maven | 3.9+ *(same)* |

```bash
node --version && conda --version && docker --version
```

---

## First time

```bash
npm run setup
```

This runs in sequence:

1. Create conda env at `$HOME/runtime_data/python_venvs/TresorAI`
2. Install Python deps for every Python service *(intelligence-service, admin-api)*
3. Install npm deps at the root and in each portal *(in parallel)*
4. Generate the brand favicons
5. Bring up Docker infra *(Postgres+pgvector, Redis, Kafka)*

Then it tells you to open the admin portal to load datasets via Airflow.

---

## Daily

```bash
npm start
```

What it does, automatically:

- Syncs npm deps at root + portals *(picks up teammate package.json changes)*
- Brings up Docker infra *(idempotent — already-running containers are fine)*
- Spawns every scaffolded backend service + portal in **one terminal**, colour-coded:

| Colour | Service | URL |
|---|---|---|
| green | portal-customer | http://localhost:4200 |
| blue | portal-admin | http://localhost:4201 |
| yellow | intelligence-service *(FastAPI)* | http://localhost:8090 |
| white | admin-api *(FastAPI, dedicated admin ops)* | http://localhost:8091 |
| cyan | api-gateway *(Spring Boot)* | http://localhost:8080 |
| magenta | ingest-service *(Spring Boot)* | http://localhost:8081 |

Ctrl+C kills all of them.

---

## Loading datasets *(via admin portal — never CLI)*

After `npm start`:

1. Open <http://localhost:4201/administration/data-management/initial-downloads>
2. Each accordion is a dataset. Click **Run download** on the ones you want.
3. Each click triggers an Airflow DAG via the admin-api service. The DAG:
   - Checks the local cache at `$HOME/runtime_data/tresorai/datasets/<key>/`
   - Skips fetch if files + sha-256 + manifest already match *(<1 s)*
   - Otherwise fetches from the configured cloud storage *(GCS / S3 / Azure — `TAI_STORAGE_PROVIDER`)*
   - Verifies checksums, touches `_COMPLETE`, registers the run in Postgres
4. The pending-setup banner at the top of the admin portal shows what's still missing.

Total cache footprint after first install: **30–55 GB** *(survives `git clean -fdx` and reinstalls)*.

---

## Stopping

```bash
npm stop
```

Hard teardown — Postgres, Redis, Kafka data volumes are wiped along with containers. Datasets at `$HOME/runtime_data/tresorai/datasets/` are NOT touched *(they're outside the repo)*.

For a soft stop that preserves data, run directly: `bash infra/local/docker-all-down.sh`.

---

## Common gotchas

- **`conda activate` from npm scripts can't propagate** to your terminal. The Python services are wired to the env's binaries directly, so `npm start` works without activating in your shell. You only need to source `./scripts/conda-activate.sh` if you want to run Python *interactively* in a terminal.
- **Cache lives at `$HOME/runtime_data/tresorai/datasets/`** — outside the repo. Override with `TAI_DATASETS_ROOT` if you need a different disk.
- **First `npm run setup` is slow** *(~10–15 min)* — Python deps for all three AI/ML tracks (sklearn, xgboost, torch, transformers, sentence-transformers, gemini SDK, ...) plus 500+ MB of node_modules per portal. Subsequent `npm start` is ~5–10 seconds.
- **Kafka uses KRaft mode** — port 9092 for clients, 9093 for the internal controller. Keep both free.
- **No ad-hoc downloads** — see ADR-0007. If you find yourself wanting `wget` or `curl` for dataset fetches, add a DAG instead.

---

## What if you really need to run something specific?

The simple-three-command surface covers 99% of daily work. The lower-level scripts are still here for debugging:

| Need | Direct command |
|---|---|
| Bring up only Docker | `bash infra/local/docker-all-up.sh` |
| Bring down Docker, KEEP volumes | `bash infra/local/docker-all-down.sh` |
| Show Docker stack status | `bash infra/local/docker-all-status.sh` |
| Re-create conda env | `bash scripts/conda-create.sh` *(prompts before overwrite)* |
| Re-install Python deps | `bash scripts/python-deps.sh` |
| Re-install portal deps | `bash scripts/install-portals.sh` |
| Regenerate brand favicons | `node scripts/generate-favicons.js` |

These are the building blocks `npm run setup` and `npm start` orchestrate.
