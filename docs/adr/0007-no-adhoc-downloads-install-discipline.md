# ADR-0007: No ad-hoc downloads — professional install discipline

- Status: Accepted
- Date: 2026-04-25

## Context
TrésorAI is intended to be installed at multiple client locations. Most "fintech AI portfolio" projects rely on a developer manually running curl / wget / Jupyter notebooks to seed reference data (supplier lists, IBAN typosquat lookup, sanctions lists, demo data). That is not how enterprise software is installed, and it is not how this project will be installed either.

## Decision
**No manual or ad-hoc downloads anywhere in this codebase.** Every install-time data load is:

1. **Parameterized** — same script / UI flow works at any client, just different inputs.
2. **Idempotent** — re-running it does not duplicate or corrupt data.
3. **Run from one of two places** — the admin portal (`Administration → Data Management → Initial Downloads`, with one accordion per dataset) or its CLI counterpart in `scripts/`.
4. **Audited** — every run logs what was fetched, when, and from where.

## Consequences
- (+) Every client install is reproducible byte-for-byte.
- (+) Ops can hand off the install to a non-engineer with the admin portal as the only required tool.
- (+) Forces a real "what data does this product depend on at install time?" inventory — which becomes a doc artifact.
- (−) More upfront UX work than a `seed.py` script.
- (−) Initial Downloads UI must be on the M0/M1 critical path even though no end-user sees it.
