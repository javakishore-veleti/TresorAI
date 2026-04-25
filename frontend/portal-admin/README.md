# portal-admin

> **TrésorAI admin portal** — the SPA used by TrésorAI ops / platform engineers and by enterprise client admins during install + ongoing operation.

## Stack
- Angular 17+ (standalone components, signals)
- TypeScript 5.x
- Tailwind or Angular Material (TBD at scaffold)

## Local
- Port: **4201**
- Build: `npm` + Angular CLI
- Dockerfile: multi-stage (build → nginx)

## Deploy
- Target: **Google Cloud Run** (separate service from `portal-customer`)
- Workflow: `.github/workflows/portal-admin.yml` (path-filtered)

## Information Architecture

Three-level navigation: **top nav → left nav → content area**.

```
┌─ Top nav ─────────────────────────────────────────────┐
│  Administration  │  Tenants  │  Models  │  System     │
└──┬────────────────────────────────────────────────────┘
   ▼
┌──── Left nav ────┐  ┌─── Content area ──────────────┐
│  Data Management │  │                               │
│  ├─ Initial      │  │  (page-specific, e.g.         │
│  │   Downloads ◀─┼──┼─  accordions, dashboards)     │
│  ├─ ...          │  │                               │
│  └─ ...          │  │                               │
│  Users & Roles   │  │                               │
│  Agent Config    │  │                               │
│  ...             │  │                               │
└──────────────────┘  └───────────────────────────────┘
```

### Top nav (planned)
- **Administration** — install + ops machinery (Data Management, Users & Roles, Agent Config, …)
- **Tenants** — multi-tenant customer management
- **Models** — model performance dashboards (false-positive rate, latency, decision audit)
- **System** — health, OpenTelemetry traces, Cloud Run service status, feature flags

### Administration → Data Management → Initial Downloads
Right-pane: **multiple accordions**, one per dataset/reference-data source the client install needs (e.g. supplier reference list, IBAN typosquat lookup, country/sanctions lists, demo seed data). Each accordion configures and triggers its own download/seed step.

> **No manual or ad-hoc downloads anywhere in this codebase.** Every install operation is parameterized, idempotent, and run from this UI (or its CLI counterpart) so a single TrésorAI install can be reproduced verbatim at any client site.

## Authorization
- Restricted to `role=ADMIN` accounts via `api-gateway` IAM
- Customer-portal users cannot reach these routes

## Status
Not scaffolded yet — see plan `T03b` in `TresorAI_Portfolio_Build_Plan.xlsx`.
