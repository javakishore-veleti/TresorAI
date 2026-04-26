"""System Health probes — environment-aware (local / gcp / aws / azure / hybrid).

Powers `Administration -> System Health` in portal-admin. Each probe runs in parallel
with a tight timeout so the endpoint always returns within ~1 second even when half
the dependencies are down.
"""

from __future__ import annotations

import asyncio
import os
import socket
import time
from datetime import datetime, timezone
from typing import Literal

import httpx
from pydantic import BaseModel


Status = Literal["up", "down", "unknown", "not_configured"]
Tier = Literal["frontend", "backend", "data", "messaging", "orchestration"]


class ServiceHealth(BaseModel):
    name: str
    tier: Tier
    target: str
    status: Status
    latency_ms: int | None
    detail: str | None = None


class SystemHealth(BaseModel):
    environment: str
    checked_at: str
    services: list[ServiceHealth]


def _env() -> str:
    return os.environ.get("TAI_ENV", "local")


def _service_targets() -> list[tuple[str, Tier, str, str]]:
    """Return (name, tier, kind, target) for each probe.

    `kind` is one of: http, tcp, not_configured
    `target` is a URL for http, "host:port" for tcp, "" for not_configured.
    Overrides per-environment via env vars TAI_SVC_<name>=<url-or-host:port>.
    """
    env = _env()

    def pick(name: str, default: str) -> str:
        return os.environ.get(f"TAI_SVC_{name.upper().replace('-', '_')}", default)

    if env == "local":
        return [
            ("portal-customer",      "frontend",      "http", pick("portal-customer",     "http://localhost:4200")),
            ("portal-admin",         "frontend",      "http", pick("portal-admin",        "http://localhost:4201")),
            ("admin-api",            "backend",       "http", pick("admin-api",           "http://localhost:8091/health")),
            ("intelligence-service", "backend",       "http", pick("intelligence-service","http://localhost:8090/health")),
            ("api-gateway",          "backend",       "http", pick("api-gateway",         "http://localhost:8080/actuator/health")),
            ("ingest-service",       "backend",       "http", pick("ingest-service",      "http://localhost:8081/actuator/health")),
            ("postgres",             "data",          "tcp",  pick("postgres",            "localhost:5432")),
            ("redis",                "data",          "tcp",  pick("redis",               "localhost:6379")),
            ("kafka",                "messaging",     "tcp",  pick("kafka",               "localhost:9092")),
            ("airflow",              "orchestration", "http", pick("airflow",             "http://localhost:8088/api/v1/health")),
        ]
    # Cloud variants resolve to managed equivalents
    if env == "gcp":
        return [
            ("portal-customer",      "frontend",      "http", pick("portal-customer",     "")),
            ("portal-admin",         "frontend",      "http", pick("portal-admin",        "")),
            ("admin-api",            "backend",       "http", pick("admin-api",           "")),
            ("intelligence-service", "backend",       "http", pick("intelligence-service","")),
            ("api-gateway",          "backend",       "http", pick("api-gateway",         "")),
            ("ingest-service",       "backend",       "http", pick("ingest-service",      "")),
            ("cloud-sql-postgres",   "data",          "http", pick("cloud_sql_postgres",  "")),
            ("memorystore-redis",    "data",          "http", pick("memorystore_redis",   "")),
            ("confluent-kafka",      "messaging",     "http", pick("confluent_kafka",     "")),
            ("cloud-composer",       "orchestration", "http", pick("cloud_composer",      "")),
            ("vertex-ai-endpoints",  "backend",       "http", pick("vertex_ai_endpoints", "")),
        ]
    if env == "aws":
        return [
            ("portal-customer",      "frontend",      "http", pick("portal-customer",     "")),
            ("portal-admin",         "frontend",      "http", pick("portal-admin",        "")),
            ("admin-api",            "backend",       "http", pick("admin-api",           "")),
            ("intelligence-service", "backend",       "http", pick("intelligence-service","")),
            ("api-gateway",          "backend",       "http", pick("api-gateway",         "")),
            ("ingest-service",       "backend",       "http", pick("ingest-service",      "")),
            ("rds-postgres",         "data",          "http", pick("rds_postgres",        "")),
            ("elasticache-redis",    "data",          "http", pick("elasticache_redis",   "")),
            ("msk-kafka",            "messaging",     "http", pick("msk_kafka",           "")),
            ("mwaa-airflow",         "orchestration", "http", pick("mwaa_airflow",        "")),
            ("sagemaker-endpoints",  "backend",       "http", pick("sagemaker",           "")),
        ]
    if env == "azure":
        return [
            ("portal-customer",      "frontend",      "http", pick("portal-customer",     "")),
            ("portal-admin",         "frontend",      "http", pick("portal-admin",        "")),
            ("admin-api",            "backend",       "http", pick("admin-api",           "")),
            ("intelligence-service", "backend",       "http", pick("intelligence-service","")),
            ("api-gateway",          "backend",       "http", pick("api-gateway",         "")),
            ("ingest-service",       "backend",       "http", pick("ingest-service",      "")),
            ("azure-postgres",       "data",          "http", pick("azure_postgres",      "")),
            ("azure-redis",          "data",          "http", pick("azure_redis",         "")),
            ("event-hubs-kafka",     "messaging",     "http", pick("event_hubs",          "")),
            ("azure-data-factory",   "orchestration", "http", pick("data_factory",        "")),
            ("azure-ml-endpoints",   "backend",       "http", pick("azure_ml",            "")),
        ]
    # hybrid -> trust per-service env overrides
    return _service_targets.__defaults__ or [
        ("portal-customer",      "frontend",  "http", pick("portal-customer",      "")),
        ("portal-admin",         "frontend",  "http", pick("portal-admin",         "")),
        ("admin-api",            "backend",   "http", pick("admin-api",            "")),
        ("intelligence-service", "backend",   "http", pick("intelligence-service", "")),
        ("api-gateway",          "backend",   "http", pick("api-gateway",          "")),
        ("ingest-service",       "backend",   "http", pick("ingest-service",       "")),
        ("postgres",             "data",      "http", pick("postgres",             "")),
        ("redis",                "data",      "http", pick("redis",                "")),
        ("kafka",                "messaging", "http", pick("kafka",                "")),
        ("airflow",              "orchestration", "http", pick("airflow",          "")),
    ]


