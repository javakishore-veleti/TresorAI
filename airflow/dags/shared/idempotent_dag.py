"""Factory that builds an idempotent dataset-load DAG (ADR-0014 pattern).

One factory, many DAG files — each Initial Downloads dataset is a 10-line file
that calls this. Same skeleton:

    [check_local_files] -> [decide_download] (branch)
                              |
                              +-- found    -> [register_run_already_present] -> [end]
                              +-- missing  -> [download_via_storage_adapter] ->
                                              [verify_checksums] ->
                                              [register_run] -> [end]

Today the task callables are stubs that walk the state machine without doing real
network work. They will be replaced with calls into tresorai.data.* + the
storage adapter (ADR-0015), and the register_run step will POST to admin-api's
/internal/airflow/dag-run-callback once that's wired (ADR-0012).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Sequence

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule

ADMIN_API_URL = os.environ.get("TAI_ADMIN_API_URL", "http://host.docker.internal:8091")

DEFAULT_ARGS = {
    "owner": "tresorai",
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}


# ---- Task-callable factories — close over dataset_key so each DAG carries its own ----

def _make_check_local_files(dataset_key: str):
    def _fn(**_ctx) -> dict:
        # TODO: from tresorai.data.manifest import verify_dataset
        # ok, reason = verify_dataset(dataset_key, deep=False)
        # return {"status": "ALREADY_PRESENT" if ok else "MISSING",
        #         "skip_download": ok, "dataset_key": dataset_key}
        return {"status": "MISSING", "skip_download": False, "dataset_key": dataset_key}
    _fn.__name__ = f"check_local_files__{dataset_key}"
    return _fn


def _decide_download(ti, **_ctx) -> str:
    check = ti.xcom_pull(task_ids="check_local_files") or {}
    return "register_run_already_present" if check.get("skip_download") else "download_via_storage_adapter"


def _make_download(dataset_key: str):
    def _fn(**_ctx) -> dict:
        # TODO: pick adapter via TAI_STORAGE_PROVIDER (gcs/s3/azure) and stream files
        return {"status": "DOWNLOADED", "dataset_key": dataset_key, "bytes": 0, "files": 0}
    _fn.__name__ = f"download__{dataset_key}"
    return _fn


def _verify_checksums(ti, **_ctx) -> dict:
    payload = ti.xcom_pull(task_ids="download_via_storage_adapter") or {}
    return {**payload, "status": "VERIFIED"}


def _make_register_run(dataset_key: str):
    def _fn(ti, **_ctx) -> dict:
        payload = ti.xcom_pull(task_ids="verify_checksums") or {}
        # TODO: httpx.post(f"{ADMIN_API_URL}/internal/airflow/dag-run-callback", json=...)
        return {"status": "SUCCESS", "dataset_key": dataset_key, "payload": payload}
    _fn.__name__ = f"register_run__{dataset_key}"
    return _fn


# ---- Public factory ----

def build_initial_download_dag(
    *,
    dag_id: str,
    dataset_key: str,
    description: str,
    schedule: str | None = None,
    tags: Sequence[str] | None = None,
    start_date: datetime = datetime(2026, 1, 1),
) -> DAG:
    """Construct the standard idempotent download DAG. Returns the DAG so the
    caller can assign it to a top-level variable in the DAG file (Airflow picks
    up any DAG object discovered at module level)."""
    tags = list(tags) if tags else ["initial-downloads", "tresorai"]

    with DAG(
        dag_id=dag_id,
        description=description,
        default_args=DEFAULT_ARGS,
        start_date=start_date,
        schedule=schedule,
        catchup=False,
        tags=tags,
    ) as dag:
        t_check = PythonOperator(
            task_id="check_local_files",
            python_callable=_make_check_local_files(dataset_key),
        )

        t_branch = BranchPythonOperator(
            task_id="decide_download",
            python_callable=_decide_download,
        )

        t_download = PythonOperator(
            task_id="download_via_storage_adapter",
            python_callable=_make_download(dataset_key),
        )

        t_verify = PythonOperator(
            task_id="verify_checksums",
            python_callable=_verify_checksums,
        )

        t_register = PythonOperator(
            task_id="register_run",
            python_callable=_make_register_run(dataset_key),
        )

        t_register_already_present = EmptyOperator(
            task_id="register_run_already_present",
        )

        t_end = EmptyOperator(
            task_id="end",
            trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        )

        t_check >> t_branch
        t_branch >> t_download >> t_verify >> t_register >> t_end
        t_branch >> t_register_already_present >> t_end

    return dag
