"""MCP server scaffold for the migration runtime (Slab 1 Story 1.1c, AC-1.1c-E).

Builds an `mcp.server.lowlevel.Server` instance with one real tool registered
(``ping``, defined in `app.mcp_server.tools.ping`). Story 1.1d will exercise
this server via a subprocess stdio smoke and assert byte-equivalent parity
against the FastAPI ``/invoke`` transport — both go through the same
`app.runtime.minimal_node`.

Slab 1 ships the substrate only. Tool catalog growth (e.g., ``gate_decide``
runtime wiring) is Slab 3 / Slab 4 work. The existing
`app.mcp_server.tools.gate_decide` module is the import-linter contract C3
allowlisted import path; it remains a placeholder until Slab 3 lands the
operator-verdict resume_api flow.
"""

from __future__ import annotations

from mcp.server import Server

from app.mcp_server.protocol import MCP_PROTOCOL_VERSION

SERVER_NAME: str = "course-dev-ide-migration-runtime"
SERVER_VERSION: str = "0.1.0-slab1"


def _build_server() -> Server:
    server = Server(name=SERVER_NAME, version=SERVER_VERSION)
    # Tool registration runs at import time of the tools module so the
    # ``@server.list_tools()`` / ``@server.call_tool()`` decorators bind
    # against this concrete server instance.
    from app.mcp_server.tools import ping as _ping  # noqa: F401  -- side-effect import

    _ping.register(server)
    return server


server: Server = _build_server()
"""Shared module-level server instance. ``__main__`` runs this via stdio."""

__all__ = ["MCP_PROTOCOL_VERSION", "SERVER_NAME", "SERVER_VERSION", "server"]
