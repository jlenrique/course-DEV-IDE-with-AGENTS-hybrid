"""Runtime start-path pre-flight executor (Story 35.3 / AD-7, AD-8, AD-11).

The runtime start path — not the HUD — executes pre-flight (phase 01) and live
heartbeats (phase 02) and gates SPOC spawn on them. This module owns:

* ``run_preflight(trial_id, runs_root, deps) -> PreflightResult`` — runs the
  ordered item set (phase-01 local checks, then phase-02 REAL live heartbeats),
  writing each item into the operator-surface projection **as it completes**
  via ``OperatorSurfaceAssembler.update_preflight_item`` (AD-11: projection-
  reported). Any non-soft item that is not ``pass`` (``fail`` OR ``missed``)
  makes the overall result NOT all-green — but ``missed`` and ``fail`` stay
  distinct states (two different alarms, AD-11). Soft items (coordination-db)
  are recorded but never gate.
* ``launch_hud_server(...)`` — launches the GET-only HUD server (Story 35.4,
  committed) as a subprocess child with the pinned env contract
  (``HUD_TRIAL_ID`` / ``HUD_RUN_DIR`` / ``HUD_LAUNCH_NONCE`` / ``HUD_PORT`` /
  ``HUD_MODE``), and NEVER raises: a launch failure returns ``None`` so the
  caller records a pre-flight FAIL instead (AD-7: a child bind failure is a
  pre-flight FAIL, never a fall-through). On Windows the child spawns with
  ``CREATE_NO_WINDOW`` so it never pops an empty console window (Story 42.2
  AC-7). Its ``atexit`` teardown is **status-aware** (Story 42.2 AC-1/AC-2):
  when the CLI process exits at a *gate pause* the child is LEFT ALIVE and
  LISTENING so the operator keeps browsing the surface; it is torn down (with a
  short grace) only on a terminal run status or an explicit operator stop.

Live calls (OpenAI, Gamma, the healthz identity probe) are injectable seams so
unit tests run hermetic with fakes; the real defaults do real network calls
(NFR5: no mocks in the live legs). The v1 heartbeat set is OpenAI + Gamma +
LangSmith-env-presence only (greenlight amendment 10); more platforms accrete
under the AD-13 falter-surface regression rule.
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
from collections.abc import Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

import httpx

from app.marcus.orchestrator.operator_surface_assembler import OperatorSurfaceAssembler
from app.models.runtime.operator_surface import PreflightItem

LOGGER = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
COORDINATION_DB_PATH = REPO_ROOT / "state" / "runtime" / "coordination.db"

OPENAI_MODELS_URL = "https://api.openai.com/v1/models"
OPENAI_HEARTBEAT_TIMEOUT_S = 10.0

#: The healthz identity probe (AD-7): 2s per attempt, briefly re-tried while the
#: freshly-launched child binds its port. A 200 with the WRONG identity fails
#: immediately (wrong-server-on-port); only connection failures are retried.
HEALTHZ_TIMEOUT_S = 2.0
HEALTHZ_READY_DEADLINE_S = 6.0
HEALTHZ_RETRY_BACKOFF_S = 0.25

#: Items whose absence is informational, not a spawn blocker (AD-11 soft set).
SOFT_ITEM_NAMES = frozenset({"coordination-db-readable"})

#: Run statuses that authorize HUD teardown when the CLI process exits (Story
#: 42.2 AC-2). A gate PAUSE (``paused-at-gate`` / ``paused-at-error``) is NOT
#: terminal — the run is parked awaiting the operator, so the HUD child must
#: stay alive and LISTENING across the pause (AC-1). Mirrors the notifier's own
#: ``TERMINAL_STATUSES``; the epic's ``cancelled`` / ``abandoned`` map onto the
#: envelope's ``failed`` status, and ``paused-at-error`` stays parked (there is
#: no post-ack signal in the envelope, and keeping the surface up is the
#: never-hide-the-run-from-the-operator default).
TERMINAL_RUN_STATUSES = frozenset({"completed", "failed"})

#: An explicit operator stop drops this sentinel file in the run dir to authorize
#: HUD teardown at the next CLI-process exit even before a terminal status
#: (Story 42.2 AC-2 explicit-stop path).
HUD_STOP_SENTINEL_NAME = ".hud-stop"

#: Grace (seconds) between ``terminate()`` and ``kill()`` when a teardown IS
#: authorized (Story 42.2 AC-2 short grace).
HUD_TEARDOWN_GRACE_S = 5.0

#: Deterministic item order (phase-01 local checks, then phase-02 live heartbeats).
PHASE_01_LOCAL_ITEMS = (
    "env-keys-present",
    "runs-root-writable",
    "coordination-db-readable",
    "litellm-importable",
    "cascade-config-validates",
)
PHASE_02_HEARTBEAT_ITEMS = ("openai", "gamma", "langsmith")


# --------------------------------------------------------------------------
# Result + dependency-injection shapes
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PreflightResult:
    """Outcome of a pre-flight run — the SPOC-spawn gate (AD-7/AD-11)."""

    all_green: bool
    items: list[PreflightItem]

    def blocking_items(self) -> list[PreflightItem]:
        """Non-soft items that are not ``pass`` — the reason spawn is blocked."""
        return [
            item
            for item in self.items
            if item.name not in SOFT_ITEM_NAMES and item.state != "pass"
        ]


@dataclass
class PreflightDeps:
    """Context + injectable live-call seams (fakes in unit tests, real by default).

    ``healthz_url`` / ``expected_trial_id`` / ``expected_launch_nonce`` /
    ``notifier_alive_fn`` are ``None`` when the HUD server / notifier were not
    launched (``--hud off``): the corresponding items are then simply omitted.
    ``healthz_fn`` lets the caller inject an immediate FAIL when the child
    failed to launch (AD-7) or a fake in tests.
    """

    env: Mapping[str, str] = field(default_factory=lambda: dict(os.environ))
    coordination_db_path: Path = COORDINATION_DB_PATH

    healthz_url: str | None = None
    expected_trial_id: str | None = None
    expected_launch_nonce: str | None = None
    notifier_alive_fn: Callable[[], bool] | None = None

    openai_heartbeat_fn: Callable[[], PreflightItem] | None = None
    gamma_heartbeat_fn: Callable[[], PreflightItem] | None = None
    healthz_fn: Callable[[], PreflightItem] | None = None


# --------------------------------------------------------------------------
# Identity helper
# --------------------------------------------------------------------------


def _canonical_trial_id(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError):
        return str(value)


def _safe(name: str, producer: Callable[[], PreflightItem]) -> PreflightItem:
    """Run one item producer; a raise becomes a FAIL item (never propagates)."""
    try:
        return producer()
    except Exception as exc:  # noqa: BLE001 — a check must never sink the start
        LOGGER.exception("pre-flight item %s raised", name)
        return PreflightItem(
            name=name, state="fail", output=f"check raised {type(exc).__name__}: {exc}"
        )


# --------------------------------------------------------------------------
# Phase-01 local checks (hermetic — no network)
# --------------------------------------------------------------------------


def _env_keys_item(env: Mapping[str, str]) -> PreflightItem:
    required = ("OPENAI_API_KEY", "LANGSMITH_API_KEY")
    missing = [name for name in required if not (env.get(name) or "").strip()]
    if missing:
        return PreflightItem(
            name="env-keys-present",
            state="fail",
            output=f"missing env keys: {', '.join(missing)}",
        )
    return PreflightItem(
        name="env-keys-present",
        state="pass",
        output="OPENAI_API_KEY + LANGSMITH_API_KEY present",
    )


def _runs_root_writable_item(runs_root: Path) -> PreflightItem:
    try:
        runs_root.mkdir(parents=True, exist_ok=True)
        probe = runs_root / f".preflight-write-probe-{os.getpid()}"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return PreflightItem(
            name="runs-root-writable",
            state="fail",
            output=f"{type(exc).__name__}: {exc}",
        )
    return PreflightItem(
        name="runs-root-writable", state="pass", output=runs_root.as_posix()
    )


def _coordination_db_item(db_path: Path) -> PreflightItem:
    """Soft check — a missing coordination.db is ``missed``, never a spawn block."""
    if not db_path.exists():
        return PreflightItem(
            name="coordination-db-readable",
            state="missed",
            output=f"absent at {db_path.as_posix()} (soft — non-blocking)",
        )
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            con.execute("SELECT 1")
        finally:
            con.close()
    except sqlite3.Error as exc:
        return PreflightItem(
            name="coordination-db-readable",
            state="fail",
            output=f"{type(exc).__name__}: {exc}",
        )
    return PreflightItem(
        name="coordination-db-readable", state="pass", output=db_path.as_posix()
    )


def _litellm_import_item() -> PreflightItem:
    try:
        import litellm  # noqa: F401
    except Exception as exc:  # noqa: BLE001 — any import failure blocks the run
        return PreflightItem(
            name="litellm-importable",
            state="fail",
            output=f"{type(exc).__name__}: {exc}",
        )
    return PreflightItem(name="litellm-importable", state="pass", output="import ok")


def _cascade_config_item() -> PreflightItem:
    """Reuse ``app.runtime.cascade_config`` validate logic directly (AD-11)."""
    try:
        from app.runtime.cascade_config import (
            ensure_pricing_covers_cascade,
            load_cascade,
            load_pricing,
        )

        cascade = load_cascade()
        pricing = load_pricing()
        ensure_pricing_covers_cascade(cascade, pricing)
    except Exception as exc:  # noqa: BLE001 — validate failure blocks the run
        return PreflightItem(
            name="cascade-config-validates",
            state="fail",
            output=f"{type(exc).__name__}: {exc}",
        )
    return PreflightItem(
        name="cascade-config-validates",
        state="pass",
        output="cascade + pricing validated",
    )


def _notifier_alive_item(alive_fn: Callable[[], bool]) -> PreflightItem:
    alive = alive_fn()
    if alive:
        return PreflightItem(
            name="notifier-process-alive", state="pass", output="notifier child alive"
        )
    return PreflightItem(
        name="notifier-process-alive",
        state="fail",
        output="notifier child not running",
    )


# --------------------------------------------------------------------------
# healthz identity probe (AD-7/AD-8) — wrong-server-on-port dies here
# --------------------------------------------------------------------------


def _default_healthz_item(deps: PreflightDeps) -> PreflightItem:
    url = deps.healthz_url
    if url is None:  # pragma: no cover — caller only invokes when url is set
        return PreflightItem(
            name="hud-server-healthz", state="missed", output="no HUD server launched"
        )
    expected_id = _canonical_trial_id(deps.expected_trial_id)
    deadline = time.monotonic() + HEALTHZ_READY_DEADLINE_S
    last_error: str | None = None
    start = time.monotonic()
    while True:
        try:
            resp = httpx.get(url, timeout=HEALTHZ_TIMEOUT_S)
        except httpx.HTTPError as exc:
            # Child may still be binding its port — retry connection failures.
            last_error = f"{type(exc).__name__}: {exc}"
            if time.monotonic() >= deadline:
                return PreflightItem(
                    name="hud-server-healthz",
                    state="fail",
                    output=f"HUD server unreachable at {url}: {last_error}",
                    latency_ms=(time.monotonic() - start) * 1000.0,
                )
            time.sleep(HEALTHZ_RETRY_BACKOFF_S)
            continue
        latency_ms = (time.monotonic() - start) * 1000.0
        if resp.status_code != 200:
            return PreflightItem(
                name="hud-server-healthz",
                state="fail",
                output=f"healthz HTTP {resp.status_code} at {url}",
                latency_ms=latency_ms,
            )
        try:
            body = resp.json()
        except ValueError:
            return PreflightItem(
                name="hud-server-healthz",
                state="fail",
                output="healthz body is not JSON",
                latency_ms=latency_ms,
            )
        found_id = _canonical_trial_id(body.get("trial_id"))
        found_nonce = body.get("launch_nonce")
        if found_id == expected_id and found_nonce == deps.expected_launch_nonce:
            return PreflightItem(
                name="hud-server-healthz",
                state="pass",
                output=f"identity matched ({found_id})",
                latency_ms=latency_ms,
            )
        # A 200 answering the port with a DIFFERENT identity is the
        # wrong-server-on-port failure (AD-8) — a hard FAIL, never a retry.
        return PreflightItem(
            name="hud-server-healthz",
            state="fail",
            output=(
                "wrong-server-on-port: bound "
                f"{expected_id}/{deps.expected_launch_nonce}, found "
                f"{found_id}/{found_nonce}"
            ),
            latency_ms=latency_ms,
        )


# --------------------------------------------------------------------------
# Phase-02 live heartbeats (REAL calls — NFR5, no mocks)
# --------------------------------------------------------------------------


def _default_openai_heartbeat(env: Mapping[str, str]) -> PreflightItem:
    key = (env.get("OPENAI_API_KEY") or "").strip()
    if not key:
        return PreflightItem(
            name="openai", state="missed", output="OPENAI_API_KEY absent"
        )
    start = time.monotonic()
    try:
        resp = httpx.get(
            OPENAI_MODELS_URL,
            headers={"Authorization": f"Bearer {key}"},
            timeout=OPENAI_HEARTBEAT_TIMEOUT_S,
        )
    except httpx.HTTPError as exc:
        return PreflightItem(
            name="openai",
            state="fail",
            output=f"{type(exc).__name__}: {exc}",
            latency_ms=(time.monotonic() - start) * 1000.0,
        )
    latency_ms = (time.monotonic() - start) * 1000.0
    if resp.status_code != 200:
        return PreflightItem(
            name="openai",
            state="fail",
            output=f"HTTP {resp.status_code}",
            latency_ms=latency_ms,
        )
    # Rate-limit headers are a PROXY quota reading when present; absent means we
    # have no direct quota signal (never-false-green: confidence stays unknown).
    remaining = resp.headers.get("x-ratelimit-remaining-requests") or resp.headers.get(
        "x-ratelimit-remaining-tokens"
    )
    if remaining is not None:
        return PreflightItem(
            name="openai",
            state="pass",
            output="GET /v1/models 200",
            latency_ms=latency_ms,
            quota_reading=f"rate-limit remaining: {remaining}",
            quota_confidence="proxy",
        )
    return PreflightItem(
        name="openai",
        state="pass",
        output="GET /v1/models 200 (no rate-limit headers)",
        latency_ms=latency_ms,
        quota_confidence="unknown",
    )


def _default_gamma_heartbeat(env: Mapping[str, str]) -> PreflightItem:
    key = (env.get("GAMMA_API_KEY") or "").strip()
    if not key:
        return PreflightItem(
            name="gamma", state="missed", output="GAMMA_API_KEY absent"
        )
    # Lazy import keeps the requests-based client (and its layer weight) out of
    # the hermetic unit-test path — tests inject a fake ``gamma_heartbeat_fn``.
    from scripts.api_clients.gamma_client import GammaClient

    start = time.monotonic()
    try:
        themes = GammaClient(api_key=key).list_themes(limit=1)
    except Exception as exc:  # noqa: BLE001 — any client failure is a heartbeat fail
        return PreflightItem(
            name="gamma",
            state="fail",
            output=f"{type(exc).__name__}: {exc}",
            latency_ms=(time.monotonic() - start) * 1000.0,
        )
    latency_ms = (time.monotonic() - start) * 1000.0
    # list_themes carries no credits field, so the reading is a PROXY (auth +
    # reachability confirmed) not a DIRECT credit balance.
    return PreflightItem(
        name="gamma",
        state="pass",
        output=f"list_themes 200 ({len(themes)} theme(s) reachable)",
        latency_ms=latency_ms,
        quota_reading="credits not exposed by /themes",
        quota_confidence="proxy",
    )


def _langsmith_env_heartbeat(env: Mapping[str, str]) -> PreflightItem:
    """v1 LangSmith heartbeat is env-presence only (greenlight amendment 10)."""
    if (env.get("LANGSMITH_API_KEY") or "").strip():
        project = (env.get("LANGSMITH_PROJECT") or "").strip()
        detail = "LANGSMITH_API_KEY present"
        if project:
            detail += f" (project={project})"
        return PreflightItem(name="langsmith", state="pass", output=detail)
    return PreflightItem(
        name="langsmith", state="missed", output="LANGSMITH_API_KEY absent"
    )


# --------------------------------------------------------------------------
# Orchestrator
# --------------------------------------------------------------------------


def run_preflight(
    trial_id: UUID | str,
    runs_root: Path,
    deps: PreflightDeps,
) -> PreflightResult:
    """Run pre-flight + heartbeats, projecting each item as it completes (AD-11).

    Returns the SPOC-spawn gate result. ``all_green`` is True iff every
    non-soft item is ``pass`` (both ``fail`` and ``missed`` break green, but
    stay distinct states). Never raises: item producers are individually
    guarded and the projection writes are swallowed by the assembler.
    """
    runs_root = Path(runs_root)
    assembler = OperatorSurfaceAssembler(trial_id, runs_root)
    items: list[PreflightItem] = []

    def _record(item: PreflightItem) -> None:
        items.append(item)
        # Writes into the projection AS IT COMPLETES (AD-11); the assembler
        # swallows its own faults and never raises into the start path.
        assembler.update_preflight_item(item)

    # -- phase 01: local checks --------------------------------------------
    _record(_safe("env-keys-present", lambda: _env_keys_item(deps.env)))
    _record(_safe("runs-root-writable", lambda: _runs_root_writable_item(runs_root)))
    _record(
        _safe(
            "coordination-db-readable",
            lambda: _coordination_db_item(deps.coordination_db_path),
        )
    )
    _record(_safe("litellm-importable", _litellm_import_item))
    _record(_safe("cascade-config-validates", _cascade_config_item))
    if deps.healthz_fn is not None or deps.healthz_url is not None:
        healthz_fn = deps.healthz_fn or (lambda: _default_healthz_item(deps))
        _record(_safe("hud-server-healthz", healthz_fn))
    if deps.notifier_alive_fn is not None:
        _record(
            _safe(
                "notifier-process-alive",
                lambda: _notifier_alive_item(deps.notifier_alive_fn),
            )
        )

    # -- phase 02: REAL live heartbeats ------------------------------------
    openai_fn = deps.openai_heartbeat_fn or (
        lambda: _default_openai_heartbeat(deps.env)
    )
    _record(_safe("openai", openai_fn))
    gamma_fn = deps.gamma_heartbeat_fn or (lambda: _default_gamma_heartbeat(deps.env))
    _record(_safe("gamma", gamma_fn))
    _record(_safe("langsmith", lambda: _langsmith_env_heartbeat(deps.env)))

    all_green = all(
        item.state == "pass"
        for item in items
        if item.name not in SOFT_ITEM_NAMES
    )
    return PreflightResult(all_green=all_green, items=items)


# --------------------------------------------------------------------------
# HUD server launch plumbing (AD-7/AD-8)
# --------------------------------------------------------------------------


def _no_window_creationflags() -> int:
    """``CREATE_NO_WINDOW`` on Windows, else ``0`` (Story 42.2 AC-7).

    A console child spawned without this flag pops an empty terminal window on
    Windows — the ergonomics defect the operator hit repeatedly during dev
    sessions. Non-Windows platforms (and Pythons lacking the flag) are
    unaffected: the return is ``0`` and no ``creationflags`` are applied.
    """
    if sys.platform == "win32":
        return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    return 0


def _read_run_status(run_dir: Path) -> str | None:
    """Best-effort read of the run's current status from the persisted envelope.

    Reads ``run.json`` (the envelope) first, then the ``operator-surface.json``
    projection's nested ``envelope.status``. NEVER raises: an absent, unreadable,
    or corrupt file yields ``None``, which the teardown treats as *non-terminal*
    (child left ALIVE) — the safe default that never kills the surface out from
    under an operator who is still parked at a gate (Story 42.2 AC-1).
    """
    run_dir = Path(run_dir)
    for name, extract in (
        ("run.json", lambda d: d.get("status")),
        ("operator-surface.json", lambda d: (d.get("envelope") or {}).get("status")),
    ):
        try:
            data = json.loads((run_dir / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            status = extract(data)
            if isinstance(status, str):
                return status
    return None


def _terminate_with_grace(proc: subprocess.Popen, grace: float) -> None:
    """Terminate ``proc``, wait up to ``grace`` seconds, then hard-kill. Quiet."""
    with suppress(Exception):
        if proc.poll() is not None:
            return
        proc.terminate()
        try:
            proc.wait(timeout=grace)
        except Exception:  # noqa: BLE001 — TimeoutExpired (or a fake proc) → hard kill
            with suppress(Exception):
                proc.kill()


def _status_aware_teardown(
    proc: subprocess.Popen,
    run_dir: Path,
    *,
    grace: float = HUD_TEARDOWN_GRACE_S,
) -> None:
    """``atexit`` hook that ties the HUD child's death to the RUN, not the CLI.

    The old contract blindly terminated the child when the ``trial start``
    process exited — so a gate pause (the process returning to the shell) killed
    the HUD. This hook instead tears the child down ONLY when the run is in a
    terminal status (:data:`TERMINAL_RUN_STATUSES`) OR an explicit operator stop
    was requested (:func:`request_hud_stop`), each with a short grace. A gate
    pause (or any non-terminal / unknown status) leaves the child ALIVE and
    LISTENING so the operator keeps the surface across pause→resume (Story 42.2
    AC-1/AC-2). NEVER raises (AC-6): a teardown fault is swallowed at exit.
    """
    try:
        if proc.poll() is not None:
            return  # already gone
        stop_requested = False
        with suppress(Exception):
            stop_requested = (Path(run_dir) / HUD_STOP_SENTINEL_NAME).exists()
        status = _read_run_status(run_dir)
        if status in TERMINAL_RUN_STATUSES or stop_requested:
            _terminate_with_grace(proc, grace)
        # else: parked at a pause (or status unknown) → leave the child ALIVE.
    except Exception:  # noqa: BLE001 — a teardown fault must never surface at exit
        LOGGER.debug("HUD status-aware teardown swallowed a fault", exc_info=True)


def request_hud_stop(run_dir: Path) -> None:
    """Authorize HUD teardown at the next CLI-process exit (Story 42.2 AC-2).

    Drops the explicit-stop sentinel in ``run_dir`` so :func:`_status_aware_teardown`
    tears the child down (with a grace) even before the run reaches a terminal
    status. Idempotent; NEVER raises.
    """
    with suppress(Exception):
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / HUD_STOP_SENTINEL_NAME).write_text("stop", encoding="utf-8")


def launch_hud_server(
    *,
    trial_id: UUID | str,
    run_dir: Path,
    launch_nonce: str,
    port: int,
    mode: str = "session",
    python_executable: str | None = None,
    popen: Callable[..., subprocess.Popen] = subprocess.Popen,
) -> subprocess.Popen | None:
    """Launch the GET-only HUD server child (Story 35.4) — NEVER raises.

    Returns the :class:`subprocess.Popen` handle, or ``None`` on launch
    failure (the caller then records the healthz pre-flight item as FAIL —
    AD-7: a child bind failure is a pre-flight FAIL, never a raise or a
    fall-through to whatever else answers the port).

    Windows: the child spawns with ``CREATE_NO_WINDOW`` so it never pops an
    empty console window (Story 42.2 AC-7). Lifecycle: registers a
    **status-aware** ``atexit`` teardown (:func:`_status_aware_teardown`) so the
    child survives a gate pause and is stopped only on a terminal run status or
    an explicit operator stop (Story 42.2 AC-1/AC-2) — it is no longer coupled
    to the CLI process's exit. ``popen`` is injectable so unit tests never spawn
    a real process.
    """
    run_dir = Path(run_dir)
    env = {
        **os.environ,
        "HUD_TRIAL_ID": str(trial_id),
        "HUD_RUN_DIR": str(run_dir),
        "HUD_LAUNCH_NONCE": launch_nonce,
        "HUD_PORT": str(port),
        "HUD_MODE": mode,
    }
    argv = [python_executable or sys.executable, "-m", "app.hud.server"]
    handle = None
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        handle = open(run_dir / "hud-server.log", "ab")  # noqa: SIM115 — child owns it
        popen_kwargs: dict[str, object] = {
            "env": env,
            "stdout": handle,
            "stderr": handle,
            "stdin": subprocess.DEVNULL,
        }
        creationflags = _no_window_creationflags()
        if creationflags:
            popen_kwargs["creationflags"] = creationflags
        proc = popen(argv, **popen_kwargs)
    except Exception as exc:  # noqa: BLE001 — launch failure is a FAIL, never a raise
        LOGGER.exception("HUD server child failed to launch: %s", exc)
        if handle is not None:
            with suppress(Exception):
                handle.close()
        return None
    atexit.register(_status_aware_teardown, proc, run_dir)
    LOGGER.info("launched HUD server child for trial %s on port %s", trial_id, port)
    return proc


def probe_hud_identity(
    port: int,
    *,
    timeout: float = HEALTHZ_TIMEOUT_S,
    get: Callable[..., object] | None = None,
) -> tuple[str | None, object] | None:
    """Best-effort ``GET /healthz`` on the loopback ``port`` (Story 42.2 AC-3).

    Returns ``(canonical_trial_id, launch_nonce)`` a live HUD reports, or
    ``None`` when nothing healthy answers. NEVER raises — a connection failure,
    non-200, or non-JSON body all resolve to ``None`` (nothing to reattach to).
    """
    getter = get or httpx.get
    url = f"http://127.0.0.1:{port}/healthz"
    try:
        resp = getter(url, timeout=timeout)
        if getattr(resp, "status_code", None) != 200:
            return None
        body = resp.json()
    except Exception:  # noqa: BLE001 — probe is advisory; any failure = no reattach
        return None
    if not isinstance(body, dict):
        return None
    found_id = _canonical_trial_id(body.get("trial_id"))
    if found_id is None:
        return None
    return found_id, body.get("launch_nonce")


def reattach_or_launch_hud_server(
    *,
    trial_id: UUID | str,
    run_dir: Path,
    launch_nonce: str,
    port: int,
    mode: str = "session",
    python_executable: str | None = None,
    popen: Callable[..., subprocess.Popen] = subprocess.Popen,
    probe: Callable[[], tuple[str | None, object] | None] | None = None,
) -> tuple[subprocess.Popen | None, str]:
    """Reuse an already-live HUD for this trial instead of double-launching.

    Story 42.2 AC-3 (no orphaned/duplicate HUD across pause→resume). Health-checks
    the port first: if a live HUD already reports THIS ``trial_id``, it is reused
    (returns ``(None, "reused")`` — no new child spawned). Otherwise a fresh child
    is launched (``(proc, "launched")`` or ``(None, "failed")`` on launch failure).
    A foreign identity on the port is NOT reused — a fresh launch proceeds and the
    pre-flight healthz identity check catches the genuine wrong-server-on-port
    conflict (AD-8). NEVER raises (AC-6).
    """
    probe_fn = probe or (lambda: probe_hud_identity(port))
    identity = None
    with suppress(Exception):
        identity = probe_fn()
    if identity is not None:
        found_id, _found_nonce = identity
        if found_id == _canonical_trial_id(str(trial_id)):
            LOGGER.info(
                "HUD already live for trial %s on port %s — reusing (no double-launch)",
                trial_id,
                port,
            )
            return None, "reused"
    proc = launch_hud_server(
        trial_id=trial_id,
        run_dir=run_dir,
        launch_nonce=launch_nonce,
        port=port,
        mode=mode,
        python_executable=python_executable,
        popen=popen,
    )
    return proc, ("launched" if proc is not None else "failed")


# --------------------------------------------------------------------------
# Public read-only overlay — tunnel plumbing (Story 42.4, operator-gated)
#
# The overlay is ADDITIVE and DEGRADES REACH ONLY: when no tunnel is configured
# (or a child fails to launch) the local HUD is unchanged and the run proceeds
# (AC-5). Every function here NEVER raises. The tunnel is fronted onto a
# SEPARATE public app (``app.hud.public``) on its own local port — never onto
# the localhost authority server — and the tunnel is ALWAYS a NAMED /
# identity-aware tunnel, NEVER an anonymous quick-tunnel (AC-1/AC-3).
# --------------------------------------------------------------------------

#: Default local port the public overlay app binds (the tunnel forwards to it).
DEFAULT_PUBLIC_HUD_PORT = 8792

#: The tunnel modes the launcher will run. Anything else (incl. absent) leaves
#: the overlay unconfigured — the launcher NEVER guesses a mode.
#:
#: ``ngrok`` (Story 42.8) fronts a **reserved** ngrok domain — one stable,
#: no-login public URL — added ALONGSIDE ``cloudflare`` / ``tailscale`` (the
#: operator picks via ``HUD_TUNNEL_MODE``). Its stability comes from the
#: reserved ``--domain=`` (never a random per-run quick-tunnel ``--url``).
PUBLIC_OVERLAY_MODES = frozenset({"cloudflare", "tailscale", "ngrok"})


@dataclass(frozen=True)
class PublicOverlayConfig:
    """Operator-provided tunnel config, read from ``.env`` / settings — never hardcoded.

    ``cloudflare`` REQUIRES a named-tunnel credential (``HUD_TUNNEL_TOKEN`` for a
    remotely-managed tunnel, or ``HUD_TUNNEL_NAME`` for a locally-configured one)
    — with neither, :meth:`from_env` returns ``None`` (unconfigured) rather than
    ever degrading to an anonymous quick-tunnel. ``tailscale`` serves the local
    port on the machine's stable ``*.ts.net`` name, tailnet-restricted.

    ``ngrok`` (Story 42.8) fronts a **reserved** ngrok domain — one stable,
    no-login public URL. It REQUIRES ``HUD_TUNNEL_NGROK_DOMAIN`` (the reserved
    domain; absent → :meth:`from_env` returns ``None``, inert). The optional
    ``ngrok_authtoken`` (from ``HUD_TUNNEL_NGROK_AUTHTOKEN``) is a **secret**: it
    is NEVER placed on the argv (:func:`tunnel_argv`) or logged — the launcher
    hands it to the ngrok child through its process env (``NGROK_AUTHTOKEN``,
    which ngrok v3 reads natively). When it is absent the child falls back to the
    operator's own ``ngrok.yml`` (e.g. a prior ``ngrok config add-authtoken``).
    """

    mode: str
    public_port: int = DEFAULT_PUBLIC_HUD_PORT
    hostname: str | None = None
    cloudflare_token: str | None = None
    tunnel_name: str | None = None
    cloudflared_bin: str = "cloudflared"
    tailscale_bin: str = "tailscale"
    ngrok_domain: str | None = None
    ngrok_authtoken: str | None = None
    ngrok_bin: str = "ngrok"

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> PublicOverlayConfig | None:
        """Parse overlay config; ``None`` when unconfigured or invalid (never raises)."""
        raw_mode = (env.get("HUD_TUNNEL_MODE") or "").strip().lower()
        if raw_mode == "cloudflared":
            raw_mode = "cloudflare"
        if raw_mode not in PUBLIC_OVERLAY_MODES:
            return None  # unset / off / unknown → overlay stays absent

        try:
            public_port = int(env.get("HUD_PUBLIC_PORT", str(DEFAULT_PUBLIC_HUD_PORT)))
        except (TypeError, ValueError):
            public_port = DEFAULT_PUBLIC_HUD_PORT

        hostname = (env.get("HUD_TUNNEL_HOSTNAME") or "").strip() or None
        cloudflared_bin = (env.get("HUD_TUNNEL_CLOUDFLARED_BIN") or "cloudflared").strip()
        tailscale_bin = (env.get("HUD_TUNNEL_TAILSCALE_BIN") or "tailscale").strip()
        ngrok_bin = (env.get("HUD_TUNNEL_NGROK_BIN") or "ngrok").strip()

        if raw_mode == "ngrok":
            # The reserved domain is what makes the URL STABLE run-to-run (never
            # a random quick-tunnel). Absent → inert, like the other modes.
            domain = (env.get("HUD_TUNNEL_NGROK_DOMAIN") or "").strip() or None
            if domain is None:
                LOGGER.warning(
                    "HUD_TUNNEL_MODE=ngrok but HUD_TUNNEL_NGROK_DOMAIN is not set "
                    "— refusing to open a random per-run quick-tunnel; overlay "
                    "stays unconfigured."
                )
                return None
            # SECRET: the authtoken NEVER rides the argv or a log line. It is
            # handed to the ngrok child through NGROK_AUTHTOKEN in its process
            # env (see ``_tunnel_child_env``); absent → ngrok uses its own config.
            authtoken = (env.get("HUD_TUNNEL_NGROK_AUTHTOKEN") or "").strip() or None
            return cls(
                mode="ngrok",
                public_port=public_port,
                hostname=hostname,
                cloudflared_bin=cloudflared_bin,
                tailscale_bin=tailscale_bin,
                ngrok_domain=domain,
                ngrok_authtoken=authtoken,
                ngrok_bin=ngrok_bin or "ngrok",
            )

        if raw_mode == "cloudflare":
            token = (env.get("HUD_TUNNEL_TOKEN") or "").strip() or None
            name = (env.get("HUD_TUNNEL_NAME") or "").strip() or None
            # NEVER an anonymous quick-tunnel: a named credential is mandatory.
            if token is None and name is None:
                LOGGER.warning(
                    "HUD_TUNNEL_MODE=cloudflare but neither HUD_TUNNEL_TOKEN nor "
                    "HUD_TUNNEL_NAME is set — refusing to open an anonymous "
                    "quick-tunnel; overlay stays unconfigured."
                )
                return None
            return cls(
                mode="cloudflare",
                public_port=public_port,
                hostname=hostname,
                cloudflare_token=token,
                tunnel_name=name,
                cloudflared_bin=cloudflared_bin,
                tailscale_bin=tailscale_bin,
            )

        # tailscale — the stable machine name is intrinsic to the tailnet; no
        # token needed. Identity is enforced by the operator's tailnet ACL.
        return cls(
            mode="tailscale",
            public_port=public_port,
            hostname=hostname,
            cloudflared_bin=cloudflared_bin,
            tailscale_bin=tailscale_bin,
        )


def tunnel_argv(config: PublicOverlayConfig) -> list[str]:
    """Build the tunnel child's argv — ALWAYS named/identity-aware (AC-1/AC-3).

    Guaranteed to never contain the cloudflared quick-tunnel ``--url`` flag: a
    cloudflare tunnel is ``tunnel run --token <t>`` or ``tunnel run <name>``; a
    tailscale tunnel is ``serve`` onto the stable machine name; an ngrok tunnel
    is ``http --domain=<reserved> <port>`` — the reserved ``--domain`` makes the
    URL STABLE (never a random ``--url`` quick-tunnel).
    """
    if config.mode == "ngrok":
        # SECRET HYGIENE: the authtoken is DELIBERATELY absent from the argv — it
        # is passed to the child via NGROK_AUTHTOKEN in its process env instead
        # (``_tunnel_child_env``), so it can never leak onto a command line or a
        # log. Only the (non-secret) reserved domain + port appear here.
        return [
            config.ngrok_bin,
            "http",
            f"--domain={config.ngrok_domain}",
            str(config.public_port),
        ]
    if config.mode == "cloudflare":
        if config.cloudflare_token:
            return [config.cloudflared_bin, "tunnel", "run", "--token", config.cloudflare_token]
        return [config.cloudflared_bin, "tunnel", "run", str(config.tunnel_name)]
    # tailscale Serve onto the loopback public app port.
    return [
        config.tailscale_bin,
        "serve",
        "--bg",
        f"http://127.0.0.1:{config.public_port}",
    ]


def public_overlay_url(config: PublicOverlayConfig | None) -> str | None:
    """The STABLE public URL the operator hands out, or ``None`` (Story 42.8 AC-5).

    ``ngrok`` → ``https://<reserved-domain>`` (constant run-to-run — that is the
    whole point of the reserved domain). ``cloudflare`` → ``https://<hostname>``
    when a hostname is configured. ``tailscale``'s ``*.ts.net`` name is intrinsic
    to the tailnet (not in our config), so it has no derivable URL here. NEVER
    contains a secret — the ngrok authtoken lives only in the child's env.
    """
    if config is None:
        return None
    if config.mode == "ngrok" and config.ngrok_domain:
        return f"https://{config.ngrok_domain}"
    if config.mode == "cloudflare" and config.hostname:
        return f"https://{config.hostname}"
    return None


#: The sentinel file the launcher drops in the run dir carrying the stable
#: public URL (Story 42.8 AC-5) — a secret-free, best-effort emit so the local
#: HUD / operator can surface the URL each run. NEVER carries the authtoken.
HUD_PUBLIC_URL_SENTINEL_NAME = ".hud-public-url"


def _tunnel_child_env(config: PublicOverlayConfig) -> dict[str, str]:
    """Process env for the tunnel child — inherits ``os.environ``, overlays secrets.

    For ``ngrok`` with an operator-provided authtoken, overlays
    ``NGROK_AUTHTOKEN`` so the child authenticates purely from its env (ngrok v3
    reads it natively) — NO ``ngrok config add-authtoken`` step required, and the
    secret never touches the argv or a log. Absent → no overlay, so the child
    falls back to the operator's own ``ngrok.yml``. Other modes inherit env only.
    """
    env = dict(os.environ)
    if config.mode == "ngrok" and config.ngrok_authtoken:
        env["NGROK_AUTHTOKEN"] = config.ngrok_authtoken
    return env


@dataclass
class PublicOverlayHandles:
    """Outcome of an overlay launch attempt (never raises to build this)."""

    status: str  # "unconfigured" | "launched" | "app-failed" | "tunnel-failed"
    app_proc: subprocess.Popen | None = None
    tunnel_proc: subprocess.Popen | None = None
    config: PublicOverlayConfig | None = None
    public_url: str | None = None  # the STABLE URL surfaced to the operator (AC-5)


def _spawn_child(
    argv: list[str],
    *,
    env: Mapping[str, str],
    log_path: Path,
    popen: Callable[..., subprocess.Popen],
) -> subprocess.Popen | None:
    """Spawn a windowless, detached-stdio child; ``None`` on any failure (quiet).

    Mirrors :func:`launch_hud_server`'s child discipline: ``CREATE_NO_WINDOW`` on
    win32 (Story 42.2 AC-7), stdout/stderr to a log file, no stdin. NEVER raises.
    """
    handle = None
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(log_path, "ab")  # noqa: SIM115 — child owns it
        popen_kwargs: dict[str, object] = {
            "env": dict(env),
            "stdout": handle,
            "stderr": handle,
            "stdin": subprocess.DEVNULL,
        }
        creationflags = _no_window_creationflags()
        if creationflags:
            popen_kwargs["creationflags"] = creationflags
        return popen(argv, **popen_kwargs)
    except Exception as exc:  # noqa: BLE001 — a launch failure degrades reach, never raises
        LOGGER.warning("public-overlay child failed to launch (%s): %s", argv[:1], exc)
        if handle is not None:
            with suppress(Exception):
                handle.close()
        return None


def launch_public_overlay(
    *,
    trial_id: UUID | str,
    run_dir: Path,
    config: PublicOverlayConfig | None,
    mode: str = "session",
    python_executable: str | None = None,
    popen: Callable[..., subprocess.Popen] = subprocess.Popen,
) -> PublicOverlayHandles:
    """Launch the public overlay app + its tunnel, lifecycle-coupled to the run.

    Operator-gated: when ``config is None`` (no tunnel configured) this is a
    no-op returning ``status="unconfigured"`` — the local HUD is untouched and
    the run proceeds (AC-5). Otherwise it launches TWO children:

    1. the public read-only app (``python -m app.hud.public``) bound to the
       overlay port — a distinct surface with no secret route (AC-1/AC-2);
    2. the NAMED tunnel (:func:`tunnel_argv`) fronting that port (AC-1/AC-3).

    Both spawn windowless on win32 (Story 42.2 AC-7) and register the SAME
    status-aware ``atexit`` teardown as the HUD child (Story 42.2 AC-1/AC-2): a
    gate pause keeps them ALIVE, a terminal status / explicit stop tears them
    down after a grace. NEVER raises (AC-5): any launch fault degrades REACH,
    never the run.
    """
    if config is None:
        return PublicOverlayHandles(status="unconfigured")

    run_dir = Path(run_dir)
    app_env = {
        **os.environ,
        "HUD_TRIAL_ID": str(trial_id),
        "HUD_RUN_DIR": str(run_dir),
        "HUD_PUBLIC_PORT": str(config.public_port),
        "HUD_MODE": mode,
    }
    app_argv = [python_executable or sys.executable, "-m", "app.hud.public"]
    app_proc = _spawn_child(
        app_argv,
        env=app_env,
        log_path=run_dir / "hud-public.log",
        popen=popen,
    )
    if app_proc is None:
        return PublicOverlayHandles(status="app-failed", config=config)
    atexit.register(_status_aware_teardown, app_proc, run_dir)

    public_url = public_overlay_url(config)
    tunnel_proc = _spawn_child(
        tunnel_argv(config),
        # The tunnel child's env carries the ngrok authtoken (if any) via
        # NGROK_AUTHTOKEN — the ONLY place the secret lives (never argv/logs).
        env=_tunnel_child_env(config),
        log_path=run_dir / "hud-tunnel.log",
        popen=popen,
    )
    if tunnel_proc is None:
        # App is up but unreachable from outside — reach degraded, run intact.
        return PublicOverlayHandles(
            status="tunnel-failed",
            app_proc=app_proc,
            config=config,
            public_url=public_url,
        )
    atexit.register(_status_aware_teardown, tunnel_proc, run_dir)
    # Surface the STABLE URL (AC-5): log it + emit a secret-free sentinel the
    # local HUD / operator can read each run. The URL never carries a secret.
    if public_url:
        LOGGER.info(
            "public overlay reachable at %s (mode=%s) for trial %s",
            public_url,
            config.mode,
            trial_id,
        )
        with suppress(Exception):
            (run_dir / HUD_PUBLIC_URL_SENTINEL_NAME).write_text(
                public_url, encoding="utf-8"
            )
    LOGGER.info(
        "launched public overlay (mode=%s, port=%s) for trial %s",
        config.mode,
        config.public_port,
        trial_id,
    )
    return PublicOverlayHandles(
        status="launched",
        app_proc=app_proc,
        tunnel_proc=tunnel_proc,
        config=config,
        public_url=public_url,
    )


__all__ = [
    "COORDINATION_DB_PATH",
    "DEFAULT_PUBLIC_HUD_PORT",
    "HUD_PUBLIC_URL_SENTINEL_NAME",
    "HUD_STOP_SENTINEL_NAME",
    "HUD_TEARDOWN_GRACE_S",
    "PHASE_01_LOCAL_ITEMS",
    "PHASE_02_HEARTBEAT_ITEMS",
    "PUBLIC_OVERLAY_MODES",
    "SOFT_ITEM_NAMES",
    "TERMINAL_RUN_STATUSES",
    "PreflightDeps",
    "PreflightResult",
    "PublicOverlayConfig",
    "PublicOverlayHandles",
    "launch_hud_server",
    "launch_public_overlay",
    "probe_hud_identity",
    "public_overlay_url",
    "reattach_or_launch_hud_server",
    "request_hud_stop",
    "run_preflight",
    "tunnel_argv",
]
