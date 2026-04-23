"""``uv run python -m app.mcp_server`` — MCP stdio runtime entry point.

Boots the shared `app.mcp_server.server.server` over stdio so an MCP client
(Claude Desktop, the MCP CLI, or Story 1.1d's parity-test subprocess) can
connect via stdin/stdout. Slab 1 ships the substrate; Story 1.1d wires the
nightly parity smoke that exercises this entry point against ``ping``.
"""

from __future__ import annotations

import asyncio

from mcp.server.stdio import stdio_server

from app.mcp_server.server import server


async def _serve() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    asyncio.run(_serve())


if __name__ == "__main__":
    main()
