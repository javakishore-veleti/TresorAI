# api-gateway

> **BFF (Backend-for-Frontend) + WebSocket fan-out** for both portals.

## Stack
- Java 21
- Spring Boot 3
- spring-boot-starter-webflux
- spring-kafka (consumer of `tx.events`)

## Local
- Port: **8080**
- Build: Maven
- Health: `GET /actuator/health`

## Deploy
- Target: **Google Cloud Run**
- Workflow: `.github/workflows/api-gateway.yml`

## Responsibilities
- Aggregate calls from `portal-customer` and `portal-admin` to backend services
- Consume Kafka `tx.events` → fan out to WebSocket subscribers via `Sinks.Many`
- Expose `/transactions`, `/agent/ask`, `/agent/explain`, `/forecast`, `/ws/stream`
- Audit log of agent decisions to Postgres
- Enforce role-based access for admin-only routes

## Status
Not scaffolded yet — see plan `T04` in `TresorAI_Portfolio_Build_Plan.xlsx`.
