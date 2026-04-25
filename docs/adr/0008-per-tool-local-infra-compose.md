# ADR-0008: Per-tool local infra (one compose per tool)

- Status: Accepted
- Date: 2026-04-25

## Context
Local dev needs Postgres + Redis + Kafka today, plus optional Qdrant / MLflow / others later. A single mega-`docker-compose.yml` is the obvious default, but it couples the lifecycle of every dependency together — bring up "everything" or "nothing" — and bumping a single image version drags in a global review of an unrelated config block.

## Decision
One `docker-compose.yaml` per tool under `infra/local/<tool>/`. A trio of orchestration scripts (`docker-all-up.sh`, `docker-all-down.sh`, `docker-all-status.sh`) iterate over an explicit `STACKS` array. Optional tools live in the directory tree but are commented out of the orchestrator until needed.

## Consequences
- (+) Independent lifecycle — start postgres without booting kafka while iterating on the AI service.
- (+) Independent versioning — bump one image without touching another tool's compose.
- (+) Mental model matches the project's per-module CI/CD philosophy.
- (+) Adding a new dependency is purely additive: drop in a new dir + add one line to the orchestrator.
- (−) Slightly more files than a single mega-compose. Mitigated by one consistent layout per tool.
- (−) Cross-stack networking (e.g. mlflow needing postgres) requires explicit network coordination if added later.
