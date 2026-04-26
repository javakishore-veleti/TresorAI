"""dag_ofac_sdn_refresh — OFAC SDN + EU consolidated sanctions -> public.sanctions.

Daily refresh. Loaded into the rule-layer of the anomaly scorer.
"""
from shared.idempotent_dag import build_initial_download_dag

dag = build_initial_download_dag(
    dag_id="dag_ofac_sdn_refresh",
    dataset_key="ofac_sanctions",
    description="OFAC SDN + EU consolidated sanctions lists — daily refresh",
    schedule="0 2 * * *",                      # 02:00 UTC daily
    tags=["supplier-intelligence", "sanctions", "compliance", "tresorai"],
)
