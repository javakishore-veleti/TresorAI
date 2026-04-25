# ADR-0003: pgvector over a standalone vector DB

- Status: Accepted
- Date: 2026-04-25

## Context
The agent loop performs similarity search against historical supplier data to detect duplicate-invoice and IBAN-typosquat fraud. Options considered: pgvector (Postgres extension), Qdrant, Milvus, Weaviate, Chroma.

## Decision
pgvector. Embeddings live in the same Postgres instance as transactional state. Standalone vector DBs (Qdrant in particular) remain available as commented-out compose stacks under `infra/local/qdrant/` for experimentation but are not part of the deployed runtime.

## Consequences
- (+) One database, one set of credentials, one backup story, one connection pool.
- (+) Joins between transactional rows (suppliers, transactions) and vector neighbors are SQL — no cross-system coordination.
- (+) Cloud SQL Postgres or Supabase satisfies both needs on free tier.
- (−) Index types and query language are less rich than dedicated vector DBs (no payload filtering at the speed of Qdrant). Mitigated by the modest scale of the use case.
- (−) ANN tuning in pgvector requires more care than turnkey vector DBs.
