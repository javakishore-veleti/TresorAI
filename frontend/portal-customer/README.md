# portal-customer

> **TrésorAI customer portal** — the SPA used by SMB end-users (CFO, controller, treasurer).

## Stack
- Angular 17+ (standalone components, signals)
- TypeScript 5.x
- Tailwind or Angular Material (TBD at scaffold)
- Apache ECharts or Chart.js for forecast viz
- WebSocket client for `/ws/stream`

## Local
- Port: **4200**
- Build: `npm` + Angular CLI
- Dockerfile: multi-stage (build → nginx)

## Deploy
- Target: **Google Cloud Run**
- Workflow: `.github/workflows/portal-customer.yml` (path-filtered)

## Routes (planned)
- `/stream` — live transaction feed (Kafka → WebSocket)
- `/forecast` — 30/60/90 cash-flow forecast with confidence bands
- `/agent` — agent reasoning trace + CFO ask
- `/flagged` — review flagged transactions (Hold / Release / Edit / Cancel)

## Status
Not scaffolded yet — see plan `T03a` in `TresorAI_Portfolio_Build_Plan.xlsx`.