async def _probe_http(client: httpx.AsyncClient, target: str) -> tuple[Status, int | None, str | None]:
    if not target:
        return "not_configured", None, "set TAI_SVC_* env var to enable this probe"
    started = time.perf_counter()
    try:
        r = await client.get(target, timeout=2.0, follow_redirects=True)
        latency = int((time.perf_counter() - started) * 1000)
        if r.status_code < 500:
            return "up", latency, f"HTTP {r.status_code}"
        return "down", latency, f"HTTP {r.status_code}"
    except (httpx.ConnectError, httpx.ConnectTimeout):
        return "down", None, "connection refused"
    except Exception as e:
        return "down", None, type(e).__name__


async def _probe_tcp(target: str) -> tuple[Status, int | None, str | None]:
    if not target:
        return "not_configured", None, None
    if ":" not in target:
        return "down", None, f"invalid target '{target}' (expected host:port)"
    host, port_s = target.rsplit(":", 1)
    try:
        port = int(port_s)
    except ValueError:
        return "down", None, f"invalid port in '{target}'"

    started = time.perf_counter()
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: socket.create_connection((host, port), timeout=1.5).close())
        latency = int((time.perf_counter() - started) * 1000)
        return "up", latency, f"tcp open on {target}"
    except (OSError, socket.timeout):
        return "down", None, f"cannot connect to {target}"


async def gather_system_health() -> SystemHealth:
    targets = _service_targets()
    async with httpx.AsyncClient() as client:
        async def probe(item: tuple[str, Tier, str, str]) -> ServiceHealth:
            name, tier, kind, target = item
            if kind == "http":
                status, latency, detail = await _probe_http(client, target)
            elif kind == "tcp":
                status, latency, detail = await _probe_tcp(target)
            else:
                status, latency, detail = "not_configured", None, None
            return ServiceHealth(
                name=name, tier=tier, target=target,
                status=status, latency_ms=latency, detail=detail,
            )

        services = await asyncio.gather(*[probe(t) for t in targets])

    return SystemHealth(
        environment=_env(),
        checked_at=datetime.now(timezone.utc).isoformat(),
        services=list(services),
    )
