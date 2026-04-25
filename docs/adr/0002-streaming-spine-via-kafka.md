# ADR-0002: Streaming spine via Kafka

- Status: Accepted
- Date: 2026-04-25

## Context
TrésorAI ingests transactions, scores them in near-real-time, and fans them out to the customer portal as they happen. We need a backbone with low latency, durable retention, and a fan-out model that does not couple producers to consumers.

## Decision
Kafka topic `tx.events` is the spine. `ingest-service` produces; `api-gateway` consumes-and-fans-out via WebSocket; `intelligence-service` consumes for asynchronous scoring. Local dev uses Apache Kafka 3.9 (KRaft mode, no Zookeeper) via `infra/local/kafka/docker-compose.yaml`. Cloud uses Confluent Cloud Free or Redpanda Cloud.

## Consequences
- (+) Producers and consumers evolve independently.
- (+) Replay is free — re-running the demo is `kafka-console-consumer --from-beginning`.
- (+) Backpressure is the broker's problem, not the app's.
- (−) Adds a stateful dependency to local dev. Mitigated by the per-tool compose layout — kafka can be brought up in isolation.
- (−) Schema discipline must be enforced via AsyncAPI contract; otherwise consumers break silently.
