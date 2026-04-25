# ADR-0005: Cloud Run over Kubernetes

- Status: Accepted
- Date: 2026-04-25

## Context
TrésorAI is a 5-service polyglot monorepo. We need a deploy target that supports independent service lifecycles, scale-to-zero (so a portfolio project does not cost real money), per-revision rollback, and a low operational tax for a solo maintainer.

## Decision
Google Cloud Run, one service per module. Images pushed to Artifact Registry. Per-module GitHub Actions workflows handle build + deploy with a `paths:` filter.

## Consequences
- (+) Scale-to-zero — idle cost is effectively zero.
- (+) Per-revision traffic split + one-line rollback (`gcloud run services update-traffic ...`).
- (+) No Kubernetes operational surface area (no nodes, no upgrades, no etcd).
- (−) Long-running stateful workloads (Kafka, Postgres) cannot live on Cloud Run — those move to managed services (Confluent Cloud, Cloud SQL or Supabase).
- (−) Cold-start latency on first request after idle. Acceptable for a portfolio demo; would warrant min-instances=1 in production.
