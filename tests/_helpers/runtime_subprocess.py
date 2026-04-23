"""Shared subprocess helpers for the FastAPI runtime test lanes.

Extracted so the per-PR runtime smoke (`tests/integration/runtime/`) and the
nightly transport-parity lane (`tests/integration/transport_parity/`) share
the same port-allocation + health-poll pattern instead of duplicating it.
"""

from __future__ import annotations

import socket
import time

import httpx

DEFAULT_BOOT_BUDGET_S: float = 8.0


def pick_free_port() -> int:
    """Return an OS-assigned free TCP port on 127.0.0.1.

    Inherent race: the port may be claimed by another process between this
    call and the subsequent subprocess bind. Acceptable for serial pytest
    execution; document if a CI lane runs these in parallel.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_health(
    client: httpx.Client,
    boot_budget_s: float = DEFAULT_BOOT_BUDGET_S,
) -> httpx.Response:
    """Poll ``/health`` until 200 or ``boot_budget_s`` elapses.

    Raises ``AssertionError`` (NOT a pytest skip) on budget exhaustion —
    the substrate not booting within budget IS a test failure, not an
    environment skip.
    """
    last_exc: Exception | None = None
    deadline = time.monotonic() + boot_budget_s
    while time.monotonic() < deadline:
        try:
            response = client.get("/health", timeout=1.0)
            if response.status_code == 200:
                return response
        except httpx.HTTPError as exc:
            last_exc = exc
        time.sleep(0.1)
    raise AssertionError(
        f"runtime server did not become healthy within {boot_budget_s}s "
        f"(last error: {last_exc!r})"
    )
