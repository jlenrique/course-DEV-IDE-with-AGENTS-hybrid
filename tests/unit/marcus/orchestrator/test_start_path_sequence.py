"""Start-path pinned-sequence tests (Story 35.3 / AD-7/8/11/12).

Hermetic. Covers: the pinned order (registered projection -> pre-flight ->
walk); pre-flight FAIL blocks the walk BEFORE any specialist dispatch and
leaves the projection at `registered` with a terminal trace event; all-green
proceeds into the walk; offline harness runs skip the live gate; the gate
launches the HUD server BEFORE the heartbeats; and pre-envelope exits
(`cancelled-at-g0` / `saved-only`) leave the projection at `registered` with a
terminal trace event (greenlight amendment 12).
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.orchestrator import preflight as pf
from app.marcus.orchestrator import production_runner as pr
from app.marcus.orchestrator.preflight import PreflightResult
from app.models.runtime.operator_surface import (
    OperatorSurfaceProjection,
    PreflightItem,
    read_operator_surface_lenient,
)


class _StopWalk(Exception):  # noqa: N818 — test sentinel, not a real error type
    """Sentinel raised from a stubbed compile step to prove the walk was entered."""


def _corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "intro.md").write_text("body", encoding="utf-8")
    return corpus


def _proj(runs_root: Path, trial_id) -> OperatorSurfaceProjection:  # noqa: ANN001
    path = runs_root / str(trial_id) / "operator-surface.json"
    parsed = read_operator_surface_lenient(path.read_bytes())
    assert isinstance(parsed, OperatorSurfaceProjection), parsed
    return parsed


# --------------------------------------------------------------------------
# Pre-envelope exits (amendment 12)
# --------------------------------------------------------------------------


def test_emit_registered_and_terminal_trace_lands_registered_plus_trace(
    tmp_path: Path,
) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    pr.emit_registered_and_terminal_trace(
        trial_id,
        runs_root,
        corpus_path=tmp_path / "corpus",
        preset="production",
        operator_id="op",
        event="trial-cancelled-at-g0",
        detail="declined at G0",
    )
    proj = _proj(runs_root, trial_id)
    assert proj.envelope.status == "registered"
    assert proj.trace is not None
    assert any(e.event == "trial-cancelled-at-g0" for e in proj.trace.events)


# --------------------------------------------------------------------------
# Pinned sequence + FAIL-blocks-walk
# --------------------------------------------------------------------------


def test_preflight_fail_blocks_walk_and_leaves_registered_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = _corpus(tmp_path)
    runs_root = tmp_path / "runs"
    trial_id = uuid4()

    fail_item = PreflightItem(name="openai", state="fail", output="boom")
    monkeypatch.setattr(
        pr,
        "_run_start_preflight_gate",
        lambda *a, **k: PreflightResult(all_green=False, items=[fail_item]),
    )
    # The walk must NEVER be entered: compile_run_graph is the first walk step
    # after the gate.
    monkeypatch.setattr(
        pr, "compile_run_graph", lambda *_a, **_k: pytest.fail("walk entered")
    )

    with pytest.raises(pr.PreflightGateFailed):
        pr.run_production_trial(
            corpus_path=corpus,
            preset="production",
            operator_id="op",
            trial_id=trial_id,
            runs_root=runs_root,
            allow_offline_cost_report=False,
            hud="off",
        )

    proj = _proj(runs_root, trial_id)
    assert proj.envelope.status == "registered"  # never went in-flight
    assert proj.trace is not None
    assert any(e.event == "preflight-blocked-spawn" for e in proj.trace.events)


def test_preflight_green_proceeds_into_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = _corpus(tmp_path)
    runs_root = tmp_path / "runs"

    monkeypatch.setattr(
        pr,
        "_run_start_preflight_gate",
        lambda *a, **k: PreflightResult(all_green=True, items=[]),
    )
    monkeypatch.setattr(
        pr, "compile_run_graph", lambda *_a, **_k: (_ for _ in ()).throw(_StopWalk())
    )

    with pytest.raises(_StopWalk):  # got PAST the green gate, into the walk
        pr.run_production_trial(
            corpus_path=corpus,
            preset="production",
            operator_id="op",
            trial_id=uuid4(),
            runs_root=runs_root,
            allow_offline_cost_report=False,
            hud="off",
        )


def test_offline_harness_run_skips_the_live_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = _corpus(tmp_path)
    runs_root = tmp_path / "runs"
    gate_called = {"hit": False}

    def _gate(*_a, **_k):
        gate_called["hit"] = True
        return PreflightResult(all_green=True, items=[])

    monkeypatch.setattr(pr, "_run_start_preflight_gate", _gate)
    monkeypatch.setattr(
        pr, "compile_run_graph", lambda *_a, **_k: (_ for _ in ()).throw(_StopWalk())
    )

    with pytest.raises(_StopWalk):
        pr.run_production_trial(
            corpus_path=corpus,
            preset="production",
            operator_id="op",
            trial_id=uuid4(),
            runs_root=runs_root,
            allow_offline_cost_report=True,  # offline: gate is skipped
            hud="on",
        )
    assert gate_called["hit"] is False


def test_pinned_sequence_order_registered_then_preflight_then_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = _corpus(tmp_path)
    runs_root = tmp_path / "runs"
    order: list[str] = []

    real_persist = pr._persist_envelope

    def _spy_persist(envelope, rr):  # noqa: ANN001
        if envelope.status == "registered":
            order.append("registered-projection")
        return real_persist(envelope, rr)

    def _gate(*_a, **_k):
        order.append("preflight")
        return PreflightResult(all_green=True, items=[])

    def _compile(*_a, **_k):
        order.append("walk")
        raise _StopWalk()

    monkeypatch.setattr(pr, "_persist_envelope", _spy_persist)
    monkeypatch.setattr(pr, "_run_start_preflight_gate", _gate)
    monkeypatch.setattr(pr, "compile_run_graph", _compile)

    with pytest.raises(_StopWalk):
        pr.run_production_trial(
            corpus_path=corpus,
            preset="production",
            operator_id="op",
            trial_id=uuid4(),
            runs_root=runs_root,
            allow_offline_cost_report=False,
            hud="off",
        )

    assert order == ["registered-projection", "preflight", "walk"]


# --------------------------------------------------------------------------
# Gate wiring: server launches BEFORE heartbeats (AD-7)
# --------------------------------------------------------------------------


def test_gate_launches_server_before_running_preflight(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    order: list[str] = []
    captured: dict[str, object] = {}

    class _FakeProc:
        def poll(self) -> None:
            return None

    def _fake_launch_server(**kwargs):  # noqa: ANN003
        order.append("server")
        captured["launch_nonce"] = kwargs["launch_nonce"]
        return _FakeProc()

    def _fake_launch_notifier(*_a, **_k):
        return _FakeProc()

    def _fake_run_preflight(trial_id, runs_root, deps):  # noqa: ANN001
        order.append("preflight")
        captured["deps"] = deps
        return PreflightResult(all_green=True, items=[])

    monkeypatch.setattr(pf, "launch_hud_server", _fake_launch_server)
    monkeypatch.setattr(pf, "run_preflight", _fake_run_preflight)
    import app.notify.__main__ as notify_main

    monkeypatch.setattr(notify_main, "launch_notifier", _fake_launch_notifier)

    trial_id = uuid4()
    result = pr._run_start_preflight_gate(
        trial_id,
        tmp_path / "run",
        tmp_path / "runs",
        hud="on",
        producer_pid=4321,
    )
    assert result.all_green is True
    assert order == ["server", "preflight"]  # server launched before pre-flight
    deps = captured["deps"]
    # A launched server means healthz has a URL + the minted nonce to check.
    assert deps.healthz_url is not None
    assert deps.expected_launch_nonce == captured["launch_nonce"]
    assert deps.expected_trial_id == str(trial_id)


def test_gate_records_healthz_fail_when_server_launch_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    class _FakeProc:
        def poll(self) -> None:
            return None

    monkeypatch.setattr(pf, "launch_hud_server", lambda **_k: None)  # launch fails

    def _fake_run_preflight(trial_id, runs_root, deps):  # noqa: ANN001
        captured["deps"] = deps
        # Exercise the injected healthz_fn the gate builds on launch failure.
        return PreflightResult(all_green=False, items=[deps.healthz_fn()])

    monkeypatch.setattr(pf, "run_preflight", _fake_run_preflight)
    import app.notify.__main__ as notify_main

    monkeypatch.setattr(notify_main, "launch_notifier", lambda *_a, **_k: _FakeProc())

    result = pr._run_start_preflight_gate(
        uuid4(),
        tmp_path / "run",
        tmp_path / "runs",
        hud="on",
        producer_pid=1,
    )
    healthz = next(i for i in result.items if i.name == "hud-server-healthz")
    assert healthz.state == "fail"
    assert "failed to launch" in (healthz.output or "")


def test_hud_off_skips_server_and_notifier_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    launched = {"server": False, "notifier": False}

    def _server(**_k):
        launched["server"] = True
        return None

    monkeypatch.setattr(pf, "launch_hud_server", _server)

    def _fake_run_preflight(trial_id, runs_root, deps):  # noqa: ANN001
        # No server/notifier launched: no healthz url, no notifier item.
        assert deps.healthz_url is None
        assert deps.healthz_fn is None
        assert deps.notifier_alive_fn is None
        return PreflightResult(all_green=True, items=[])

    monkeypatch.setattr(pf, "run_preflight", _fake_run_preflight)

    pr._run_start_preflight_gate(
        uuid4(), tmp_path / "run", tmp_path / "runs", hud="off", producer_pid=1
    )
    assert launched["server"] is False  # --hud off: no launch
