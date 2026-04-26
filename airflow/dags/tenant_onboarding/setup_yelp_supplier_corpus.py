"""setup_yelp_supplier_corpus — Yelp business corpus (~10 GB) -> public.suppliers_yelp.

Embedding fine-tune corpus for the supplier-similarity model. Optional dataset.
"""
from shared.idempotent_dag import build_initial_download_dag

dag = build_initial_download_dag(
    dag_id="setup_yelp_supplier_corpus",
    dataset_key="yelp_supplier",
    description="Yelp Open Dataset business records — supplier embedding fine-tune corpus",
    schedule=None,
    tags=["tenant-onboarding", "supplier-corpus", "embedding-training", "tresorai"],
)
