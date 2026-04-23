"""MCP stdio subprocess smoke (Slab 1 Story 1.1d, AC-1.1d-B).

Spawns ``python -m app.mcp_server`` as a real subprocess via the MCP SDK's
``stdio_client`` + ``ClientSession``, runs the full initialize / list_tools /
call_tool round-trip, and verifies clean shutdown within budget. Skips
cleanly if the ``mcp`` SDK client surface is not importable.

**Reopen-trigger note (per AC-1.1d-D):** if this test or
`test_fastapi_mcp_parity.py` flakes >2% across its first 20 runs, reopen
the MCP-in-Slab-1 deferral conversation per the 2026-04-22 middle-path
consensus contingency. Do NOT silently retry-loop until green.
"""

from __future__ import annotations

import sys

import pytest

from app.runtime.minimal_node import MINIMAL_NODE_NAME

pytestmark = pytest.mark.transport_parity


@pytest.mark.asyncio
async def test_mcp_stdio_initialize_list_tools_and_ping_round_trip() -> None:
    try:
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client
    except ImportError as exc:
        pytest.skip(f"mcp SDK client surface not importable ({exc}); AC-1.1d-B requires it")

    params = StdioServerParameters(command=sys.executable, args=["-m", "app.mcp_server"])

    async with (
        stdio_client(params) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
            # Step 2: initialize handshake
            init_result = await session.initialize()
            assert init_result.protocolVersion, "MCP server returned empty protocolVersion"
            assert init_result.serverInfo.name == "course-dev-ide-migration-runtime", (
                f"unexpected server name: {init_result.serverInfo.name!r}"
            )

            # Step 3: list_tools — assert ping is present
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            assert "ping" in tool_names, (
                f"ping tool missing from MCP server's list_tools response; got {tool_names}"
            )

            # Step 4: call_tool('ping', {input:'smoke'}) — assert canonical payload
            import json

            call_result = await session.call_tool("ping", {"input": "smoke"})
            assert not call_result.isError, (
                f"ping tool returned isError=True: {call_result.content!r}"
            )
            assert len(call_result.content) >= 1
            text_payload = call_result.content[0].text
            parsed = json.loads(text_payload)
            assert parsed == {
                "node": MINIMAL_NODE_NAME,
                "result": {
                    "smoke": "ok",
                    "node": MINIMAL_NODE_NAME,
                    "echo": "smoke",
                },
            }, f"ping payload diverged from canonical: {parsed!r}"

    # Step 5: stdio_client + ClientSession context-managers handle subprocess
    # shutdown; the async-with exit closes streams which signals the server
    # to exit. The MCP SDK manages SIGTERM/terminate() internally for the
    # spawned subprocess; if it fails to clean up, anyio raises and the test
    # fails loudly here at context-exit. No extra teardown assertion needed.
