"""MCP server subprocess hygiene (Slab 1 Story 1.1d, AC-1.1d-B step 5).

Decoupled from the MCP-SDK roundtrip in `test_mcp_stdio_smoke.py` because the
SDK's `stdio_client` hides the subprocess.Popen handle inside its context
manager — we cannot directly assert ``proc.returncode is not None`` from
inside that flow. This test spawns ``python -m app.mcp_server`` via raw
``subprocess.Popen`` so the explicit shutdown-budget + returncode-set + no-
orphaned-pipes assertions called out in AC-1.1d-B step 5 are real, not
implicit.

Per AC-1.1d-B: graceful shutdown within 3 seconds, hard-fail at 10 seconds.

**Reopen-trigger note (per AC-1.1d-D):** if this test or the SDK round-trip
in `test_mcp_stdio_smoke.py` flakes >2% across its first 20 runs, reopen
the MCP-in-Slab-1 deferral conversation per the 2026-04-22 middle-path
consensus contingency. Do NOT silently retry-loop until green.
"""

from __future__ import annotations

import subprocess
import sys
import time

import pytest

from app.parity.contracts import parity_contract

pytestmark = pytest.mark.transport_parity

GRACEFUL_SHUTDOWN_BUDGET_S: float = 3.0
HARD_FAIL_SHUTDOWN_BUDGET_S: float = 10.0
SERVER_BOOT_PAUSE_S: float = 0.5


@parity_contract(
    surface_id="mcp_subprocess_hygiene",
    mandatory_transports=["mcp-subprocess"],
    optional_transports=[],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for test_mcp_subprocess_hygiene.py."""
    return "mcp_subprocess_hygiene"


def test_mcp_server_subprocess_terminates_cleanly_within_budget() -> None:
    """Spawn the MCP server, send terminate(), assert returncode set in <=3s.

    Verifies AC-1.1d-B step 5 literally: subprocess returncode IS set after
    shutdown, no orphaned pipes (drained via communicate()), graceful
    shutdown within 3 seconds (hard-fail at 10s budget).
    """
    proc = subprocess.Popen(
        [sys.executable, "-m", "app.mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Brief pause so the server has time to boot + open its stdio handlers
    # before we tear it down — without this, terminate() can race the
    # asyncio.run() startup and confuse the shutdown signal.
    time.sleep(SERVER_BOOT_PAUSE_S)
    assert proc.poll() is None, (
        f"MCP server subprocess exited prematurely with returncode "
        f"{proc.returncode!r}; cannot test shutdown hygiene"
    )

    t0 = time.monotonic()
    proc.terminate()
    try:
        # communicate() drains stdout/stderr WHILE waiting — protects against
        # a Windows pipe-buffer-full deadlock where the child blocks on a
        # final stderr write and never exits within budget. AC-1.1d-B step 5
        # "no orphaned pipes" is enforced by this drain.
        proc.communicate(timeout=HARD_FAIL_SHUTDOWN_BUDGET_S)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        pytest.fail(
            f"MCP server did not exit within hard-fail budget "
            f"{HARD_FAIL_SHUTDOWN_BUDGET_S}s of terminate(); orphaned subprocess "
            "indicates a signal-handler regression in app.mcp_server."
        )

    elapsed = time.monotonic() - t0
    assert proc.returncode is not None, (
        "subprocess.returncode is unset after communicate(); MCP server may "
        "have orphaned its process group."
    )
    assert elapsed <= GRACEFUL_SHUTDOWN_BUDGET_S, (
        f"MCP server took {elapsed:.2f}s to terminate; AC-1.1d-B step 5 "
        f"requires graceful shutdown within {GRACEFUL_SHUTDOWN_BUDGET_S}s. "
        f"(Hard-fail budget {HARD_FAIL_SHUTDOWN_BUDGET_S}s was met but soft "
        "budget exceeded — investigate uvicorn/asyncio shutdown latency.)"
    )
