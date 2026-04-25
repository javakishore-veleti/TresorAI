# ADR-0004: Gemini 2.0 Flash for the agent loop

- Status: Accepted
- Date: 2026-04-25

## Context
The intelligence-service runs an LLM-as-judge loop: score → retrieve evidence via tool calls → emit a structured decision + reasoning trace. It must be fast enough that the live demo never feels staged (sub-second perceived latency) and cheap enough to leave running on a portfolio.

## Decision
Gemini 2.0 Flash via google-generativeai. `text-embedding-004` for embeddings. Tool use enabled (`get_supplier_history`, `get_cash_position`, `get_similar_past_tx`). Reasoning trace is captured server-side and rendered live in the customer portal.

## Consequences
- (+) Sub-second responses are achievable; suits a real-time UX.
- (+) Generous free tier — pennies/day for portfolio use.
- (+) Single SDK for completions + embeddings.
- (−) Gemini-specific tool-use schema; switching providers later is a non-trivial refactor.
- (−) Vertex AI quota is regional — consider this when picking the Cloud Run region.
