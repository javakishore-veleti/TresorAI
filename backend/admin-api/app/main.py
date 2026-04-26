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
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.airflow_client import AIRFLOW_BASE, AirflowError, get_dag_run, trigger_dag
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


@app.on_event("startup")
async def _unpause_setup_dags_on_boot() -> None:
    """Best-effort unpause of every setup_* DAG in the catalog.

    Existing Airflow installs may have these DAGs paused from before
    DAGS_ARE_PAUSED_AT_CREATION flipped to false. Running this at admin-api
    startup keeps the catalog DAGs ready-to-trigger for the user without
    requiring a manual UI unpause for each one.
    """
    from app.airflow_client import unpause_dag

    for entry in _CATALOG.values():
        try:
            await unpause_dag(entry.airflow_dag_id)
        except Exception:
            pass  # truly best-effort; unpause failures don't block trigger flow


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
    # Storage locations — resolved per ADR-0014 + ADR-0015 from env vars
    local_path: str | None = None      # $HOME/runtime_data/tresorai/datasets/<key>/
    source_provider: str | None = None # gcs | s3 | azure
    source_uri: str | None = None      # gs://... or s3://... or https://....blob...


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
            airflow_dag_id="setup_demo_seed", target_table="public.transactions",
            current_status="never_loaded", rows_loaded=None,
            first_loaded_at=None, last_run_at=None,
        ),
        DatasetCatalogEntry(
            key="ofac_sanctions", title="OFAC + EU consolidated sanctions",
            subtitle="Daily-refreshed sanctions lists for the rule layer",
            required=True, approx_size_bytes=20_971_520,
            airflow_dag_id="setup_ofac_eu_sanctions", target_table="public.sanctions",
            current_status="never_loaded", rows_loaded=None,
            first_loaded_at=None, last_run_at=None,
        ),
        DatasetCatalogEntry(
            key="iban_typosquat", title="IBAN typosquat lookup",
            subtitle="Curated IBAN lookalike patterns + supplier domains",
            required=True, approx_size_bytes=524_288,
            airflow_dag_id="setup_iban_typosquat", target_table="public.iban_typosquat",
            current_status="never_loaded", rows_loaded=None,
            first_loaded_at=None, last_run_at=None,
        ),
        DatasetCatalogEntry(
            key="paysim_extended", title="PaySim extended fraud dataset (~5 GB)",
            subtitle="Real-shape labelled fraud for XGBoost / Isolation Forest",
            required=True, approx_size_bytes=5_368_709_120,
            airflow_dag_id="setup_paysim_extended", target_table="public.tx_paysim",
            current_status="never_loaded", rows_loaded=None,
            first_loaded_at=None, last_run_at=None,
        ),
        DatasetCatalogEntry(
            key="yelp_supplier", title="Yelp supplier corpus (~10 GB)",
            subtitle="Embedding fine-tune corpus for Deep Learning track",
            required=False, approx_size_bytes=10_737_418_240,
            airflow_dag_id="setup_yelp_supplier_corpus", target_table="public.suppliers_yelp",
            current_status="never_loaded", rows_loaded=None,
            first_loaded_at=None, last_run_at=None,
        ),
        DatasetCatalogEntry(
            key="iso_country_codes", title="ISO 3166 country codes",
            subtitle="Yearly-refresh reference data",
            required=True, approx_size_bytes=10_240,
            airflow_dag_id="setup_iso_country_codes", target_table="public.country_codes",
            current_status="never_loaded", rows_loaded=None,
            first_loaded_at=None, last_run_at=None,
        ),
        DatasetCatalogEntry(
            key="eval_set_curated", title="Agent quality eval set",
            subtitle="Hand-curated (tx, expected_decision, citations) cases",
            required=True, approx_size_bytes=204_800,
            airflow_dag_id="setup_agent_eval", target_table="public.agent_eval_cases",
            current_status="never_loaded", rows_loaded=None,
            first_loaded_at=None, last_run_at=None,
        ),
    ]
}

_RUNS: dict[str, list[RunRecord]] = {key: [] for key in _CATALOG}
_LOCK = asyncio.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Map Airflow's dagRun states to our 7-state catalog status (ADR-0014).
_AIRFLOW_TO_STATUS = {
    "queued":  "running",
    "running": "running",
    "success": "success",
    "failed":  "failed",
}


