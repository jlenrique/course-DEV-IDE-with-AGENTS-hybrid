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
import socket
import subprocess
import sys
import time
from collections.abc import Iterator

import httpx
import pytest

from app.runtime.minimal_node import MINIMAL_NODE_NAME

pytestmark = pytest.mark.transport_parity

PARITY_INPUT: str = "parity"
SERVER_BOOT_BUDGET_S: float = 8.0
SHUTDOWN_BUDGET_S: float = 3.0


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_health(client: httpx.Client, deadline: float) -> None:
    last_exc: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = client.get("/health", timeout=1.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError as exc:
            last_exc = exc
        time.sleep(0.1)
    raise AssertionError(
        f"FastAPI runtime did not become healthy within {SERVER_BOOT_BUDGET_S}s "
        f"(last error: {last_exc!r})"
    )


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
    deadline = time.monotonic() + SERVER_BOOT_BUDGET_S
    with httpx.Client(base_url=base_url) as client:
        _wait_for_health(client, deadline)
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
) -> None:
    _proc, port = fastapi_subprocess

    fastapi_payload = _capture_fastapi_payload(port)
    mcp_payload = await _capture_mcp_payload()

    expected_residual: dict[str, object] = {
        "node": MINIMAL_NODE_NAME,
        "result": {
            "smoke": "ok",
            "node": MINIMAL_NODE_NAME,
            "echo": PARITY_INPUT,
        },
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
