"""FastAPI ↔ MCP byte-equivalent parity (Slab 1 Story 1.1d, AC-1.1d-C).

Drives the same input through both transports and asserts the residual
payloads (after stripping the allowed-divergence envelope fields per
`docs/dev-guide/transport-parity-envelope-exceptions.md`) are byte-equivalent.

This test is the operational evidence backing the architecture **D7**
three-transport parity claim and **FR2** compound-contract claim. CLI parity
(Slab 3 Story 3.4) and SSE parity (later) extend this same pattern.

**Reopen-trigger note (per AC-1.1d-D):** if this test or
`test_mcp_stdio_smoke.py` flakes >2% across its first 20 runs, reopen the
MCP-in-Slab-1 deferral conversation per the 2026-04-22 middle-path consensus
contingency. Do NOT silently retry-loop until green.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import types
from collections.abc import Iterator

import httpx
import pytest

from app.parity.contracts import parity_contract
from tests._helpers.runtime_subprocess import (
    DEFAULT_BOOT_BUDGET_S as SERVER_BOOT_BUDGET_S,
)
from tests._helpers.runtime_subprocess import (
    pick_free_port as _pick_free_port,
)
from tests._helpers.runtime_subprocess import (
    wait_for_health,
)

pytestmark = pytest.mark.transport_parity

PARITY_INPUT: str = "parity"
SHUTDOWN_BUDGET_S: float = 3.0


@parity_contract(
    surface_id="fastapi_mcp_parity",
    mandatory_transports=["http", "mcp-stdio"],
    optional_transports=[],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for test_fastapi_mcp_parity.py."""
    return "fastapi_mcp_parity"


@pytest.fixture
def fastapi_subprocess() -> Iterator[tuple[subprocess.Popen[bytes], int]]:
    port = _pick_free_port()
    env = os.environ.copy()
    env["RUNTIME_PORT"] = str(port)
    proc = subprocess.Popen(
        [sys.executable, "-m", "app.runtime_server"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        yield proc, port
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.communicate(timeout=SHUTDOWN_BUDGET_S * 2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
        else:
            proc.communicate()


def _capture_fastapi_payload(port: int) -> dict[str, object]:
    """Lane A — drive FastAPI /invoke; return the parsed JSON body."""
    base_url = f"http://127.0.0.1:{port}"
    with httpx.Client(base_url=base_url) as client:
        wait_for_health(client, boot_budget_s=SERVER_BOOT_BUDGET_S)
        response = client.post("/invoke", json={"input": PARITY_INPUT}, timeout=2.0)
        assert response.status_code == 200, (
            f"FastAPI /invoke returned status {response.status_code}: {response.text!r}"
        )
        return response.json()


async def _capture_mcp_payload() -> dict[str, object]:
    """Lane B — spawn MCP server subprocess, call ping tool, parse + unwrap.

    Strips the MCP envelope per `transport-parity-envelope-exceptions.md`:
    asserts ``isError == False`` then returns the parsed
    ``content[0].text`` as the residual payload (the same JSON shape FastAPI
    returns directly).
    """
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    params = StdioServerParameters(command=sys.executable, args=["-m", "app.mcp_server"])
    async with (
        stdio_client(params) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        call_result = await session.call_tool("ping", {"input": PARITY_INPUT})
        assert not call_result.isError, (
            f"MCP ping returned isError=True: {call_result.content!r}"
        )
        assert len(call_result.content) >= 1
        text_payload = call_result.content[0].text
        return json.loads(text_payload)


@pytest.mark.asyncio
async def test_fastapi_mcp_parity_residual_byte_equivalent(
    fastapi_subprocess: tuple[subprocess.Popen[bytes], int],
    minimal_node_fixture: types.ModuleType,
) -> None:
    """Drive both transports; assert residuals match the canonical no-op payload.

    Consumes ``minimal_node_fixture`` per AC-1.1d-A: the import-boundary
    contract is exercised by reading the canonical name + payload from the
    same module both transports route through, so any future drift on the
    SoT side will surface at this assertion site.
    """
    _proc, port = fastapi_subprocess
    canonical_name = minimal_node_fixture.MINIMAL_NODE_NAME
    canonical_payload = minimal_node_fixture.minimal_node({"input": PARITY_INPUT})

    fastapi_payload = _capture_fastapi_payload(port)
    mcp_payload = await _capture_mcp_payload()

    expected_residual: dict[str, object] = {
        "node": canonical_name,
        "result": canonical_payload,
    }

    assert fastapi_payload == expected_residual, (
        f"FastAPI residual diverged from canonical: {fastapi_payload!r}"
    )
    assert mcp_payload == expected_residual, (
        f"MCP residual diverged from canonical: {mcp_payload!r}"
    )
    assert fastapi_payload == mcp_payload, (
        "FastAPI ↔ MCP parity violation: residual payloads differ.\n"
        f"  FastAPI: {fastapi_payload!r}\n"
        f"  MCP:     {mcp_payload!r}\n"
        "If a transport-level field was added, update "
        "`docs/dev-guide/transport-parity-envelope-exceptions.md` AND the "
        "stripping logic in this test, in the same commit."
    )
