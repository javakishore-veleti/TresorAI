"""setup_iso_country_codes — ISO 3166 country codes -> public.country_codes.

Reference data. Yearly refresh.
"""
from shared.idempotent_dag import build_initial_download_dag

dag = build_initial_download_dag(
    dag_id="setup_iso_country_codes",
    dataset_key="iso_country_codes",
    description="ISO 3166 country codes — yearly refresh reference data",
    schedule="0 4 1 1 *",                       # 04:00 UTC, Jan 1 each year
    tags=["supplier-intelligence", "reference-data", "tresorai"],
)
