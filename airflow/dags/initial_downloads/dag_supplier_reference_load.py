"""TrésorAI · dag_supplier_reference_load.

First example DAG implementing the standard idempotent pattern from ADR-0014:

    [check_local_files] -> [decide_download] (branch)
                              |
                              +-- found    -> [register_run_already_present] -> [end]
                              +-- missing  -> [download_via_storage_adapter] ->
                                              [verify_checksums] ->
                                              [register_run] -> [end]

Today this is a stub that walks the state machine without actually fetching anything.
Real implementation will call tresorai.data.cli + the GCS/S3/Azure adapter (ADR-0015)
and POST status updates to the admin-api callback endpoint.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule

DATASET_KEY = "tx_synthetic_v1"
ADMIN_API_URL = os.environ.get("TAI_ADMIN_API_URL", "http://host.docker.internal:8091")


def check_local_files(**_ctx) -> dict:
    """Stub: would call tresorai.data.manifest.verify_dataset(DATASET_KEY)."""
    return {"status": "MISSING", "skip_download": False, "dataset_key": DATASET_KEY}


def decide_download(ti, **_ctx) -> str:
    check = ti.xcom_pull(task_ids="check_local_files") or {}
    return "register_run_already_present" if check.get("skip_download") else "download_via_storage_adapter"


def download_via_storage_adapter(**_ctx) -> dict:
    """Stub: would call the configured storage adapter (gcs/s3/azure)."""
    return {"status": "DOWNLOADED", "bytes": 0, "files": 0}


def verify_checksums(ti, **_ctx) -> dict:
    payload = ti.xcom_pull(task_ids="download_via_storage_adapter") or {}
    return {**payload, "status": "VERIFIED"}


def register_run(ti, **_ctx) -> dict:
    payload = ti.xcom_pull(task_ids="verify_checksums") or {}
    # TODO: POST to ADMIN_API_URL + /internal/airflow/dag-run-callback
    return {"status": "SUCCESS", "dataset_key": DATASET_KEY, "payload": payload}


default_args = {
    "owner": "tresorai",
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}


with DAG(
    dag_id="dag_supplier_reference_load",
    description="Per-tenant supplier corpus -> pgvector embedding store",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["initial-downloads", "tenant-data", "tresorai"],
) as dag:
    t_check = PythonOperator(
        task_id="check_local_files",
        python_callable=check_local_files,
    )

    t_branch = BranchPythonOperator(
        task_id="decide_download",
        python_callable=decide_download,
    )

    t_download = PythonOperator(
        task_id="download_via_storage_adapter",
        python_callable=download_via_storage_adapter,
    )

    t_verify = PythonOperator(
        task_id="verify_checksums",
        python_callable=verify_checksums,
    )

    t_register = PythonOperator(
        task_id="register_run",
        python_callable=register_run,
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
