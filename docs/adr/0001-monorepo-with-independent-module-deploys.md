# ADR-0001: Monorepo with independent module deploys

- Status: Accepted
- Date: 2026-04-25

## Context
TrésorAI has 5 deployable units (portal-customer, portal-admin, api-gateway, ingest-service, intelligence-service) plus shared contracts and infra. The product is small enough that a polyrepo would create artificial friction (cross-repo PRs for contract changes, fragmented CI), but we still need each module to deploy independently — touching one service should not redeploy the others.

## Decision
Single Git repository (`javakishore-veleti/TresorAI`). Each module owns its own Dockerfile, build tool (npm / Maven / uv), and CI workflow under `.github/workflows/<module>.yml` with `paths:` filter. One Cloud Run service per module.

## Consequences
- (+) Atomic contract + consumer changes in one PR.
- (+) Per-module CI runs only when the module changes — fast feedback, low CI minutes.
- (+) Single PR review surface, single issue tracker.
- (−) Repo-root tooling (root `package.json`, lint config) needs care to not become a chokepoint for module-local conventions.
- (−) Newcomers must read this ADR to understand the intent — the repo layout alone could be mistaken for a coupled mono-app.
