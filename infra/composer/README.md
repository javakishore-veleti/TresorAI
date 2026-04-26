# infra/composer/

Cloud Composer 2/3 *(managed Airflow on GCP)* environment manifests + deploy scripts. Production counterpart to `infra/local/airflow/`.

## Planned contents

```
infra/composer/
├── env.tf                   # Terraform — Composer environment (size, region, image version, network)
├── deploy-dags.sh           # gsutil rsync from <repo>/airflow/dags to gs://composer-bucket/dags
├── deploy-plugins.sh        # same for plugins
├── connections.yaml         # Airflow Connections (Postgres, GCS, etc.) — applied via REST API
├── variables.yaml           # Airflow Variables — applied via REST API
└── README.md
```

## Deploy flow (planned, T26+)

1. PR merged that touches `airflow/**` → GitHub Actions workflow `.github/workflows/airflow-dags.yml`
2. Workflow auths to GCP via Workload Identity Federation *(no JSON keys — ADR-0013)*
3. `gsutil rsync -r -d airflow/dags gs://us-east1-tresorai-composer-XXX/dags/`
4. Composer auto-picks up new DAG files within ~30 s

DAG code never lives in this directory — it lives at `<repo>/airflow/dags/`. This directory only contains the deploy machinery.

## Why a separate dir from `infra/cloudrun/`

Different deploy target *(GCS object store, not Cloud Run service revisions)*, different lifecycle *(DAGs deploy on every PR; Cloud Run services deploy independently per ADR-0001)*, different IAM *(Composer service account vs Cloud Run service accounts)*. Keeping them apart matches the per-tool layout we use in `infra/local/`.

## Status

Not started — see plan T26 in `TresorAI_Portfolio_Build_Plan.xlsx`.
