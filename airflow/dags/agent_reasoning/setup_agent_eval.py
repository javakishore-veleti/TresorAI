"""setup_agent_eval — agent quality eval cases -> public.agent_eval_cases.

Curated (transaction, expected_decision, expected_citations) cases used to
score the Gemini agent loop. Replayed on every prompt change.
"""
from shared.idempotent_dag import build_initial_download_dag

dag = build_initial_download_dag(
    dag_id="setup_agent_eval",
    dataset_key="eval_set_curated",
    description="Hand-curated agent quality eval cases — load + run scoring",
    schedule=None,                              # triggered on prompt change / release
    tags=["agent-reasoning", "eval", "tresorai"],
)
