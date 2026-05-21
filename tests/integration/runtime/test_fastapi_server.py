"""Integration test for `app.runtime_server` (Slab 1 Story 1.1c, AC-1.1c-C).

Spawns the FastAPI runtime as a subprocess, probes ``/health`` + ``/invoke``
via ``httpx``, asserts NFR-S2 loopback-only bind, and verifies clean shutdown
within 2 seconds.

Sandbox-AC discipline: skip-not-fail on Postgres unreachable; no operator-side
CLIs (``curl``, ``psql``, etc.) — uses shipped Python deps only.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator

import httpx
import pytest

from app.runtime.minimal_node import MINIMAL_NODE_NAME
from app.runtime.server import DEFAULT_BIND_HOST, app
from tests._helpers.runtime_subprocess import (
    DEFAULT_BOOT_BUDGET_S as SERVER_BOOT_BUDGET_S,
)
from tests._helpers.runtime_subprocess import (
    pick_free_port as _pick_free_port,
)
from tests._helpers.runtime_subprocess import (
    wait_for_health as _wait_for_health_helper,
)

SHUTDOWN_BUDGET_S: float = 2.0


def _wait_for_health(client: httpx.Client, deadline: float) -> httpx.Response:
    """Adapter preserving the test's deadline-based call signature."""
    remaining = max(0.0, deadline - time.monotonic())
    return _wait_for_health_helper(client, boot_budget_s=remaining)


@pytest.fixture
def runtime_server_subprocess() -> Iterator[tuple[subprocess.Popen[bytes], int]]:
    port = _pick_free_port()
    env = os.environ.copy()
    env["RUNTIME_PORT"] = str(port)
    env.pop("DATABASE_URL", None)
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
                # communicate() drains stdout/stderr pipes — without this on
                # Windows, a full pipe buffer (~4-64KB) can block the child's
                # write() and prevent shutdown within budget.
                proc.communicate(timeout=SHUTDOWN_BUDGET_S * 2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
        else:
            proc.communicate()


def test_app_state_pins_loopback_bind_host() -> None:
    """In-process introspection guard for NFR-S2 (defense-in-depth alongside subprocess check)."""
    assert app.state.bound_host == "127.0.0.1", (
        f"NFR-S2 violation: app.state.bound_host is {app.state.bound_host!r}, "
        "expected '127.0.0.1'. The runtime server must NOT silently bind to a "
        "non-loopback address (e.g. 0.0.0.0 for Windows-firewall debugging)."
    )
    assert DEFAULT_BIND_HOST == "127.0.0.1"


def test_runtime_server_health_invoke_and_clean_shutdown(
    runtime_server_subprocess: tuple[subprocess.Popen[bytes], int],
) -> None:
    proc, port = runtime_server_subprocess
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + SERVER_BOOT_BUDGET_S

    with httpx.Client(base_url=base_url) as client:
        health = _wait_for_health(client, deadline)
        body = health.json()
        assert body["status"] == "ok"
        assert body["postgres"] in {"connected", "skipped"}, body

        invoke = client.post("/invoke", json={"input": "ping"}, timeout=2.0)
        assert invoke.status_code == 200
        invoke_body = invoke.json()
        assert invoke_body["node"] == MINIMAL_NODE_NAME
        assert invoke_body["result"] == {
            "smoke": "ok",
            "node": MINIMAL_NODE_NAME,
            "echo": "ping",
        }

    # Clean shutdown: terminate() (cross-platform) and assert returncode is set
    # within budget. SIGTERM on POSIX maps to terminate(); on Windows it sends
    # CTRL_BREAK_EVENT / TerminateProcess. Either way returncode != None proves
    # uvicorn shut down without orphaning the process.
    proc.terminate()
    try:
        # communicate() drains pipes while waiting — protects against a Windows
        # pipe-buffer-full deadlock where the child blocks on stdout/stderr
        # write and never exits.
        proc.communicate(timeout=SHUTDOWN_BUDGET_S)
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"runtime server did not exit within {SHUTDOWN_BUDGET_S}s of terminate(); "
            "this indicates an orphaned thread or signal handler regression."
        )
    assert proc.returncode is not None, "subprocess returncode unset after communicate()"


def test_runtime_server_refuses_non_loopback_connection(
    runtime_server_subprocess: tuple[subprocess.Popen[bytes], int],
) -> None:
    """NFR-S2 negative test: a connection to a non-loopback address must fail.

    Strategy: discover the host's primary LAN IP via socket.gethostbyname; if
    unresolvable or it resolves to loopback, skip with a documented reason
    (the test is meaningless on a host with no real LAN IP). Otherwise attempt
    a TCP connect to that LAN IP on the runtime port with a 1s timeout and
    assert it is refused / times out.
    """
    proc, port = runtime_server_subprocess
    deadline = time.monotonic() + SERVER_BOOT_BUDGET_S
    with httpx.Client(base_url=f"http://127.0.0.1:{port}") as client:
        _wait_for_health(client, deadline)

    try:
        candidate_ips = {
            ip
            for ip in socket.gethostbyname_ex(socket.gethostname())[2]
            if not ip.startswith("127.")
        }
    except OSError as exc:
        pytest.skip(f"cannot resolve host LAN IPs ({exc}); non-loopback assertion N/A")
    if not candidate_ips:
        pytest.skip("host has no non-loopback IPv4 address; non-loopback assertion N/A")

    accepted: list[str] = []
    refusal_errors: dict[str, str] = {}
    for lan_ip in sorted(candidate_ips):
        try:
            with socket.create_connection((lan_ip, port), timeout=1.0) as sock:
                sock.close()
            accepted.append(lan_ip)
        except (TimeoutError, ConnectionRefusedError, OSError) as exc:
            refusal_errors[lan_ip] = repr(exc)

    assert not accepted, (
        f"runtime server accepted connections on non-loopback IPs {accepted}; "
        f"NFR-S2 requires 127.0.0.1-only bind. Per-IP refusal errors for the "
        f"IPs that did refuse: {refusal_errors}"
    )
