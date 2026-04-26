"""setup_demo_seed — synthetic transactions (~5 GB) -> public.transactions.

Demo replay stream + Classical-ML training corpus. Runs once at tenant install.
"""
from shared.idempotent_dag import build_initial_download_dag

dag = build_initial_download_dag(
    dag_id="setup_demo_seed",
    dataset_key="tx_synthetic_v1",
    description="Synthetic 5-GB transaction dataset for demo replay + classical-ML training",
    schedule=None,
    tags=["tenant-onboarding", "demo-data", "tresorai"],
)
