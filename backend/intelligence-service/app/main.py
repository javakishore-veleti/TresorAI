"""TrésorAI intelligence-service — FastAPI hello-world.

Endpoints to come (per ADR-0004 + ADR-0006 + ADR-0012):
  POST /score             — rule + embedding anomaly scorer
  POST /agent/judge       — Gemini agent loop with tool use
  POST /agent/act         — drafts Hold/Release/Alert action
  POST /forecast          — 30/60/90 cash-flow forecast
  GET  /datasets/status   — local cache state per dataset (admin portal feeds this)
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from tresorai.data.paths import datasets_root

app = FastAPI(
    title="TrésorAI · intelligence-service",
    version="0.0.1",
    description="The AI brain — Classical ML + Deep Learning + GenAI agent loop.",
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    datasets_root: str
    datasets_root_exists: bool


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    root = datasets_root()
    return HealthResponse(
        status="ok",
        service="intelligence-service",
        version=app.version,
        datasets_root=str(root),
        datasets_root_exists=root.exists(),
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "intelligence-service",
        "docs": "/docs",
        "health": "/health",
    }
