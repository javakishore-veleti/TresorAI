# intelligence-service

> **The AI brain** — agent loop, embedding store, anomaly scorer, cash-flow forecast. Other services call it via REST; it never sits in the streaming hot path.

## Stack
- Python 3.12
- FastAPI
- Pydantic v2
- **uv** (dep manager)
- **Gemini 2.0 Flash** via google-generativeai SDK (agent loop, LLM-as-judge with tool use)
- **text-embedding-004** (Google embeddings) — primary
- **sentence-transformers** — fallback embeddings
- **pgvector** client (similarity search over historical suppliers)
- **Prophet** (cash-flow forecast)
- **XGBoost** (M5 — replaces rule-based fraud scorer)
- **OpenTelemetry** (distributed tracing)

## Local
- Port: **8090**
- Build: `uv` + Docker
- Health: `GET /health`

## Deploy
- Target: **Google Cloud Run**
- Workflow: `.github/workflows/intelligence-service.yml`

## Endpoints (planned)
- `POST /score` → `{score, signals[], explanation}` — rule-based + embedding anomaly scorer
- `POST /agent/judge` → `{decision, reasoning_trace[], citations[]}` — Gemini agent with tools (`get_supplier_history`, `get_cash_position`, `get_similar_past_tx`)
- `POST /agent/act` → drafted action (Hold / Release / Alert) — never executes; human-in-the-loop
- `POST /forecast` → `{points[], lower[], upper[]}` — 30/60/90 day cash-flow forecast with confidence band

## Status
Not scaffolded yet — see plan `T06` in `TresorAI_Portfolio_Build_Plan.xlsx`.
