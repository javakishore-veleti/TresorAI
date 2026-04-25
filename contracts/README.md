# contracts

> **Single source of truth** for all module-to-module interfaces.

## Format
- **OpenAPI 3.1** — REST contracts (`api-gateway`, `intelligence-service`)
- **AsyncAPI 2.6** — event contracts (Kafka topic `tx.events`, WebSocket `/ws/stream`)

## Files (planned)
- `api-gateway.openapi.yaml`
- `intelligence-service.openapi.yaml`
- `ingest.asyncapi.yaml`

## Tooling
- `redoc-cli` — render docs as HTML
- `openapi-generator` — generate TypeScript clients (Angular portals) and Java clients (api-gateway → intelligence-service)

## Rule
Breaking contract changes must be PR-visible — generated clients are checked in, so a contract diff that breaks consumers shows up in the same PR.

## Status
Not started — see plan `T02` in `TresorAI_Portfolio_Build_Plan.xlsx`.
