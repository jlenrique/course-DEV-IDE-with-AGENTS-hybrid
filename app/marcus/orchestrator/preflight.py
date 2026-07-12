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
  ``HUD_MODE``), registers an ``atexit`` terminate, and NEVER raises: a launch
  failure returns ``None`` so the caller records a pre-flight FAIL instead
  (AD-7: a child bind failure is a pre-flight FAIL, never a fall-through).

Live calls (OpenAI, Gamma, the healthz identity probe) are injectable seams so
unit tests run hermetic with fakes; the real defaults do real network calls
(NFR5: no mocks in the live legs). The v1 heartbeat set is OpenAI + Gamma +
LangSmith-env-presence only (greenlight amendment 10); more platforms accrete
under the AD-13 falter-surface regression rule.
"""

from __future__ import annotations

import atexit
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


def _terminate_quietly(proc: subprocess.Popen) -> None:
    with suppress(Exception):
        if proc.poll() is None:
            proc.terminate()


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
    fall-through to whatever else answers the port). Registers an ``atexit``
    terminate so the child dies with the runtime session (AD-7 lifecycle).
    ``popen`` is injectable so unit tests never spawn a real process.
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
        proc = popen(
            argv,
            env=env,
            stdout=handle,
            stderr=handle,
            stdin=subprocess.DEVNULL,
        )
    except Exception as exc:  # noqa: BLE001 — launch failure is a FAIL, never a raise
        LOGGER.exception("HUD server child failed to launch: %s", exc)
        if handle is not None:
            with suppress(Exception):
                handle.close()
        return None
    atexit.register(_terminate_quietly, proc)
    LOGGER.info("launched HUD server child for trial %s on port %s", trial_id, port)
    return proc


__all__ = [
    "COORDINATION_DB_PATH",
    "PHASE_01_LOCAL_ITEMS",
    "PHASE_02_HEARTBEAT_ITEMS",
    "SOFT_ITEM_NAMES",
    "PreflightDeps",
    "PreflightResult",
    "launch_hud_server",
    "run_preflight",
]
