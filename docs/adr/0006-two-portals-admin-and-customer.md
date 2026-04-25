# ADR-0006: Two portals — admin and customer

- Status: Accepted
- Date: 2026-04-25

## Context
The original plan listed a single Angular SPA (`portal-web`). In practice TrésorAI has two distinct user populations: **SMB end-users** (CFO / controller / treasurer — the daily UX of the product) and **TrésorAI ops + enterprise client admins** (who install, configure, and operate the product at multiple client locations). Their navigation, authorization, and visual density needs are different enough that one app would either bloat the customer experience with admin-only nav or hide admin features behind feature flags.

## Decision
Split into two SPAs, deployed as two independent Cloud Run services:

- **`frontend/portal-customer`** — SMB user UX. Live tx stream, agent reasoning trace, cash-flow forecast, flagged-tx review. Port 4200 locally.
- **`frontend/portal-admin`** — ops + enterprise install UX. Three-level navigation: top-nav → left-nav → content area. Authorized to `role=ADMIN` only. Port 4201 locally.

`api-gateway` enforces role-based access for admin routes; both portals share the same backend.

## Consequences
- (+) Each SPA stays focused; bundle size and IA stay tight per audience.
- (+) Independent deploys — admin features can roll out without forcing a customer-portal redeploy.
- (+) Authorization story is structural, not just runtime.
- (−) Two Angular apps to maintain — design system must be shared (component library) to avoid drift.
- (−) Two Cloud Run services + two CI workflows.
