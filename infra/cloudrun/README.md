# infra/cloudrun

Per-module Cloud Run deploy manifests + helper scripts (M2 scope).

## Layout (planned)

```
infra/cloudrun/
├── portal-customer.yaml
├── portal-admin.yaml
├── api-gateway.yaml
├── ingest-service.yaml
└── intelligence-service.yaml
```

Each manifest declares the Cloud Run service for its module: image (from Artifact Registry), env vars (from Secret Manager refs), CPU/memory, concurrency, scale-to-zero settings.

## Status
Not started — see plan `T26` in `TresorAI_Portfolio_Build_Plan.xlsx`.
