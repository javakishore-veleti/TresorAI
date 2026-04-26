# ADR-0012: Apache Airflow + Cloud Composer as the orchestration substrate for all three AI/ML tracks

- Status: Accepted
- Date: 2026-04-25

## Context
TrésorAI is not a pure GenAI demo — it ships **three AI/ML tracks** that together solve the SMB AP-fraud + treasury problem:

1. **Classical ML** — XGBoost fraud classifier, LightGBM cash baseline, Isolation Forest tabular anomaly, logistic baseline for compliance/explainability, Random Forest feature-importance.
2. **Deep Learning** — fine-tuned embeddings on per-channel supplier corpora, Temporal Fusion Transformer for cash forecasting, tabular autoencoder for anomaly, seq2seq for transaction-context modelling.
3. **Generative AI** — Gemini 2.0 Flash agent loop with tool use, prompt registry, few-shot library, LLM-as-judge eval suite, RAG corpus refresh.

Each track has training, eval, promotion, drift-monitoring, and inference workflows. At enterprise scale (1 000+ tenants under one channel partner, 5–7 yr retention, sanctions refreshes daily, eval cycles continuous), this is **150–250 DAG runs/day per channel**. Direct cron + scripts in `api-gateway` is not viable — we need real orchestration with retries, lineage, scheduling, dependency graphs, and an audit trail.

We considered: (a) Cron + scripts in api-gateway, (b) Cloud Workflows, (c) Cloud Run Jobs, (d) Apache Airflow + Cloud Composer.

## Decision
**Apache Airflow** as the orchestration substrate for all three tracks plus Initial Downloads.

- **Local:** Apache Airflow 2.10 via `infra/local/airflow/docker-compose.yaml`, image pinned to `apache/airflow:2.10.0-python3.12` *(already cached on developer laptops; matches the project Python 3.12 standard)*.
- **Cloud:** **Google Cloud Composer 2** *(or Composer 3 once GA in our chosen region)* — Google's managed Airflow on GKE. Same DAG code runs locally and in cloud; only the connection IDs and pool sizes differ.
- **Async invocation from admin portal:** `Run download` / `Run training` / `Run eval` buttons → `api-gateway` records intent in Postgres → calls Airflow REST API `POST /api/v1/dags/<dag_id>/dagRuns` with `dag_run_conf` → returns 202 with `run_id`. Status updates flow back via Airflow `on_success_callback` / `on_failure_callback` posting to api-gateway, with polling as fallback.

### DAG inventory (canonical)

| Family | DAGs | Cadence |
|---|---|---|
| **Initial Downloads** *(reference data, not ML)* | `dag_supplier_reference_load` · `dag_iban_typosquat_load` · `dag_demo_seed_load` · `dag_ofac_sdn_refresh` · `dag_eu_sanctions_refresh` · `dag_uk_sanctions_refresh` · `dag_un_sanctions_refresh` · `dag_iso_country_codes_load` · `dag_yelp_supplier_corpus_load` · `dag_paysim_extended_load` · `dag_opencorporates_index_load` *(optional)* | Daily / quarterly / yearly / on-demand |
| **Classical ML** | `dag_xgboost_fraud_train` · `dag_xgboost_fraud_eval` · `dag_xgboost_fraud_promote` · `dag_iso_forest_train` · `dag_lgbm_cash_baseline_train` · `dag_logistic_compliance_baseline` · `dag_rf_feature_importance` | Weekly per tenant; promote daily |
| **Deep Learning** | `dag_embedding_finetune_train` · `dag_embedding_eval` · `dag_embedding_deploy` · `dag_tft_cash_forecast_train` · `dag_autoencoder_anomaly_train` · `dag_seq2seq_tx_context_train` · `dag_dl_model_promote` | Monthly per model; eval continuous |
| **Generative AI** | `dag_agent_eval_suite` · `dag_prompt_regression_test` · `dag_rag_corpus_refresh` · `dag_few_shot_curate` · `dag_prompt_promote_canary` · `dag_token_spend_audit` | Daily / on prompt change |
| **Cross-cutting** | `dag_decision_audit_export` · `dag_feature_engineering_pipeline` · `dag_model_registry_sync` · `dag_drift_monitor_all_tracks` · `dag_per_tenant_kpi_rollup` | Hourly / daily |

Total: **~30 DAGs**, **~150–250 runs/day per channel partner** in production.

## Consequences

- (+) **One orchestrator, three tracks** — no impedance mismatch between Classical ML, DL, and GenAI workflows. Same pattern, same UI, same audit log.
- (+) **Same DAG code, two environments** — Composer runs the same Python that local Airflow does. No "production-only" surprises.
- (+) **Industry-standard observability** — Airflow UI, structured logs, task duration, retry counts. Senior-architect signal.
- (+) **Idempotency by design** — see [ADR-0014](./0014-local-dataset-cache-and-idempotent-loads.md). Re-clicking "Run download" on an already-loaded dataset short-circuits in <1 s.
- (+) **GCP-native cloud story** — Cloud Composer 2/3 + Vertex AI training/serving + BigQuery feature lake (see [ADR-0013](./0013-vertex-ai-centric-ml-platform-on-gcp.md)).
- (+) **Multi-tenant ready** — DAGs accept `tenant_id` as a runtime conf parameter; one DAG instance per tenant per refresh.
- (−) **Operational weight** — Airflow stack is heavy locally (postgres + redis + scheduler + worker + webserver, ~3 GB image footprint). Mitigated by per-tool docker-compose pattern (ADR-0008) — Airflow stays commented-out in `docker-all-up.sh` STACKS until you're working on Initial Downloads or training.
- (−) **Cloud Composer is not free** — Composer 2 small node ~$0.05/hr (~$36/mo), no scale-to-zero. Mitigation: enable Composer only when actively demoing/training; M5+ for portfolio.
- (−) **Status-update plumbing** — Airflow → Postgres status sync requires Airflow callbacks posting to api-gateway. We pick callbacks (low latency) with polling as fallback.
