"""Thin async client for the Airflow 2.x REST API.

We use a tiny subset:
  - PATCH /api/v1/dags/{dag_id}             (unpause if paused)
  - POST  /api/v1/dags/{dag_id}/dagRuns     (trigger a run)
  - GET   /api/v1/dags/{dag_id}/dagRuns/{run_id}  (poll status)

Auth is HTTP Basic; defaults match the local docker-compose user (admin/admin).
"""

from __future__ import annotations

import os
from typing import Any

import httpx

AIRFLOW_BASE = os.environ.get("AIRFLOW_API_URL", "http://localhost:8088/api/v1")
AIRFLOW_AUTH = (
    os.environ.get("AIRFLOW_USERNAME", "admin"),
    os.environ.get("AIRFLOW_PASSWORD", "admin"),
)


class AirflowError(RuntimeError):
    """Raised when the Airflow REST API is unreachable or returns an error."""


async def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(auth=AIRFLOW_AUTH, timeout=10.0)


async def unpause_dag(dag_id: str) -> None:
    """Unpause a DAG (best-effort — failures don't block the trigger)."""
    try:
        async with await _client() as c:
            await c.patch(
                f"{AIRFLOW_BASE}/dags/{dag_id}",
                json={"is_paused": False},
                params={"update_mask": "is_paused"},
            )
    except Exception:
        # Non-fatal — POST /dagRuns can still trigger a paused DAG manually.
        pass


async def trigger_dag(dag_id: str, run_id: str, conf: dict[str, Any] | None = None) -> dict:
    """Kick off a DAG run. Returns Airflow's dagRun JSON."""
    await unpause_dag(dag_id)
    payload: dict[str, Any] = {"dag_run_id": run_id}
    if conf:
        payload["conf"] = conf
    try:
        async with await _client() as c:
            r = await c.post(f"{AIRFLOW_BASE}/dags/{dag_id}/dagRuns", json=payload)
            if r.status_code >= 400:
                raise AirflowError(f"Airflow {r.status_code}: {r.text[:200]}")
            return r.json()
    except httpx.ConnectError as e:
        raise AirflowError(f"Cannot reach Airflow at {AIRFLOW_BASE}: {e}") from e
    except httpx.TimeoutException as e:
        raise AirflowError(f"Airflow timed out at {AIRFLOW_BASE}") from e


async def get_dag_run(dag_id: str, run_id: str) -> dict:
    """Fetch the current state of a running dagRun."""
    async with await _client() as c:
        r = await c.get(f"{AIRFLOW_BASE}/dags/{dag_id}/dagRuns/{run_id}")
        if r.status_code >= 400:
            raise AirflowError(f"Airflow {r.status_code}: {r.text[:200]}")
        return r.json()
