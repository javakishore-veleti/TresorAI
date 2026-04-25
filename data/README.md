# data

> **Synthetic and reference data** for local development, tests, and the demo path.

## Files (planned)
- `transactions.csv` — 5000 rows, 90 days, 200 suppliers, 12 planted fraud patterns
- `suppliers.json` — supplier reference list (legit-supplier corpus for embedding matches)
- `fraud-patterns.md` — catalog of planted patterns: duplicate invoices, IBAN typosquats, off-hours payroll, round-amount ACME-style scams

## Loading
The `ingest-service` reads `transactions.csv` and replays it onto Kafka topic `tx.events`. The admin portal's **Initial Downloads** UI handles seeding `suppliers.json` and reference data into Postgres + pgvector at install time — there is no manual / ad-hoc loading.

## Status
Not generated yet — see plan `T10` in `TresorAI_Portfolio_Build_Plan.xlsx`.
