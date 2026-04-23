"""FastAPI runtime server for Slab 1 substrate (Story 1.1c).

Exposes:

- ``GET /health`` — liveness + Postgres reachability probe (skip-not-fail per
  sandbox-AC discipline; same shape as Story 1.1b's `test_server_version.py`).
- ``POST /invoke`` — invokes the shared `app.runtime.minimal_node` directly.

Bind policy: 127.0.0.1 only per NFR-S2. The bound host is exposed on
``app.state.bound_host`` so the integration test can introspect without
parsing logs.

Story 1.4 will replace the direct-call ``/invoke`` shape with the
manifest-driven graph dispatcher; this Slab 1 shape exists so M1 acceptance
evidence can begin accruing through the FastAPI transport.
"""

from __future__ import annotations

import os
from typing import Any

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from app.runtime.minimal_node import MINIMAL_NODE_NAME, minimal_node

DEFAULT_BIND_HOST: str = "127.0.0.1"
DEFAULT_BIND_PORT: int = 8765


class InvokePayload(BaseModel):
    """Body shape for ``POST /invoke``. Slab 1: only the ``input`` echo field."""

    model_config = ConfigDict(extra="forbid")

    input: str | None = Field(default=None)


def _postgres_status() -> str:
    """Return ``"connected"`` if Postgres reachable, else ``"skipped"``.

    Mirrors the skip-not-fail policy from `tests/integration/postgres/test_server_version.py`:
    sandbox-AC discipline says the runtime substrate proves liveness without
    requiring an operator-side service to be up. Catches the full `psycopg.Error`
    family so a malformed `DATABASE_URL` (raises `ProgrammingError`) is treated
    the same as an unreachable service rather than a 500 from `/health`.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return "skipped"
    try:
        with psycopg.connect(database_url, connect_timeout=2) as conn:
            _ = conn.info.server_version
        return "connected"
    except psycopg.Error:
        return "skipped"


def create_app() -> FastAPI:
    """Build the FastAPI app and pin the bound host on ``app.state``."""
    app = FastAPI(title="course-dev-ide migration runtime", version="0.1.0-slab1")
    app.state.bound_host = DEFAULT_BIND_HOST

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "postgres": _postgres_status()}

    @app.post("/invoke")
    def invoke(payload: InvokePayload) -> dict[str, Any]:
        # Direct call into the shared minimal node — same callable as smoke +
        # MCP ping. Story 1.4 introduces graph dispatch; do NOT compile a graph
        # here in 1.1c (scope creep into 1.4 territory).
        result = minimal_node(payload.model_dump())
        return {"node": MINIMAL_NODE_NAME, "result": result}

    return app


app: FastAPI = create_app()
