"""dag_iban_typosquat_load — curated IBAN typosquat lookup -> public.iban_typosquat.

Curated lookalike-domain + IBAN-typosquat patterns. Refreshed quarterly.
"""
from shared.idempotent_dag import build_initial_download_dag

dag = build_initial_download_dag(
    dag_id="dag_iban_typosquat_load",
    dataset_key="iban_typosquat",
    description="Curated IBAN typosquat patterns + supplier lookalike domains",
    schedule=None,                              # on demand / quarterly
    tags=["supplier-intelligence", "fraud-signals", "tresorai"],
)
