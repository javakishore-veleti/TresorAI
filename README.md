# TrésorAI

> **Stop AP fraud before it ships, and know your cash 90 days out.**
> An agentic treasury & payments copilot for small and mid-sized businesses.

[![License: MIT](https://img.shields.io/github/license/javakishore-veleti/TresorAI?style=flat-square)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/javakishore-veleti/TresorAI?style=flat-square)](https://github.com/javakishore-veleti/TresorAI/commits)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)](#)
[![Domain](https://img.shields.io/badge/Domain-FinTech%20%C2%B7%20B2B-2ea44f?style=flat-square)](#)

---

## Table of contents

1. [Context](#1-context)
2. [Key stakeholders & customers](#2-key-stakeholders--customers)
3. [Data](#3-data)
4. [Business domain](#4-business-domain)
5. [Business capabilities](#5-business-capabilities)
6. [Business services](#6-business-services)
7. [Where AI / ML is critical](#7-where-ai--ml-is-critical)
8. [How customers interact](#8-how-customers-interact)
9. [How the business improves continuously](#9-how-the-business-improves-continuously)
10. [Two portals](#10-two-portals)
11. [Architecture views](#11-architecture-views)
    - 11.1 [Enterprise architecture](#111-enterprise-architecture)
    - 11.2 [Solution architecture](#112-solution-architecture)
    - 11.3 [Product architecture](#113-product-architecture)
    - 11.4 [AI architecture](#114-ai-architecture)
    - 11.5 [MLOps](#115-mlops)
    - 11.6 [AIOps](#116-aiops)
    - 11.7 [Observability](#117-observability)
12. [Modules](#12-modules)
13. [Quickstart](#13-quickstart)
14. [Design](#14-design)
15. [Roadmap](#15-roadmap)
16. [Tech stack (collapsible)](#16-tech-stack)

---

## 1. Context

### Definitions

> **SMB** *(Small and Medium-sized Business)* — common operating definition: **10–250 employees, $1M–$50M annual revenue**. Synonyms: SME (Small and Medium Enterprise, the EU/OECD term), mid-market when on the upper end. SMBs are too big for shoebox accounting, too small to afford enterprise treasury platforms. This is the **missing middle** of fintech — and the segment TrésorAI is built for.
>
> **Business domain** — TrésorAI sits at the intersection of three classical financial sub-domains:
>
> | Sub-domain | What it means |
> |---|---|
> | **Treasury management** | Cash position, 30/60/90-day forecasting, payment-timing decisions, working-capital optimization |
> | **Payment fraud / AP risk** | Catching fraudulent, duplicate, or misdirected outbound payments **before** they ship — typosquatted IBANs, off-hours payroll runs, look-alike suppliers |
> | **Supplier intelligence** *(KYV — Know Your Vendor)* | Embedding-based similarity over a tenant's own supplier history; vendor onboarding hygiene; counterparty risk |

### Who deploys TrésorAI *(the financial institutions that have these use cases)*

TrésorAI is **B2B2C** — it ships under a channel partner's brand to the partner's SMB customers. The partners that have this use case:

| Channel partner | Examples | Why they care |
|---|---|---|
| **Commercial / business-banking arms of banks** | Regional and community banks; business-banking divisions of national banks (Wells Fargo Business Banking, Chase for Business, BMO Harris, BNP Paribas SME, Santander SME) | Differentiate their SMB depository product; reduce fraud losses they bear under Reg E / payment-services-directive liability |
| **SMB-focused neobanks / fintech-banks** | Mercury, Brex, Ramp, Relay, Bluevine, Novo, Tide, Wise Business, Qonto, Revolut Business | Their entire positioning is "modern finance for SMBs" — an agentic AP-fraud + cash-flow copilot is a natural extension |
| **AP automation & accounting ISVs** | Bill.com, Tipalti, Stampli, AvidXchange, Bottomline, Sage Intacct, QuickBooks Enterprise, Xero, NetSuite (SMB tier) | They already own the AP workflow; they need an AI layer that adds judgment, not just OCR |
| **Embedded-finance platforms** | Treasury Prime, Synctera, Unit, Solid, Modern Treasury | They white-label TrésorAI for non-bank distribution partners (vertical SaaS, marketplaces) |
| **Open-banking / data-aggregator partners** *(integration, not channel)* | Plaid, Bridge, TrueLayer, Tink, Belvo, Yapily, Salt Edge | They are the data-feed source `ingest-service` consumes; not a sales channel |
| **Payment processors with B2B AP focus** | Stripe Business, Adyen for Platforms, GoCardless | Adjacent — typically integration partners more than distribution partners |

The product is multi-tenant from day one (§3, §11.1) so a single TrésorAI install can serve hundreds of SMB tenants under a single channel partner's brand.

### The recurring losses we eliminate

A 30-person SMB pays 800 invoices a month. Payroll on the 15th. Rent on the 1st. A handful of new suppliers every quarter. Today, the CFO catches AP fraud only when the bank statement arrives — too late. Cash forecasts live in a spreadsheet that's updated weekly, by hand, and is wrong by Wednesday.

**Two recurring losses:**

1. **Fraudulent or duplicate invoices that slip through** — typosquatted IBANs, off-hours payroll runs, suppliers that look real but aren't. Industry data: SMBs lose roughly 5% of revenue to occupational fraud annually; AP fraud is the single largest category.
2. **Late surprises in cash position** — a missed receivable, a misjudged payment timing, an unexpected vendor obligation. The CFO learns about it after it costs them.

Existing tools force a choice: enterprise-grade fraud platforms priced for banks, or a spreadsheet. TrésorAI is the missing middle — agentic AI for the SMB CFO, B2B install discipline for the channel partner who deploys it.

## 2. Key stakeholders & customers

**End-users (customer side — `portal-customer`):**

| Role | What they want |
|---|---|
| **CFO** *(primary)* | Catch fraud before it costs us. Know cash position with confidence bands, not gut feel. |
| **Controller** | Review flagged transactions efficiently. Maintain a clean supplier list. Audit-ready trail. |
| **Treasurer / Payments Ops** | Time payments to cash availability. Handle vendor disputes with citations from history. |

**Operators (TrésorAI side — `portal-admin`):**

| Role | What they own |
|---|---|
| **Customer Success Lead** | Onboard a new client: run Initial Downloads, configure agent thresholds, validate the first 24 hours of decisions. |
| **Platform Engineer** | Operate the install at multiple client locations. Reproduce environments. Watch service health and model performance. |
| **Product Manager** | Track agent decision quality (false-positive / negative rate), feature adoption, customer NPS on explanation quality. |

**External:**

| Role | Touchpoint |
|---|---|
| **Channel partner** *(bank platform, accounting ISV)* | Embeds TrésorAI; integrates via the contract APIs in `contracts/`. |
| **Regulator / external auditor** | Read-only audit-log export for periodic review. |
| **Design-partner SMBs** *(M5)* | Quarterly feedback loop driving roadmap. |

## 3. Data

| Data | Source | Persistence | Consumed by |
|---|---|---|---|
| **Bank transactions** *(real or sandbox feed)* | `ingest-service` from open-banking sandbox (Bridge / Plaid) or synthetic CSV | Kafka topic `tx.events` (durable) → Postgres for query | All downstream services |
| **Supplier reference list** | Loaded at install via Initial Downloads UI; appended as customer adds suppliers | Postgres + pgvector embeddings | `intelligence-service` for similarity matching |
| **Historical agent decisions** | Every Hold / Release / Alert from the customer portal | Postgres (audit log) | Compliance export, retraining data |
| **Cash positions & receivables** | Customer ERP / accounting integration *(M5)* | Postgres | Forecast service (Prophet) |
| **Reference packs** *(IBAN typosquat lookups, sanctions lists, country codes)* | Initial Downloads — parameterized, idempotent, audited | Postgres | Rule layer of the anomaly scorer |
| **Embeddings** *(supplier text, transaction memo)* | `intelligence-service` via `text-embedding-004` | pgvector | Anomaly scorer, agent retrieval tools |

Data principles:
- **Multi-tenant from day one.** Every row carries a `tenant_id`; cross-tenant reads are physically prevented at the gateway layer.
- **Audit by default.** Every agent decision and every install operation is timestamped, hashed, and replayable.
- **No ad-hoc loading.** Reference data only enters the system through the Initial Downloads flow. *(See [ADR-0007](docs/adr/0007-no-adhoc-downloads-install-discipline.md).)*

## 4. Business domain

TrésorAI sits at the intersection of three classical fintech sub-domains:

| Sub-domain | What we do here |
|---|---|
| **Treasury management** | Live cash-position view, 30/60/90-day forecast, payment-timing decisions |
| **Payment fraud / AP risk** | Real-time scoring of every outbound payment, agent-led judgment with citations |
| **Supplier intelligence** | Embedding-based similarity over a tenant's own supplier history — duplicate-invoice and typosquat detection |

Adjacent (not in scope at M0–M3): AR collections, receivables financing, FX risk, regulatory reporting. Designed to integrate with — not compete against — these systems.

## 5. Business capabilities

A capability map (level-1) — independent of which service / team owns it.

| # | Capability | Outcome |
|---|---|---|
| C1 | **Real-time AP fraud detection** | Every outbound payment scored before approval; high-risk surfaced within 200 ms |
| C2 | **Cash position intelligence** | Always-current view of cash, with 30/60/90-day forecast that responds to pending decisions |
| C3 | **Agent-based decision support** | Human-in-the-loop Hold / Release / Alert recommendations with visible reasoning trace |
| C4 | **Audit & compliance** | Every decision logged with evidence; replayable; exportable |
| C5 | **Multi-tenant operations** | Logical isolation, per-tenant configuration, parameterized install |
| C6 | **Reference data management** | Reproducible, idempotent, audited install of every dataset the product depends on |
| C7 | **Integration & channel partnerships** | OpenAPI / AsyncAPI contracts; embedded deployment by banks and accounting ISVs |
| C8 | **Continuous learning** | Decisions feed model improvement loops; design-partner feedback drives roadmap |

## 6. Business services

The externally-visible services — what a customer or partner perceives.

| Service | Surface | Capability supported |
|---|---|---|
| **AP Fraud Catch** | `portal-customer` live tx feed + `/score` API | C1 |
| **Cash-Flow Forecasting** | `portal-customer` forecast view + `/forecast` API | C2 |
| **Agent Reasoning** | `portal-customer` reasoning trace panel + `/agent/explain` API | C3 |
| **Action Drafting** *(Hold / Release / Alert)* | `portal-customer` review modal + `/agent/act` API | C3, C4 |
| **Tenant Onboarding** | `portal-admin` → Tenants + Initial Downloads flow | C5, C6 |
| **Reference Data Sync** | `portal-admin` → Administration → Data Management → Initial Downloads | C6 |
| **Audit & Decision Replay** | `portal-admin` → Models / `portal-customer` → Flagged history; export endpoints | C4 |
| **Channel API** | OpenAPI 3.1 + AsyncAPI 2.6 contracts in `contracts/` | C7 |
| **Model Performance** | `portal-admin` → Models dashboard | C8 |

## 7. Where AI / ML is critical

AI is not a chatbot bolted on — it is the **decision tier** of the product. Three integration points:

| Where | Technique | Why it matters |
|---|---|---|
| **Anomaly scoring** | Rule-based + embedding similarity (`sentence-transformers` fallback, `text-embedding-004` primary) over a tenant's own supplier history in **pgvector** | Catches both obvious patterns (duplicate invoices, off-hours payroll) and subtle ones (IBAN typosquat, look-alike supplier names) |
| **Agent reasoning loop** | **Gemini 2.0 Flash** with tool use — tools: `get_supplier_history`, `get_cash_position`, `get_similar_past_tx` | Sub-second judgment with a *visible* reasoning trace — "agentic UX, not chatbot UX." See [ADR-0004](docs/adr/0004-gemini-flash-for-agent-loop.md). |
| **Cash-flow forecasting** | **Prophet** on transactional history + LLM-derived adjustments for known events (planned payroll, scheduled vendor payments) | Confidence bands the CFO can trust; updates as agent decisions land |
| **Future: fraud model upgrade (M5)** | **XGBoost** on labeled synthetic + open-source fraud datasets, with a model card | Replaces the rule-based portion of the scorer with a learned model |

Why agentic over a single LLM call: the agent **retrieves evidence with each tool call** before forming a recommendation, so explanations cite specific past transactions. Compliance and the CFO both want citations — an LLM that asserts without retrieving is not deployable in finance.

## 8. How customers interact

The customer journey — what a CFO actually does, in order:

1. **Onboarding** *(week 0, run by Customer Success in `portal-admin`)*
   - Initial Downloads — reference packs, fraud-pattern catalogs
   - Tenant created, agent thresholds tuned, first 24h of decisions reviewed in shadow mode
2. **Daily** *(`portal-customer`, 5–10 min)*
   - Glance at live tx feed — green pass, amber pending, coral flagged
   - For each flagged tx: read the agent's reasoning trace, click Hold / Release / Alert
3. **Weekly** *(`portal-customer`, 15 min)*
   - Review the cash-flow forecast; decide on payment timing
   - "Ask the agent" for ad-hoc questions — "what's our exposure to ACME?"
4. **Monthly** *(`portal-customer` + audit export)*
   - Review flagged-transaction history, supplier additions, agent decision quality
   - Export audit log for the auditor
5. **Quarterly** *(channel partner / TrésorAI ops)*
   - Update reference packs (sanctions lists, fraud-pattern packs) via Initial Downloads
   - Review model dashboards; tune thresholds if false-positive rate has drifted

## 9. How the business improves continuously

| Function | Inputs they watch | Tools / surfaces |
|---|---|---|
| **Product managers** | Agent false-positive / false-negative rate; explanation NPS; feature adoption per tenant; tx volume per tenant | `portal-admin` → Models dashboard; product analytics |
| **Business heads / GTM** | Pricing-tier mix; channel-partner pipeline; design-partner conversion; CAC / LTV by segment | CRM; channel partner agreements; design-partner roadmap |
| **Customer Success** | Time-to-first-value (onboarding day → first caught fraud); tenant churn signals; reference-data freshness | `portal-admin` → Tenants + Initial Downloads audit log |
| **Operations / Platform** | Install reproducibility (Initial Downloads success rate); infra cost per tenant; SLA / latency | `portal-admin` → System; OpenTelemetry traces; Cloud Run dashboards |
| **Engineering** | Independent-deploy proven per module; test coverage per module; ADR cadence | GitHub Actions per-module workflows; `docs/adr/`; `TresorAI_Portfolio_Build_Plan.xlsx` |
| **Compliance** | Audit-log completeness; decision replay-ability; reference-data provenance | Audit export endpoints; Initial Downloads audit log |

Closed-loop improvement: every customer decision (Hold / Release / Alert) becomes labeled training data; the M5 XGBoost upgrade is fed by this loop, not by external datasets alone.

---

## 10. Two portals

| Portal | Audience | Headline experiences |
|---|---|---|
| **`portal-customer`** *(:4200)* | CFO, Controller, Treasurer | Live AP feed · Agent reasoning trace · Hold/Release/Alert review · 30/60/90 cash forecast · Ask-the-agent |
| **`portal-admin`** *(:4201)* | TrésorAI ops + enterprise client admins | Top-nav (Administration · Tenants · Models · System) → left-nav → content. Initial Downloads · Tenant Onboarding · Model Dashboards · System Health |

## 11. Architecture views

Seven views — each answers a different question, each is owned by a different stakeholder.

### 11.1 Enterprise architecture

**Question:** *Where does TrésorAI sit in the customer's enterprise stack and the partner ecosystem?*

```
   Channel partner (bank platform / accounting ISV)
                          │  embedded deployment + OIDC SSO
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │            TrésorAI  (per-tenant Cloud Run)          │
   │     ┌──────────────────────────────────────────┐    │
   │     │ portal-customer · portal-admin            │    │
   │     │ api-gateway · ingest · intelligence       │    │
   │     └──────────────────────────────────────────┘    │
   └────┬───────────────┬───────────────┬───────────────┘
        │               │               │
        ▼               ▼               ▼
   Open-banking    Customer ERP    Audit / SOC2 /
   feed (Bridge,   /accounting     compliance
   Plaid, FPS)    (M5 integration) export
```

**EA decisions:**
- **Multi-tenant from day 1** — every row carries `tenant_id`; isolation enforced at the gateway, not the row trigger.
- **Channel-first GTM** — sold via banks and accounting ISVs that embed TrésorAI under their brand, not direct-to-SMB.
- **Identity** — OIDC / SAML federation with the channel partner's IdP; no native user store for customer-side users.
- **Compliance posture** — GDPR + SOC2 readiness from M2; data residency configurable per channel.
- **Integration surface** — OpenAPI 3.1 + AsyncAPI 2.6 contracts versioned in `contracts/`; partners code against contracts, not against services.

### 11.2 Solution architecture

**Question:** *What did we build, how does it run, what are the NFRs?*

```
┌─ portal-customer ─┐    ┌─ portal-admin ─┐
│   Angular 17+     │    │  Angular 17+   │
└────────┬──────────┘    └────────┬───────┘
         │                        │
         └─────────┬──────────────┘
                   │ REST + WebSocket
         ┌─────────▼─────────┐                ┌────────────────┐
         │   api-gateway     │◀──── Kafka ────│ ingest-service │
         │  (Spring Boot,    │   tx.events    │ (Spring Boot,  │
         │  WebFlux + WS)    │                │  bank-feed)    │
         └────────┬──────────┘                └────────────────┘
                  │ REST
                  ▼
         ┌──────────────────────────┐
         │   intelligence-service   │
         │   FastAPI + Gemini 2.0   │
         │   pgvector + Prophet     │
         └──────────────────────────┘
                  │
                  ▼
         Postgres + pgvector · Redis
```

**Non-functional targets:**

| NFR | Target |
|---|---|
| Tx scoring latency *(p95)* | < 200 ms |
| Agent recommendation latency *(p95)* | < 800 ms |
| Availability *(per service)* | 99.9% (Cloud Run scale-to-zero, per-revision rollback) |
| Throughput *(peak per tenant)* | 1 000 tx / sec |
| Recovery time on rollback | < 60 s (`gcloud run services update-traffic`) |
| Audit-log durability | 100% — every decision persisted before response |
| Tenant isolation | physical at gateway, logical at row, never cross-read |

Polyglot is deliberate — Java + Spring Kafka owns the streaming spine; Python + FastAPI owns the AI tier. *(See [ADR-0001](docs/adr/0001-monorepo-with-independent-module-deploys.md), [ADR-0002](docs/adr/0002-streaming-spine-via-kafka.md).)* Full C4-style diagrams: `docs/architecture.md` *(planned, T34)*.

### 11.3 Product architecture

**Question:** *How do business capabilities decompose into services and modules?*

| Capability *(§5)* | Business service *(§6)* | Implementing module |
|---|---|---|
| C1 Real-time AP fraud detection | AP Fraud Catch | `intelligence-service` `/score`, `api-gateway`, `portal-customer` |
| C2 Cash position intelligence | Cash-Flow Forecasting | `intelligence-service` `/forecast`, `portal-customer` |
| C3 Agent decision support | Agent Reasoning + Action Drafting | `intelligence-service` `/agent/judge`, `/agent/act`, `portal-customer` |
| C4 Audit & compliance | Audit & Decision Replay | `api-gateway` audit log → Postgres, both portals |
| C5 Multi-tenant operations | Tenant Onboarding | `portal-admin` Tenants, `api-gateway` IAM |
| C6 Reference data management | Reference Data Sync | `portal-admin` Initial Downloads, `api-gateway` `/admin/initial-downloads`, scripts/ CLI counterpart |
| C7 Integration & partnerships | Channel API | `contracts/` (OpenAPI + AsyncAPI), generated clients |
| C8 Continuous learning | Model Performance | `portal-admin` Models, audit log → training pipeline |

### 11.4 AI architecture

**Question:** *How does the agent actually reason, and why is that reliable enough for finance?*

```
   Tx event ─────────────────────────────────────┐
       │                                         │
       ▼                                         │
   ┌─────────────┐                               │
   │   Scorer    │  rules + embedding similarity │  Streaming
   │  (rules +   │  (pgvector over tenant's own  │  hot path —
   │  embeddings)│   supplier corpus)            │  never blocks
   └──────┬──────┘                               │
          │  {score, signals[]}                  │
          ▼                                      │
   ┌─────────────┐    ┌──────────────────────┐  │
   │   Agent     │◀──▶│ Tool catalog         │  │
   │  Gemini 2.0 │    │  get_supplier_history │  │
   │  Flash      │    │  get_cash_position    │  │
   │  + tool use │    │  get_similar_past_tx  │  │
   └──────┬──────┘    └──────────────────────┘  │
          │                                      │
          ▼                                      │
   {decision,                                    │
    reasoning_trace[],   ─────► UI render ◀──────┘
    citations[]}              (live observability
                               for the user)
```

**Layers:**

| Layer | Component | Tech |
|---|---|---|
| **Retrieval** | Vector + structured lookup | pgvector (primary), `sentence-transformers` fallback, structured Postgres queries |
| **Reasoning** | LLM-as-judge agent loop with tool use | Gemini 2.0 Flash via `google-generativeai` |
| **Decision** | Structured output: action + trace + citations | Pydantic schema enforced server-side |
| **Forecast** | Prophet + LLM-derived event adjustments | Prophet on synthetic + actuals; Gemini for event reasoning |
| **Fallback** | Rule-based if Gemini unavailable; embeddings if Gemini up but tools fail | Hard-coded rule chain in `intelligence-service` |

**Key design choice:** the agent **retrieves evidence with each tool call** before recommending. Citations are baked into the decision schema — the customer sees *which* past transactions, *which* supplier records, *which* cash-position snapshot the agent used. An LLM that asserts without retrieving is not deployable in finance. *(See [ADR-0004](docs/adr/0004-gemini-flash-for-agent-loop.md).)*

### 11.5 MLOps

**Question:** *How do models go from notebook to production to retired?*

| Stage | What happens | Tooling |
|---|---|---|
| **Data** | Customer Hold/Release/Alert decisions become labeled training data; reference packs version-controlled in object storage | Postgres audit log, Initial Downloads audit |
| **Train** | XGBoost fraud model (M5); embedding fine-tuning *(stretch)* | `intelligence-service` training scripts; **MLflow** for experiment tracking *(commented stack today, enabled at M5)*; Vertex AI Training for cloud runs |
| **Version** | Model card + git SHA tag → Artifact Registry; ADR for any model-architecture change | Artifact Registry, `docs/adr/`, model-card template |
| **Deploy** | Shadow mode (model runs but only audit-logged) → canary 10% per tenant → full cutover; per-tenant rollout flags | `intelligence-service` config, feature flags |
| **Monitor** | False-positive / false-negative rate, decision distribution, drift on input features | `portal-admin` Models dashboard |
| **Rollback** | Same channel as forward — flag-driven; no redeploy needed | Feature flags, model registry |
| **Retire** | Model and its artifacts archived with a "retired" model card | Artifact Registry tag, audit log |

The agent loop itself is treated as a model artifact — system prompt + tool schemas + reasoning template are versioned and rolled out the same way.

### 11.6 AIOps

**Question:** *How do we operate AI-bearing services without 3 a.m. surprises?*

| Concern | Mechanism |
|---|---|
| **Latency budgets** | Per-call budgets enforced in `intelligence-service`: scorer ≤150 ms, agent ≤700 ms; budget breach → fallback path |
| **Cost guardrails** | Token spend per tenant tracked and capped; exceeding cap routes to rule-based scorer + alert |
| **Prompt caching** | Stable system prompts and tool schemas cached at the SDK layer; cache hit-rate monitored |
| **Failure modes** | Gemini timeout / quota / 5xx → `sentence-transformers` fallback; tool call fails → agent receives explicit error and recovers; whole service down → rule-based scoring continues |
| **Quality gates** | Daily false-positive / false-negative rate vs threshold; auto-page if drift > 2σ |
| **Decision quality regression** | Replay last 24h decisions through a candidate model before promotion |
| **Cost per decision** | Reported on Models dashboard; trended weekly |
| **Tenant noisy-neighbour** | Per-tenant token budgets; rate limit on `/agent/*` endpoints |

**Incident playbook (excerpt):** "Gemini API down" → 1) confirm via Vertex AI status, 2) feature-flag agent loop to fallback, 3) page customer-comms (banner in `portal-customer`), 4) flagged-tx review goes to enriched-rule-based mode, 5) post-mortem includes whether fallback rate was below the agreed threshold.

### 11.7 Observability

**Question:** *Can you debug a single customer's flagged transaction at 11 p.m. without VPNing into anything?*

| Signal | Implementation | Where it lands |
|---|---|---|
| **Distributed traces** | OpenTelemetry SDK in every service; `traceparent` propagated across REST and Kafka headers | Cloud Trace; one trace per customer transaction across all services |
| **Structured logs** | JSON with `tenant_id`, `request_id`, `tx_id`, `agent_decision_id` on every line | Cloud Logging |
| **Metrics** | RED metrics (rate, errors, duration) per endpoint; per-tenant cardinality | Cloud Monitoring → Models dashboard |
| **Agent reasoning trace** | First-class observability primitive — same JSON the user sees in `portal-customer` is the durable audit + debugging artifact | Postgres `agent_decisions` table |
| **Audit log** | Every Hold/Release/Alert + every Initial Downloads run: hashed, signed, exportable | Postgres + scheduled GCS export |
| **Alerts** | Cloud Monitoring policies for: error rate, latency p95, false-positive drift, token-spend overshoot, Initial Downloads failure | PagerDuty / email *(channel TBD)* |
| **Trace–log correlation** | `request_id` is shared between traces and logs; clicking a span in Cloud Trace deep-links to its logs | Cloud Trace UI |

**Debug path** — a customer says "you held supplier X yesterday and I don't understand why":
1. Find the `agent_decision_id` from the customer's flagged-tx history.
2. One query to Postgres returns the full reasoning_trace + citations.
3. The same `agent_decision_id` is the trace ID — Cloud Trace shows the cross-service span tree.
4. Logs filtered by `agent_decision_id` show the tool-call inputs and outputs.

No VPN. No log diving. The trace IS the explanation.

## 12. Modules

| Module | Path | Stack | Local Port | Deploy |
|---|---|---|---|---|
| `portal-customer` | `frontend/portal-customer` | Angular 17+, TypeScript, Tailwind | 4200 | Cloud Run |
| `portal-admin` | `frontend/portal-admin` | Angular 17+, TypeScript, Tailwind | 4201 | Cloud Run |
| `api-gateway` | `backend/api-gateway` | Java 21, Spring Boot 3, WebFlux + WebSocket | 8080 | Cloud Run |
| `ingest-service` | `backend/ingest-service` | Java 21, Spring Boot 3, Spring Kafka producer | 8081 | Cloud Run |
| `intelligence-service` | `backend/intelligence-service` | Python 3.12, FastAPI, Gemini 2.0 Flash, pgvector, Prophet | 8090 | Cloud Run |
| `contracts` | `contracts/` | OpenAPI 3.1 + AsyncAPI 2.6 | n/a | n/a |
| `infra` | `infra/` | docker-compose (per tool), gcloud manifests | n/a | GCP |

## 13. Quickstart

```bash
# 1. Conda env at $HOME/runtime_data/python_venvs/TresorAI (Python 3.12)
npm run setup:conda:create

# 2. Activate (must be sourced)
source ./scripts/conda-activate.sh

# 3. Local infra (postgres+pgvector, redis, kafka)
npm run infra:up
npm run infra:status

# 4. Generate brand favicons (committed; rebuild only if you change the SVG)
npm run generate:favicons

# 5. Once intelligence-service is scaffolded
npm run setup:python:deps

# Or run the full sequence
npm run setup:initial:all

# Tear down
npm run infra:down
source ./scripts/conda-deactivate.sh
```

## 14. Design

Visual direction is locked in [ADR-0010](docs/adr/0010-visual-design-direction.md): **no pure black, no pure gray** anywhere. Warm "treasure" palette — emerald + champagne gold + pearl/cream surfaces. First-class alert / toast / status-pill primitives. Custom favicon mark (emerald rounded square, pearl "T", gold gem; admin variant adds a mauve badge).

Design tokens live in `tailwind.config.cjs` (Tailwind, single source of truth) and `design-system/tokens.css` (CSS-variables form). Brand-mark SVGs and the generated favicon pack live under `design-system/`.

## 15. Roadmap

| Milestone | Goal | Target |
|---|---|---|
| **M0 — Foundation** | Repo skeleton, CI/CD, GCP project, contracts v0.1, design system, local hello-world per module | Week 1 |
| **M1 — Local MVP** | Live tx stream → anomaly + agent → reasoning trace UI → cash forecast on docker-compose. Initial Downloads admin UI live. | Weeks 2–3 |
| **M2 — Cloud deploy** | All 5 services on Cloud Run with proven independent build & deploy | Week 4 |
| **M3 — Polish + demo** | Visual polish, deterministic demo, 90-sec Loom, hero imagery, final README | Week 5 |
| **M4 — Launch** | LinkedIn launch, optional blog, Show HN | Week 6 |
| **M5 — Iterate** | Real open-banking sandbox, design-partner SMBs, XGBoost fraud model | Ongoing |

Detailed task breakdown: `TresorAI_Portfolio_Build_Plan.xlsx` (private — not in the repo).

## License

[MIT](LICENSE) © 2026 Kishore Veleti

---

## 16. Tech stack

| Layer | Stack |
|---|---|
| **Frontend** | Angular 17+ · TypeScript 5 · Tailwind 3 · RxJS 7 |
| **AI / ML** *(intelligence-service)* | Gemini 2.0 Flash *(agent + tool use, LLM-as-judge)* · `text-embedding-004` · `sentence-transformers` *(fallback)* · pgvector · Prophet · XGBoost *(M5)* · OpenTelemetry |
| **Backend — Python (AI)** | Python 3.12 · FastAPI · Pydantic · uv · Conda *(pinned env)* |
| **Backend — JVM (streaming + BFF)** | Java 21 · Spring Boot 3 · Spring Kafka · Maven |
| **Data & messaging** | Apache Kafka 3.9 *(KRaft)* · PostgreSQL 16 · Redis 7 |
| **Contracts & APIs** | OpenAPI 3.1 · AsyncAPI 2.6 · WebSocket |
| **Infra & DevOps** | Google Cloud · Cloud Run · Artifact Registry · Docker · GitHub Actions |
| **Quality** | JUnit 5 · pytest · Jest · ESLint · Prettier |

<details>
<summary>Show the full badge wall</summary>

[![Angular](https://img.shields.io/badge/Angular-17+-DD0031?style=flat-square&logo=angular&logoColor=white)](https://angular.dev/) [![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/) [![Tailwind](https://img.shields.io/badge/Tailwind-3.x-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/) [![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-4285F4?style=flat-square&logo=googlegemini&logoColor=white)](https://ai.google.dev/) [![pgvector](https://img.shields.io/badge/pgvector-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector) [![Prophet](https://img.shields.io/badge/Prophet-1F77B4?style=flat-square&logo=meta&logoColor=white)](https://facebook.github.io/prophet/) [![XGBoost](https://img.shields.io/badge/XGBoost-EB6F0E?style=flat-square)](https://xgboost.readthedocs.io/) [![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![Java](https://img.shields.io/badge/Java-21-007396?style=flat-square&logo=openjdk&logoColor=white)](https://openjdk.org/projects/jdk/21/) [![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.x-6DB33F?style=flat-square&logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot) [![Apache Kafka](https://img.shields.io/badge/Kafka-3.9-231F20?style=flat-square&logo=apachekafka&logoColor=white)](https://kafka.apache.org/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/) [![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-6BA539?style=flat-square&logo=openapiinitiative&logoColor=white)](https://www.openapis.org/) [![AsyncAPI](https://img.shields.io/badge/AsyncAPI-2.6-FF3D00?style=flat-square&logo=asyncapi&logoColor=white)](https://www.asyncapi.com/) [![Cloud Run](https://img.shields.io/badge/Cloud%20Run-4285F4?style=flat-square&logo=googlecloud&logoColor=white)](https://cloud.google.com/run) [![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/) [![GitHub Actions](https://img.shields.io/badge/Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions) [![OpenTelemetry](https://img.shields.io/badge/OTel-425CC7?style=flat-square&logo=opentelemetry&logoColor=white)](https://opentelemetry.io/)

</details>
