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

## Visual direction (ADR-0010)
- **No black, no gray** anywhere. Warm palette only.
- Primary: emerald (`#047857`); accent: champagne gold (`#D4A574`).
- Backgrounds are warm pearl / cream — never `#FFFFFF` flat or gray.
- First-class alert / toast / status-pill primitives (`<tai-alert>`, `<tai-toast>`, `<tai-status-pill>`).
- Custom favicon pack (16/32/180/192/512) — emerald-and-gold "T" mark.
- Hero imagery: recolored vector illustrations (undraw.co) matched to the palette. No stock photos.
- Tooling: Tailwind CSS with shared `tailwind.config.cjs`; Angular CDK for headless primitives; **no** default Material theme.

## Status
Not scaffolded yet — see plan `T03` in `TresorAI_Portfolio_Build_Plan.xlsx`.
