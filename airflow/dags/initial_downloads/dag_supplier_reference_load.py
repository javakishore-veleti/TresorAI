"""TrésorAI · dag_supplier_reference_load.

First example DAG implementing the standard idempotent pattern from ADR-0014:

    [check_local_files] -> branch -> [download] -> [verify_checksums] -> [register_run]
                                  |
                                  +--> [register_run_already_present]

Today this is a stub that walks the state machine without actually fetching anything.
Real implementation will call tresorai.data.cli + the GCS/S3/Azure adapter (ADR-0015)
and POST status updates to the admin-api callback endpoint.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator

DATASET_KEY = "tx_synthetic_v1"  # standalone test target — replace per DAG
ADMIN_API_URL = os.environ.get("TAI_ADMIN_API_URL", "http://host.docker.internal:8091")

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

    @task
    def check_local_files() -> dict:
        """Stub: would call tresorai.data.manifest.verify_dataset(DATASET_KEY)."""
        # TODO: import tresorai.data.manifest and call verify_dataset
        return {"status": "MISSING", "skip_download": False, "dataset_key": DATASET_KEY}

    def decide_download(ti) -> str:
        check = ti.xcom_pull(task_ids="check_local_files")
        return "register_run_already_present" if check.get("skip_download") else "download_via_storage_adapter"

    branch = BranchPythonOperator(
        task_id="decide_download",
        python_callable=decide_download,
    )

    @task
    def download_via_storage_adapter() -> dict:
        """Stub: would call the configured storage adapter (gcs/s3/azure)."""
        return {"status": "DOWNLOADED", "bytes": 0, "files": 0}

    @task
    def verify_checksums(payload: dict) -> dict:
        return {**payload, "status": "VERIFIED"}

    @task
    def register_run(payload: dict) -> dict:
        # TODO: POST to ADMIN_API_URL + /internal/airflow/dag-run-callback
        return {"status": "SUCCESS", "dataset_key": DATASET_KEY, "payload": payload}

    register_run_already_present = EmptyOperator(
        task_id="register_run_already_present",
    )

    end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")

    check = check_local_files()
    check >> branch
    branch >> download_via_storage_adapter() >> verify_checksums(download_via_storage_adapter.output) >> register_run(verify_checksums.output) >> end
    branch >> register_run_already_present >> end
