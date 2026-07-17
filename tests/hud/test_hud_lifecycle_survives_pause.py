"""Story 42.2 — HUD lifecycle survives a gate pause + no stray console windows.

Hermetic: every subprocess spawn is an injected fake (``popen=`` seam) and the
``atexit`` registration is captured via monkeypatch, so NO real HUD server, no
real socket, and no real long-lived child is created. Covers:

* AC-1 pause ≠ teardown — a gate pause leaves the child ALIVE.
* AC-2 teardown couples to terminal status + explicit stop, each with a grace.
* AC-3 resume re-attaches (reuse-not-double-launch) via the healthz handshake.
* AC-4 idle honesty — the HUD serves the paused surface / shows offline when idle
  (existing zero-lie render, asserted read-only; unchanged by this story).
* AC-6 NEVER-raises — a lifecycle fault degrades the surface, never the run.
* AC-7 no stray console windows — the HUD-server child spawns with
  ``CREATE_NO_WINDOW`` on win32 (the ergonomics defect this story fixes).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from app.marcus.orchestrator import preflight as pf

_TRIAL = "11111111-1111-4111-8111-111111111111"
_OTHER = "22222222-2222-4222-8222-222222222222"


class _FakeProc:
    """Minimal Popen stand-in with observable terminate/kill/wait lifecycle."""

    def __init__(self, *, alive: bool = True, wait_raises: bool = False) -> None:
        self._alive = alive
        self.terminated = False
        self.killed = False
        self.waited = False
        self._wait_raises = wait_raises

    def poll(self) -> int | None:
        return None if self._alive else 0

    def terminate(self) -> None:
        # A real terminate() only signals; the process may linger until wait/kill.
        self.terminated = True

    def kill(self) -> None:
        self.killed = True
        self._alive = False

    def wait(self, timeout: float | None = None) -> int:
        self.waited = True
        if self._wait_raises:
            raise subprocess.TimeoutExpired(cmd="hud", timeout=timeout or 0.0)
        self._alive = False
        return 0


def _write_status(run_dir: Path, status: str) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps({"status": status}), encoding="utf-8")
    return run_dir


# ---------------------------------------------------------------------------
# AC-7 — no stray console windows on Windows
# ---------------------------------------------------------------------------


def test_launch_hud_server_passes_create_no_window_on_win32(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pf.sys, "platform", "win32")
    # CREATE_NO_WINDOW is absent from subprocess off-Windows; provide it so the
    # helper's getattr resolves the real flag value on any CI host.
    monkeypatch.setattr(pf.subprocess, "CREATE_NO_WINDOW", 0x08000000, raising=False)
    monkeypatch.setattr(pf.atexit, "register", lambda *a, **k: None)
    captured: dict[str, object] = {}

    def _fake_popen(argv, **kwargs):  # noqa: ANN001, ANN003
        captured["kwargs"] = kwargs
        return _FakeProc()

    proc = pf.launch_hud_server(
        trial_id=_TRIAL,
        run_dir=tmp_path / "run",
        launch_nonce="n",
        port=8791,
        popen=_fake_popen,
    )
    assert proc is not None
    assert captured["kwargs"]["creationflags"] == 0x08000000  # type: ignore[index]


def test_launch_hud_server_no_creationflags_off_win32(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pf.sys, "platform", "linux")
    monkeypatch.setattr(pf.atexit, "register", lambda *a, **k: None)
    captured: dict[str, object] = {}

    def _fake_popen(argv, **kwargs):  # noqa: ANN001, ANN003
        captured["kwargs"] = kwargs
        return _FakeProc()

    pf.launch_hud_server(
        trial_id=_TRIAL,
        run_dir=tmp_path / "run",
        launch_nonce="n",
        port=8791,
        popen=_fake_popen,
    )
    assert "creationflags" not in captured["kwargs"]  # POSIX path untouched


def test_no_window_creationflags_is_zero_off_win32(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(pf.sys, "platform", "darwin")
    assert pf._no_window_creationflags() == 0


# ---------------------------------------------------------------------------
# AC-1 — launch couples teardown to the RUN (status-aware), not the CLI process
# ---------------------------------------------------------------------------


def test_launch_registers_status_aware_teardown_with_run_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The atexit hook is the status-aware teardown (not a blind terminate),
    and it is handed the run_dir so it can read the run status at exit."""
    registered: list[tuple] = []
    monkeypatch.setattr(
        pf.atexit, "register", lambda fn, *a, **k: registered.append((fn, a))
    )
    run_dir = tmp_path / "run"
    proc = pf.launch_hud_server(
        trial_id=_TRIAL,
        run_dir=run_dir,
        launch_nonce="n",
        port=8791,
        popen=lambda argv, **k: _FakeProc(),
    )
    assert len(registered) == 1
    fn, args = registered[0]
    assert fn is pf._status_aware_teardown
    assert args[0] is proc
    assert Path(args[1]) == run_dir


