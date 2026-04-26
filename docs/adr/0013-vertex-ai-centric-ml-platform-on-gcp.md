# ADR-0013: Vertex-AI-centric ML platform in GCP

- Status: Accepted
- Date: 2026-04-25

## Context
The cloud deployment must support all three AI/ML tracks (Classical ML, Deep Learning, Generative AI — see [ADR-0012](./0012-airflow-for-initial-downloads.md)) with first-class managed services for training, registry, serving, evals, feature store, and observability. The two realistic alternatives were (a) build on raw GKE + open-source stack (Kubeflow, MLflow, KServe) versus (b) lean on Vertex AI as the integrated managed platform.

## Decision
**Vertex-AI-centric** for the GCP deployment. Cloud Composer (Airflow) DAGs invoke Vertex AI APIs for everything ML-shaped. Open-source equivalents are kept locally (MLflow, JupyterLab, etc.) so DAG code is portable; production calls hit Vertex.

| Concern | GCP service |
|---|---|
| Orchestration | **Cloud Composer 2 / 3** *(managed Airflow)* |
| Classical ML training | **Vertex AI Training** with custom containers (XGBoost, LightGBM, sklearn, Isolation Forest) |
| Deep Learning training | **Vertex AI Training** with GPU/TPU; **Vertex AI Pipelines (KFP)** for end-to-end DL pipelines |
| Online prediction | **Vertex AI Endpoints** with per-tenant traffic split |
| Batch prediction | **Vertex AI Batch Prediction** |
| Feature store | **Vertex AI Feature Store** (online + offline) |
| Model registry | **Vertex AI Model Registry** |
| Generative AI | **Vertex AI Generative AI / Gemini API** |
| GenAI evals | **Vertex AI Evaluation Service** + custom LLM-as-judge DAGs |
| Experiment tracking | **Vertex AI Experiments** *(MLflow stays for the cross-track view)* |
| Streaming | **Pub/Sub + Dataflow** *(or Confluent Cloud Kafka if we keep API surface)* |
| Data lake / warehouse | **BigQuery + Cloud Storage** |
| Container registry | **Artifact Registry** |
| Compute (services) | **Cloud Run** *(per ADR-0005)* |
| Identity | **Workload Identity Federation** *(no JSON service-account keys)* |
| Secrets | **Secret Manager** |
| Observability | **Cloud Trace + Cloud Logging + Cloud Monitoring** |

## Consequences

- (+) **One coherent ML platform** — model lifecycle, lineage, registry, serving all integrated with IAM, audit logs, and billing.
- (+) **Less glue code** — skip building Kubeflow + KServe + MLflow + Feast from scratch.
- (+) **Senior-architect signal** — clear delineation of which managed service owns which lifecycle stage.
- (+) **Per-tenant traffic split is built-in** — Vertex AI Endpoints support traffic-percent splits without our code.
- (−) **GCP lock-in** for the production deployment. Mitigated by storage abstraction (ADR-0015) and Airflow as the portable control plane — DAG code carries no Vertex-specific schema; only the operator implementations do.
- (−) **Composer is not free** — small Composer 2 node ~$36/mo idle, no scale-to-zero. Acceptable for portfolio + active demo periods.
- (−) **Vertex AI Feature Store online tier costs scale with read QPS** — for portfolio demo we use offline-only; online tier enabled only when going to design-partner production.