async def _poll_airflow_run(dataset_key: str, dag_id: str, run_id: str, record: RunRecord) -> None:
    """Poll Airflow until the dagRun reaches a terminal state, mirror state into the catalog.

    Updates entry.current_status, entry.last_run_progress, entry.last_run_at, and
    appends/finalizes the RunRecord. Bounded loop — stops after 5 minutes regardless.
    """
    entry = _CATALOG[dataset_key]
    started_perf = time.perf_counter()

    progress_step = 5  # cosmetic — real progress isn't surfaced by Airflow REST
    for tick in range(100):                # max ~5 min at 3 s per tick
        await asyncio.sleep(3.0)
        try:
            run = await get_dag_run(dag_id, run_id)
        except AirflowError:
            continue                       # transient — keep polling

        af_state = (run.get("state") or "queued").lower()
        catalog_state = _AIRFLOW_TO_STATUS.get(af_state, "running")

        async with _LOCK:
            entry.current_status = catalog_state
            if catalog_state == "running":
                entry.last_run_progress = min(95, 5 + tick * progress_step)

        if af_state in ("success", "failed"):
            duration_ms = int((time.perf_counter() - started_perf) * 1000)

            async with _LOCK:
                entry.last_run_progress = 100
                entry.last_run_at = _now_iso()
                if af_state == "success":
                    entry.rows_loaded = entry.rows_loaded or 0
                    if entry.first_loaded_at is None:
                        entry.first_loaded_at = record.started_at
                else:
                    entry.last_error = run.get("note") or "DAG run failed"  # type: ignore[attr-defined]

            record.status = af_state
            record.finished_at = _now_iso()
            record.duration_ms = duration_ms
            return

    # Timed out — mark failed so the UI clears the spinner
    async with _LOCK:
        entry.current_status = "failed"
        entry.last_run_progress = 100
        entry.last_run_at = _now_iso()
    record.status = "failed"
    record.finished_at = _now_iso()
    record.error_message = "Timed out waiting for Airflow dagRun"


def _resolve_storage_paths(dataset_key: str) -> dict[str, str | None]:
    """Compute local cache + cloud source URI from env (ADR-0014 + ADR-0015)."""
    home = os.path.expanduser("~")
    cache_root = os.environ.get(
        "TAI_DATASETS_ROOT",
        os.path.join(home, "runtime_data", "tresorai", "datasets"),
    )
    local_path = os.path.join(cache_root, dataset_key) + "/"

    provider = os.environ.get("TAI_STORAGE_PROVIDER", "gcs").lower()
    bucket = os.environ.get("TAI_STORAGE_BUCKET", "tresorai-datasets")
    prefix = os.environ.get("TAI_STORAGE_PREFIX", "datasets/")
    if not prefix.endswith("/"):
        prefix += "/"

    if provider == "gcs":
        source_uri = f"gs://{bucket}/{prefix}{dataset_key}/"
    elif provider == "s3":
        source_uri = f"s3://{bucket}/{prefix}{dataset_key}/"
    elif provider == "azure":
        account = os.environ.get("TAI_AZURE_ACCOUNT", "tresorai")
        container = os.environ.get("TAI_AZURE_CONTAINER", "datasets")
        source_uri = f"https://{account}.blob.core.windows.net/{container}/{prefix}{dataset_key}/"
    else:
        source_uri = None

    return {"local_path": local_path, "source_provider": provider, "source_uri": source_uri}


def _enrich(entry: DatasetCatalogEntry) -> DatasetCatalogEntry:
    paths = _resolve_storage_paths(entry.key)
    return entry.model_copy(update=paths)


@app.get("/api/admin/initial-downloads/datasets", response_model=list[DatasetCatalogEntry])
def list_datasets() -> list[DatasetCatalogEntry]:
    return [_enrich(e) for e in _CATALOG.values()]


@app.get("/api/admin/initial-downloads/{dataset_key}", response_model=DatasetCatalogEntry)
def get_dataset(dataset_key: str) -> DatasetCatalogEntry:
    entry = _CATALOG.get(dataset_key)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Unknown dataset_key: {dataset_key}")
    return _enrich(entry)


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

    # Real Airflow trigger. Run ID format follows Airflow's convention so the
    # webserver UI deep-link works: /dags/<dag_id>/grid?dag_run_id=<run_id>
    run_id = f"manual__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}__{uuid.uuid4().hex[:8]}"

    try:
        await trigger_dag(
            dag_id=entry.airflow_dag_id,
            run_id=run_id,
            conf={
                "dataset_key": dataset_key,
                "force": body.force,
                "triggered_by": body.triggered_by or "admin-portal",
            },
        )
    except AirflowError as e:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Cannot trigger Airflow DAG '{entry.airflow_dag_id}': {e}. "
                f"Confirm Airflow is running (System Health → Orchestration)."
            ),
        )

    record = RunRecord(
        id=run_id, dataset_key=dataset_key, airflow_dag_id=entry.airflow_dag_id,
        status="queued", started_at=_now_iso(), finished_at=None, duration_ms=None,
        forced=body.force, triggered_by=body.triggered_by, rows_loaded=None,
        error_message=None,
    )
    _RUNS[dataset_key].append(record)

    async with _LOCK:
        entry.current_status = "running"
        entry.last_run_id = run_id
        entry.last_run_progress = 5
        entry.last_run_at = record.started_at

    background.add_task(_poll_airflow_run, dataset_key, entry.airflow_dag_id, run_id, record)

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
