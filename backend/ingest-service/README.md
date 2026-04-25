# ingest-service

> **Streaming spine producer** — synthetic bank-feed driver that publishes transactions to Kafka.

## Stack
- Java 21
- Spring Boot 3
- spring-kafka (producer)

## Local
- Port: **8081**
- Build: Maven
- Health: `GET /actuator/health`

## Deploy
- Target: **Google Cloud Run**
- Workflow: `.github/workflows/ingest-service.yml`

## Responsibilities
- Read `data/transactions.csv` (5000 rows, 90 days, 200 suppliers, 12 planted fraud patterns)
- Produce JSON to Kafka topic `tx.events` at configurable rate (5–20 tx/sec)
- Schema validation against AsyncAPI contract before publish
- Bridge for future real open-banking sandbox (Bridge / Plaid) — see T43

## Status
Not scaffolded yet — see plan `T05` in `TresorAI_Portfolio_Build_Plan.xlsx`.
