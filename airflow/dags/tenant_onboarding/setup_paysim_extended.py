"""setup_paysim_extended — PaySim labelled fraud (~5 GB) -> public.tx_paysim.

Real-shape labelled fraud for XGBoost / Isolation Forest baselines. One-shot at install.
"""
from shared.idempotent_dag import build_initial_download_dag

dag = build_initial_download_dag(
    dag_id="setup_paysim_extended",
    dataset_key="paysim_extended",
    description="PaySim extended labelled fraud dataset for fraud-detection model training",
    schedule=None,
    tags=["tenant-onboarding", "fraud-training-data", "tresorai"],
)
