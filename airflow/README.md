# airflow/

**Production-deployable** Airflow DAGs and plugins. Same code runs locally and in Cloud Composer.

## Layout — organized by **business function**, not technical paradigm

```
airflow/
├── dags/
│   ├── tenant_onboarding/        One-shot loads at install time (demo seed, PaySim, Yelp corpus)
│   ├── supplier_intelligence/    KYV ongoing — sanctions refresh, IBAN typosquat, country codes
│   ├── ap_fraud_catch/           Fraud-detection model lifecycle (XGBoost / Isolation Forest train+eval+promote)
│   ├── cash_flow_forecasting/    Forecast model lifecycle (Prophet / TFT)
│   ├── agent_reasoning/          Agent quality eval, prompt regression, RAG corpus refresh
│   ├── audit_compliance/         Audit log exports, retention archives
│   ├── model_performance/        Drift detection, decision replay, model promotion
│   └── shared/                   Cross-cutting helpers — the idempotent-load DAG factory
├── plugins/                      Custom Airflow operators / hooks / sensors
└── requirements.txt              (when needed) extra Python deps for the Airflow image
```

DAGs are bucketed by what a business stakeholder would talk about — *"who runs this and when?"* — not by which Python library they happen to import. The implementation detail (XGBoost vs PyTorch vs Gemini) lives inside the DAG, not in the directory name.

## Local

`infra/local/airflow/docker-compose.yaml` bind-mounts `dags/` and `plugins/` from this directory into the Airflow scheduler + webserver containers. Saves a DAG file → reload happens automatically (Airflow polls every 30 s).

Web UI: http://localhost:8088 *(admin / admin)*
REST API: http://localhost:8088/api/v1/

## Production (GCP — Cloud Composer)

Deploy is a one-way sync from this directory to the Composer-managed GCS bucket:

```bash
gsutil rsync -r -d airflow/dags/    gs://us-east1-tresorai-composer-XXX/dags/
gsutil rsync -r -d airflow/plugins/ gs://us-east1-tresorai-composer-XXX/plugins/
```

Wired up in `.github/workflows/airflow-dags.yml` (planned, T26+) — triggered on PR merge that touches `airflow/**`.

`infra/composer/` holds the Composer environment manifests + the deploy script.

## DAG conventions

Every DAG ID is namespaced by track:

| Family | Prefix | Example |
|---|---|---|
| Initial Downloads | `dag_*_load` / `dag_*_refresh` | `dag_supplier_reference_load`, `dag_ofac_sdn_refresh` |
| Classical ML | `dag_<model>_<verb>` | `dag_xgboost_fraud_train`, `dag_xgboost_fraud_promote` |
| Deep Learning | `dag_<model>_<verb>` | `dag_embedding_finetune_train`, `dag_tft_cash_forecast_train` |
| Generative AI | `dag_<surface>_<verb>` | `dag_agent_eval_suite`, `dag_prompt_regression_test`, `dag_rag_corpus_refresh` |

Every dataset DAG follows the idempotent pattern from ADR-0014:

```
[check_local_files] → branch → [download_via_storage_adapter] → [verify_checksums] → [register_run]
                            ↘ [register_run_already_present]
```

`register_run` POSTs to `${TAI_ADMIN_API_URL}/internal/airflow/dag-run-callback` so the admin portal sees fresh status.

## Why repo-root, not `infra/local/`

`infra/local/` is local-dev-only — it never ships to the cloud. DAGs ARE production code; they ship to Cloud Composer via GCS sync. Having them at the repo root keeps the deploy artifact discoverable and lets a single GitHub Actions workflow path-filter on `airflow/**`. *(See [ADR-0016](../docs/adr/0016-airflow-dags-as-deployable-artifact.md).)*
