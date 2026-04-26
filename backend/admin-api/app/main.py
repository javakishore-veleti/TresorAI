"""TrésorAI · admin-api — dedicated FastAPI service for portal-admin operations.

Owns:
  - Initial Downloads catalog + run history (Postgres-backed; ADR-0014)
  - Airflow DAG triggers via REST API (ADR-0012)
  - Airflow callback receivers (status sync back into Postgres)

Today this is in-memory + a simulated DAG runner so the admin portal renders a
real running -> success transition. Real Airflow REST + Postgres lands next.
"""

from __future__ import annotations

import asyncio
import os
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.system_health import SystemHealth, gather_system_health

app = FastAPI(
    title="TrésorAI · admin-api",
    version="0.0.1",
    description="Dedicated admin operations service. Backs the portal-admin Initial Downloads page and pending-setup banner.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:4201",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:4201",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    last_run_id: str | None = None
    last_run_progress: int | None = None  # 0-100, only when running


class RunRecord(BaseModel):
    id: str
    dataset_key: str
    airflow_dag_id: str
    status: str
    started_at: str
    finished_at: str | None
    duration_ms: int | None
    forced: bool
    triggered_by: str | None
    rows_loaded: int | None
    error_message: str | None


class TriggerRunRequest(BaseModel):
    force: bool = False
    triggered_by: str | None = None


class TriggerRunResponse(BaseModel):
    dataset_key: str
    run_id: str
    airflow_dag_id: str
    status: str = "queued"


_CATALOG: dict[str, DatasetCatalogEntry] = {
    e.key: e
    for e in [
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
}

_RUNS: dict[str, list[RunRecord]] = {key: [] for key in _CATALOG}
_LOCK = asyncio.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _simulate_run(dataset_key: str, run_id: str, forced: bool) -> None:
    entry = _CATALOG[dataset_key]
    runs = _RUNS[dataset_key]
    started = _now_iso()
    started_perf = time.perf_counter()

    gb = max(0.05, entry.approx_size_bytes / 1024**3)
    duration_s = min(12.0, 1.0 + gb)
    steps = 20
    step_s = duration_s / steps

    record = RunRecord(
        id=run_id, dataset_key=dataset_key, airflow_dag_id=entry.airflow_dag_id,
        status="running", started_at=started, finished_at=None, duration_ms=None,
        forced=forced, triggered_by=None, rows_loaded=None, error_message=None,
    )
    runs.append(record)

    async with _LOCK:
        entry.current_status = "running"
        entry.last_run_id = run_id
        entry.last_run_progress = 0
        entry.last_run_at = started

    for i in range(1, steps + 1):
        await asyncio.sleep(step_s)
        async with _LOCK:
            entry.last_run_progress = int(100 * i / steps)

    finished_perf = time.perf_counter()
    duration_ms = int((finished_perf - started_perf) * 1000)
    rows = int(gb * 1_000_000) if gb > 0.5 else random.randint(50, 5_000)

    async with _LOCK:
        entry.current_status = "success"
        entry.last_run_progress = 100
        entry.rows_loaded = rows
        if entry.first_loaded_at is None:
            entry.first_loaded_at = started
        entry.last_run_at = _now_iso()

    record.status = "success"
    record.finished_at = _now_iso()
    record.duration_ms = duration_ms
    record.rows_loaded = rows


@app.get("/api/admin/initial-downloads/datasets", response_model=list[DatasetCatalogEntry])
def list_datasets() -> list[DatasetCatalogEntry]:
    return list(_CATALOG.values())


@app.get("/api/admin/initial-downloads/{dataset_key}", response_model=DatasetCatalogEntry)
def get_dataset(dataset_key: str) -> DatasetCatalogEntry:
    entry = _CATALOG.get(dataset_key)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Unknown dataset_key: {dataset_key}")
    return entry


@app.get("/api/admin/initial-downloads/{dataset_key}/runs", response_model=list[RunRecord])
def list_runs(dataset_key: str) -> list[RunRecord]:
    if dataset_key not in _RUNS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset_key: {dataset_key}")
    return list(reversed(_RUNS[dataset_key]))[:20]


@app.post("/api/admin/initial-downloads/{dataset_key}/run", response_model=TriggerRunResponse)
async def trigger_run(
    dataset_key: str,
    body: TriggerRunRequest,
    background: BackgroundTasks,
) -> TriggerRunResponse:
    entry = _CATALOG.get(dataset_key)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Unknown dataset_key: {dataset_key}")

    if entry.current_status == "running":
        raise HTTPException(status_code=409, detail="Run already in progress for this dataset")

    if entry.current_status in {"success", "already_present"} and not body.force:
        run_id = str(uuid.uuid4())
        record = RunRecord(
            id=run_id, dataset_key=dataset_key, airflow_dag_id=entry.airflow_dag_id,
            status="already_present", started_at=_now_iso(), finished_at=_now_iso(),
            duration_ms=80, forced=False, triggered_by=body.triggered_by,
            rows_loaded=entry.rows_loaded, error_message=None,
        )
        _RUNS[dataset_key].append(record)
        async with _LOCK:
            entry.last_run_at = record.started_at
            entry.current_status = "already_present"
        return TriggerRunResponse(
            dataset_key=dataset_key, run_id=run_id,
            airflow_dag_id=entry.airflow_dag_id, status="already_present",
        )

    run_id = str(uuid.uuid4())
    background.add_task(_simulate_run, dataset_key, run_id, body.force)

    return TriggerRunResponse(
        dataset_key=dataset_key, run_id=run_id,
        airflow_dag_id=entry.airflow_dag_id, status="queued",
    )


@app.post("/internal/airflow/dag-run-callback")
def airflow_callback(payload: dict[str, Any]) -> dict[str, str]:
    return {"received": "ok"}


@app.get("/api/admin/system/health", response_model=SystemHealth)
async def system_health() -> SystemHealth:
    """Server-side probe of every backend dependency. Powers Administration -> System Health.

    Cloud-aware via TAI_ENV (local | gcp | aws | azure | hybrid). Per-service URL
    overrides via TAI_SVC_<name> env vars.
    """
    return await gather_system_health()


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "admin-api", "docs": "/docs", "health": "/health"}
