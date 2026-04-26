# ADR-0016: Airflow DAGs live at repo root, not under `infra/local/`

- Status: Accepted
- Date: 2026-04-25

## Context
Apache Airflow runs locally for dev (per ADR-0012) and Cloud Composer runs the same DAGs in GCP (per ADR-0013). Initial implementation placed DAG files inside `infra/local/airflow/dags/`. That directory exists for local docker-compose orchestration only — it ships to no production environment, isn't a path-filter target for any CI workflow, and its name communicates "throwaway."

The user pushed back *(2026-04-25)*: how do these DAGs get to Cloud Composer in production if they live under `infra/local/`?

## Decision
DAGs and plugins live at **`<repo-root>/airflow/`** — a first-class deployable module, not a local-dev artifact.

```
airflow/
├── dags/
│   ├── initial_downloads/
│   ├── classical_ml/
│   ├── deep_learning/
│   ├── generative_ai/
│   └── shared/
├── plugins/
└── requirements.txt        (optional — extra packages for the Airflow image)
```

- **Local** — `infra/local/airflow/docker-compose.yaml` bind-mounts `../../../airflow/dags` and `../../../airflow/plugins` into the scheduler + webserver containers. Edit a DAG → Airflow reloads in ~30 s.
- **Production (GCP)** — `infra/composer/deploy-dags.sh` runs `gsutil rsync -r -d airflow/dags/ gs://composer-bucket/dags/` from a GitHub Actions workflow that path-filters on `airflow/**`.

## Consequences

- (+) **Same code, two environments** — local Airflow and Cloud Composer mount/serve the *exact* same files.
- (+) **Discoverable** — `airflow/` at the repo root signals "this is a real subsystem," not a local hack.
- (+) **Path-filter-friendly** — one CI workflow watches `airflow/**` and only runs when DAG code changes.
- (+) **Mirrors the rest of the monorepo** — frontend / backend / contracts / data / docs all sit at the root; Airflow joins them.
- (+) **Deploy story is one line** — `gsutil rsync` from `airflow/dags` to the GCS bucket. No build step, no container.
- (−) **One more top-level directory** to scan when reading the repo. Mitigated by clear `airflow/README.md`.
- (−) **`infra/local/airflow/` now contains only the docker-compose + logs** — slight redundancy with the directory name, but the per-tool pattern is consistent with postgres/redis/kafka under the same parent.

## Migration

- DAGs that were under `infra/local/airflow/dags/` moved to `airflow/dags/<track>/`.
- `infra/local/airflow/docker-compose.yaml` updated to bind-mount `../../../airflow/`.
- `infra/composer/` directory created for the future Cloud Composer deploy script.
