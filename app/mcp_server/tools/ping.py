"""MCP ``ping`` tool — Slab 1 substrate target for FastAPI<->MCP parity (Story 1.1c).

The handler invokes `app.runtime.minimal_node` exactly as the FastAPI
``/invoke`` route does. Story 1.1d's transport-parity assertion compares the
two transports' payloads byte-for-byte; that test is only falsifiable
because both call sites import the SAME callable from the SAME module.

**Do not re-implement the no-op behavior here.** Always import from
`app.runtime.minimal_node`. See the docstring there for the load-bearing
invariant.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from app.runtime.minimal_node import MINIMAL_NODE_NAME, minimal_node

PING_TOOL_NAME: str = "ping"
PING_TOOL_DESCRIPTION: str = (
    "Migration substrate probe: invokes the shared minimal LangGraph node and "
    "returns its canonical payload. Story 1.1d uses this for FastAPI<->MCP "
    "byte-equivalent parity assertion."
)


def register(server: Server) -> None:
    """Bind the ``ping`` list_tools / call_tool handlers to ``server``.

    Encapsulated as a function so `app.mcp_server.server` can call it once at
    server-build time without relying on import-time global state across
    modules — keeps registration explicit and testable.
    """

    @server.list_tools()
    async def _list_tools() -> list[Tool]:
        return [
            Tool(
                name=PING_TOOL_NAME,
                description=PING_TOOL_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": ["string", "null"],
                            "description": "Optional echo string returned in the payload.",
                        },
                    },
                    "additionalProperties": False,
                },
            ),
        ]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        if name != PING_TOOL_NAME:
            raise ValueError(
                f"unknown tool {name!r}; Slab 1 server registers only {PING_TOOL_NAME!r}"
            )
        payload = minimal_node({"input": (arguments or {}).get("input")})
        return [
            TextContent(
                type="text",
                text=json.dumps({"node": MINIMAL_NODE_NAME, "result": payload}),
            ),
        ]