def test_teardown_noop_on_gate_pause_leaves_child_alive(tmp_path: Path) -> None:
    run_dir = _write_status(tmp_path / "run", "paused-at-gate")
    proc = _FakeProc(alive=True)
    pf._status_aware_teardown(proc, run_dir, grace=0.01)
    assert proc.poll() is None  # still LISTENING across the pause
    assert proc.terminated is False


def test_teardown_noop_on_paused_at_error_leaves_child_alive(tmp_path: Path) -> None:
    run_dir = _write_status(tmp_path / "run", "paused-at-error")
    proc = _FakeProc(alive=True)
    pf._status_aware_teardown(proc, run_dir, grace=0.01)
    assert proc.poll() is None
    assert proc.terminated is False


def test_teardown_noop_when_status_unknown(tmp_path: Path) -> None:
    """No run.json (or unreadable) → status None → safe default is LEAVE ALIVE."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    proc = _FakeProc(alive=True)
    pf._status_aware_teardown(proc, run_dir, grace=0.01)
    assert proc.terminated is False


# ---------------------------------------------------------------------------
# AC-2 — teardown on terminal status OR explicit stop, each with a grace
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", ["completed", "failed"])
def test_teardown_terminates_with_grace_on_terminal_status(
    tmp_path: Path, status: str
) -> None:
    run_dir = _write_status(tmp_path / "run", status)
    proc = _FakeProc(alive=True)
    pf._status_aware_teardown(proc, run_dir, grace=0.01)
    assert proc.terminated is True
    assert proc.waited is True  # a grace window was honored
    assert proc.killed is False  # graceful exit, no hard kill needed
    assert proc.poll() is not None


def test_teardown_hard_kills_after_grace_timeout(tmp_path: Path) -> None:
    run_dir = _write_status(tmp_path / "run", "completed")
    proc = _FakeProc(alive=True, wait_raises=True)
    pf._status_aware_teardown(proc, run_dir, grace=0.01)
    assert proc.terminated is True
    assert proc.killed is True  # grace elapsed → escalate to kill


def test_explicit_stop_tears_down_even_while_paused(tmp_path: Path) -> None:
    run_dir = _write_status(tmp_path / "run", "paused-at-gate")
    pf.request_hud_stop(run_dir)  # operator stop overrides the non-terminal status
    proc = _FakeProc(alive=True)
    pf._status_aware_teardown(proc, run_dir, grace=0.01)
    assert proc.terminated is True


def test_request_hud_stop_writes_sentinel_and_is_idempotent(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    pf.request_hud_stop(run_dir)
    pf.request_hud_stop(run_dir)  # idempotent
    assert (run_dir / pf.HUD_STOP_SENTINEL_NAME).exists()


def test_teardown_noop_when_child_already_dead(tmp_path: Path) -> None:
    run_dir = _write_status(tmp_path / "run", "completed")
    proc = _FakeProc(alive=False)
    pf._status_aware_teardown(proc, run_dir, grace=0.01)
    assert proc.terminated is False  # already gone → nothing to do


# ---------------------------------------------------------------------------
# AC-6 — NEVER raises: a lifecycle fault degrades the surface, never the run
# ---------------------------------------------------------------------------


def test_teardown_never_raises_on_proc_fault(tmp_path: Path) -> None:
    class _ExplodingProc:
        def poll(self):  # noqa: ANN202
            raise RuntimeError("boom")

    # Must not propagate — swallowed at exit.
    pf._status_aware_teardown(_ExplodingProc(), tmp_path / "run", grace=0.01)


def test_request_hud_stop_never_raises_on_bad_path() -> None:
    # A NUL byte makes an impossible path; request_hud_stop must swallow it.
    pf.request_hud_stop(Path("\x00impossible"))


def test_read_run_status_never_raises_on_corrupt_json(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "run.json").write_text("{not json", encoding="utf-8")
    assert pf._read_run_status(run_dir) is None


def test_read_run_status_falls_back_to_projection(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    # No run.json; the operator-surface projection carries the nested status.
    (run_dir / "operator-surface.json").write_text(
        json.dumps({"envelope": {"status": "completed"}}), encoding="utf-8"
    )
    assert pf._read_run_status(run_dir) == "completed"


# ---------------------------------------------------------------------------
# AC-3 — resume re-attaches, does not double-launch
# ---------------------------------------------------------------------------


def test_reattach_reuses_live_hud_for_same_trial_no_double_launch(
    tmp_path: Path,
) -> None:
    launched: list = []

    def _popen(argv, **kwargs):  # noqa: ANN001, ANN003
        launched.append(argv)
        return _FakeProc()

    proc, action = pf.reattach_or_launch_hud_server(
        trial_id=_TRIAL,
        run_dir=tmp_path / "run",
        launch_nonce="fresh",
        port=8791,
        popen=_popen,
        probe=lambda: (pf._canonical_trial_id(_TRIAL), "old-nonce"),
    )
    assert action == "reused"
    assert proc is None
    assert launched == []  # NOT a second HUD — the live one is reused


def test_reattach_launches_when_port_is_free(tmp_path: Path) -> None:
    launched: list = []

    def _popen(argv, **kwargs):  # noqa: ANN001, ANN003
        launched.append(argv)
        return _FakeProc()

    proc, action = pf.reattach_or_launch_hud_server(
        trial_id=_TRIAL,
        run_dir=tmp_path / "run",
        launch_nonce="fresh",
        port=8791,
        popen=_popen,
        probe=lambda: None,  # nothing healthy answers
    )
    assert action == "launched"
    assert proc is not None
    assert len(launched) == 1


def test_reattach_does_not_reuse_a_foreign_trial_on_port(tmp_path: Path) -> None:
    launched: list = []

    def _popen(argv, **kwargs):  # noqa: ANN001, ANN003
        launched.append(argv)
        return _FakeProc()

    proc, action = pf.reattach_or_launch_hud_server(
        trial_id=_TRIAL,
        run_dir=tmp_path / "run",
        launch_nonce="fresh",
        port=8791,
        popen=_popen,
        probe=lambda: (pf._canonical_trial_id(_OTHER), "n"),
    )
    # Foreign identity on the port → fresh launch (pre-flight healthz then
    # catches the genuine wrong-server-on-port conflict, AD-8).
    assert action == "launched"
    assert len(launched) == 1


def test_reattach_never_raises_when_probe_faults(tmp_path: Path) -> None:
    def _bad_probe():
        raise RuntimeError("probe boom")

    proc, action = pf.reattach_or_launch_hud_server(
        trial_id=_TRIAL,
        run_dir=tmp_path / "run",
        launch_nonce="fresh",
        port=8791,
        popen=lambda argv, **k: _FakeProc(),
        probe=_bad_probe,
    )
    assert action == "launched"  # a faulting probe degrades to a fresh launch


def test_probe_hud_identity_returns_none_on_connection_error() -> None:
    def _boom(url, timeout=None):  # noqa: ANN001, ANN202
        raise pf.httpx.ConnectError("refused")

    assert pf.probe_hud_identity(8791, get=_boom) is None


def test_probe_hud_identity_returns_identity_on_200() -> None:
    class _Resp:
        status_code = 200

        def json(self):  # noqa: ANN202
            return {"trial_id": _TRIAL, "launch_nonce": "n"}

    result = pf.probe_hud_identity(8791, get=lambda u, timeout=None: _Resp())
    assert result == (pf._canonical_trial_id(_TRIAL), "n")


def test_probe_hud_identity_returns_none_on_non_200() -> None:
    class _Resp:
        status_code = 503

        def json(self):  # noqa: ANN202
            return {}

    assert pf.probe_hud_identity(8791, get=lambda u, timeout=None: _Resp()) is None


# ---------------------------------------------------------------------------
# AC-4 — idle honesty: HUD serves the paused surface / shows offline when idle
# (existing zero-lie render — asserted read-only; this story does not change it)
# ---------------------------------------------------------------------------


def test_hud_render_serves_paused_surface_and_offline_when_idle() -> None:
    from app.hud.render.page import _annunciator_parts

    # Between pause and resume the HUD serves the live paused surface.
    _cls, _sym, text = _annunciator_parts(
        {"panel_state": "live", "envelope": {"paused_gate": "G0E"}, "status": "paused-at-gate"}
    )
    assert "PAUSED AT GATE G0E" in text

    # When no run is bound it honestly says so (idle).
    _cls2, _sym2, idle_text = _annunciator_parts({"panel_state": "no-active-run"})
    assert "NO ACTIVE RUN" in idle_text
