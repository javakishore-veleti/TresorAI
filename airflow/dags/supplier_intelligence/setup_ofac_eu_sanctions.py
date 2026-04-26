"""setup_ofac_eu_sanctions — OFAC SDN + EU consolidated sanctions -> public.sanctions.

Daily refresh. Loaded into the rule-layer of the anomaly scorer.
"""
from shared.idempotent_dag import build_initial_download_dag

dag = build_initial_download_dag(
    dag_id="setup_ofac_eu_sanctions",
    dataset_key="ofac_sanctions",
    description="OFAC SDN + EU consolidated sanctions lists — daily refresh",
    schedule=None,
    tags=["supplier-intelligence", "sanctions", "compliance", "tresorai"],
)
