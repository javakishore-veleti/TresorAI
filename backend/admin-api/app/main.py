"""TrésorAI · admin-api — dedicated FastAPI service for portal-admin operations.

Owns:
  - Initial Downloads catalog + run history (Postgres-backed; ADR-0014)
  - Airflow DAG triggers via REST API (ADR-0012)
  - Airflow callback receivers (status sync back into Postgres)
  - (Future) tenant management, model-registry reads, system health roll-up

Why a dedicated service (not folded into api-gateway):
  - Talks to Airflow REST API + Vertex AI Model Registry — surfaces api-gateway
    should never reach.
  - Different IAM boundary: admin-api is for ops/superusers only; api-gateway is
    customer-facing.
  - Different deploy cadence; admin features can lag customer features safely.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="TrésorAI · admin-api",
    version="0.0.1",
    description="Dedicated admin operations service. Backs the portal-admin Initial Downloads page and pending-setup banner.",
)


# --------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    db_url_set: bool
    airflow_url_set: bool


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="admin-api",
        version=app.version,
        db_url_set=bool(os.environ.get("DATABASE_URL")),
        airflow_url_set=bool(os.environ.get("AIRFLOW_API_URL")),
    )


# --------------------------------------------------------------------------
# Initial Downloads — catalog + runs
# --------------------------------------------------------------------------
class DatasetCatalogEntry(BaseModel):
    key: str
    title: str
    subtitle: str | None
    required: bool
    approx_size_bytes: int
    airflow_dag_id: str
    target_table: str | None
    current_status: str
    rows_loaded: int | None
    first_loaded_at: str | None
    last_run_at: str | None


# Stub catalog — replaced with Postgres SELECT once SQLAlchemy session is wired.
# Mirrors data/sql/0001_initial_downloads.sql seed inserts.
_STUB_CATALOG: list[DatasetCatalogEntry] = [
    DatasetCatalogEntry(
        key="tx_synthetic_v1", title="Synthetic transactions (~5 GB)",
        subtitle="Demo replay stream + classical-ML training corpus",
        required=True, approx_size_bytes=5_368_709_120,
        airflow_dag_id="dag_demo_seed_load", target_table="public.transactions",
        current_status="never_loaded", rows_loaded=None,
        first_loaded_at=None, last_run_at=None,
    ),
    DatasetCatalogEntry(
        key="ofac_sanctions", title="OFAC + EU consolidated sanctions",
        subtitle="Daily-refreshed sanctions lists for the rule layer",
        required=True, approx_size_bytes=20_971_520,
        airflow_dag_id="dag_ofac_sdn_refresh", target_table="public.sanctions",
        current_status="never_loaded", rows_loaded=None,
        first_loaded_at=None, last_run_at=None,
    ),
    DatasetCatalogEntry(
        key="iban_typosquat", title="IBAN typosquat lookup",
        subtitle="Curated IBAN lookalike patterns + supplier domains",
        required=True, approx_size_bytes=524_288,
        airflow_dag_id="dag_iban_typosquat_load", target_table="public.iban_typosquat",
        current_status="never_loaded", rows_loaded=None,
        first_loaded_at=None, last_run_at=None,
    ),
    DatasetCatalogEntry(
        key="paysim_extended", title="PaySim extended fraud dataset (~5 GB)",
        subtitle="Real-shape labelled fraud for XGBoost / Isolation Forest",
        required=True, approx_size_bytes=5_368_709_120,
        airflow_dag_id="dag_paysim_extended_load", target_table="public.tx_paysim",
        current_status="never_loaded", rows_loaded=None,
        first_loaded_at=None, last_run_at=None,
    ),
    DatasetCatalogEntry(
        key="yelp_supplier", title="Yelp supplier corpus (~10 GB)",
        subtitle="Embedding fine-tune corpus for Deep Learning track",
        required=False, approx_size_bytes=10_737_418_240,
        airflow_dag_id="dag_yelp_supplier_corpus_load", target_table="public.suppliers_yelp",
        current_status="never_loaded", rows_loaded=None,
        first_loaded_at=None, last_run_at=None,
    ),
    DatasetCatalogEntry(
        key="iso_country_codes", title="ISO 3166 country codes",
        subtitle="Yearly-refresh reference data",
        required=True, approx_size_bytes=10_240,
        airflow_dag_id="dag_iso_country_codes_load", target_table="public.country_codes",
        current_status="never_loaded", rows_loaded=None,
        first_loaded_at=None, last_run_at=None,
    ),
    DatasetCatalogEntry(
        key="eval_set_curated", title="Agent quality eval set",
        subtitle="Hand-curated (tx, expected_decision, citations) cases",
        required=True, approx_size_bytes=204_800,
        airflow_dag_id="dag_agent_eval_suite", target_table="public.agent_eval_cases",
        current_status="never_loaded", rows_loaded=None,
        first_loaded_at=None, last_run_at=None,
    ),
]


@app.get("/api/admin/initial-downloads/datasets", response_model=list[DatasetCatalogEntry])
def list_datasets() -> list[DatasetCatalogEntry]:
    """Return the full catalog with current status. Stub today; reads Postgres tomorrow."""
    return _STUB_CATALOG


class TriggerRunRequest(BaseModel):
    force: bool = False
    triggered_by: str | None = None


class TriggerRunResponse(BaseModel):
    dataset_key: str
    run_id: str
    airflow_dag_id: str
    status: str = "queued"


@app.post("/api/admin/initial-downloads/{dataset_key}/run", response_model=TriggerRunResponse)
def trigger_run(dataset_key: str, body: TriggerRunRequest) -> TriggerRunResponse:
    """Trigger an Airflow DAG run for the given dataset. Stub today.

    Real impl will:
      1. INSERT into initial_downloads_runs (status='queued', forced=body.force, ...)
      2. POST /api/v1/dags/<dag_id>/dagRuns to AIRFLOW_API_URL with conf={force, run_id}
      3. Return the run_id; Airflow callbacks update status as the DAG progresses
    """
    entry = next((d for d in _STUB_CATALOG if d.key == dataset_key), None)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Unknown dataset_key: {dataset_key}")
    return TriggerRunResponse(
        dataset_key=dataset_key,
        run_id="stub-run-id",
        airflow_dag_id=entry.airflow_dag_id,
    )


@app.post("/internal/airflow/dag-run-callback")
def airflow_callback(payload: dict[str, Any]) -> dict[str, str]:
    """Airflow on_success / on_failure callback target. Stub today.

    Real impl will UPDATE initial_downloads_runs.status + initial_downloads_datasets.current_status
    based on the payload from the Airflow callback.
    """
    return {"received": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "admin-api", "docs": "/docs", "health": "/health"}
