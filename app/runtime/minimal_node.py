"""Shared minimal LangGraph node — single source of truth for the no-op transport target.

**Three call sites import this module:**

1. `app.smoke_test` — runs the node via the manifest-loaded `StateGraph`.
2. `app.runtime.server` — `/invoke` route handler calls `minimal_node` directly.
3. `app.mcp_server.tools.ping` — MCP `ping` tool invokes `minimal_node`.

Story 1.1d's FastAPI<->MCP byte-equivalent parity assertion depends on every
transport returning the SAME dict from the SAME function. Re-implementing the
node in any of those three call sites would silently break the parity test in
ways the per-PR smoke can't catch.

**Do not re-implement. Always import.** This is a load-bearing invariant.
"""

from __future__ import annotations

from typing import Any

MINIMAL_NODE_NAME: str = "noop"
"""Stable identifier for the shared no-op node. Referenced by smoke + manifest + tests."""


def minimal_node(state: dict[str, Any] | Any) -> dict[str, Any]:
    """Return the canonical no-op payload, echoing the input field if present.

    Accepts either a plain dict (FastAPI / MCP / smoke entry path) or a Pydantic
    state object (LangGraph reducer entry path); reads ``input`` defensively so
    the same callable serves all three transports without typing gymnastics.
    """
    echo = state.get("input") if hasattr(state, "get") else getattr(state, "input", None)
    return {"smoke": "ok", "node": MINIMAL_NODE_NAME, "echo": echo}
