"""Unit tests for the start-path pre-flight executor (Story 35.3 / AD-7/8/11).

Hermetic: every live call (OpenAI, Gamma, the healthz identity probe) is an
injectable seam replaced with a fake here. The `live`-marked integration test
at the bottom does the REAL calls (NFR5) and is excluded by the xdist default.

Covers: per-item projection writes; ordered item set; missed != fail (both gate,
distinct states); soft coordination-db never gates; wrong-server-on-port healthz
FAIL; healthz identity match PASS; launch-failure -> None never raises.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.marcus.orchestrator import preflight as pf
from app.marcus.orchestrator.operator_surface_assembler import OperatorSurfaceAssembler
from app.marcus.orchestrator.preflight import (
    PreflightDeps,
    launch_hud_server,
    run_preflight,
)
from app.models.runtime.operator_surface import (
    OperatorSurfaceProjection,
    PreflightItem,
    read_operator_surface_lenient,
)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


class _StubEnvelope:
    """Minimal registered envelope: the fields emit() reads + model_dump_json."""

    def __init__(self, trial_id: UUID) -> None:
        self.trial_id = trial_id
        self.status = "registered"
        self.paused_gate = None
        self.paused_error_tag = None
        self.waiting_batch_id = None
        self.completed_at = None
        self.corpus_path = "lesson-alpha"
        self.preset = "production"
        self.operator_id = "operator_cli"

    def model_dump_json(self, indent: int = 2) -> str:
        return json.dumps({"trial_id": str(self.trial_id)}, indent=indent, sort_keys=True)


def _seed_registered(trial_id: UUID, runs_root: Path) -> OperatorSurfaceAssembler:
    """Establish a registered projection so update_preflight_item has a base."""
    assembler = OperatorSurfaceAssembler(trial_id, runs_root)
    assembler.emit(_StubEnvelope(trial_id))
    return assembler


def _pass_deps(**overrides: object) -> PreflightDeps:
    """Deps whose heartbeats all PASS and whose local env keys are present."""
    base = {
        "env": {
            "OPENAI_API_KEY": "sk-test",
            "LANGSMITH_API_KEY": "ls-test",
            "LANGSMITH_PROJECT": "proj",
        },
        # A coordination.db that exists so the soft item is a clean PASS unless
        # a test overrides it.
        "openai_heartbeat_fn": lambda: PreflightItem(
            name="openai", state="pass", latency_ms=12.0, quota_confidence="proxy"
        ),
        "gamma_heartbeat_fn": lambda: PreflightItem(
            name="gamma", state="pass", latency_ms=9.0, quota_confidence="proxy"
        ),
    }
    base.update(overrides)
    return PreflightDeps(**base)  # type: ignore[arg-type]


def _read(runs_root: Path, trial_id: UUID) -> OperatorSurfaceProjection:
    path = runs_root / str(trial_id) / "operator-surface.json"
    parsed = read_operator_surface_lenient(path.read_bytes())
    assert isinstance(parsed, OperatorSurfaceProjection), parsed
    return parsed


# --------------------------------------------------------------------------
# run_preflight — item set, ordering, projection writes
# --------------------------------------------------------------------------


def test_all_green_when_every_non_soft_item_passes(tmp_path: Path) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    # Point the soft coordination-db at an existing sqlite file so it PASSES.
    db = tmp_path / "coordination.db"
    import sqlite3

    sqlite3.connect(db).close()
    result = run_preflight(
        trial_id, runs_root, _pass_deps(coordination_db_path=db)
    )
    assert result.all_green is True
    assert result.blocking_items() == []


def test_each_item_is_written_into_the_projection_as_it_completes(
    tmp_path: Path,
) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    result = run_preflight(trial_id, runs_root, _pass_deps())

    proj = _read(runs_root, trial_id)
    assert proj.preflight is not None
    projected = {item.name for item in proj.preflight.items}
    # Phase-01 locals + phase-02 heartbeats all landed in the projection.
    assert {
        "env-keys-present",
        "runs-root-writable",
        "coordination-db-readable",
        "litellm-importable",
        "cascade-config-validates",
        "openai",
        "gamma",
        "langsmith",
    } <= projected
    # The in-memory result mirrors what was projected.
    assert {i.name for i in result.items} == projected


def test_missed_is_not_fail_but_both_break_green(tmp_path: Path) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    # openai heartbeat MISSED (env absent style), gamma PASS.
    deps = _pass_deps(
        openai_heartbeat_fn=lambda: PreflightItem(
            name="openai", state="missed", output="OPENAI_API_KEY absent"
        )
    )
    result = run_preflight(trial_id, runs_root, deps)

    openai = next(i for i in result.items if i.name == "openai")
    assert openai.state == "missed"  # distinct alarm, NOT coerced to "fail"
    assert result.all_green is False  # ... but a missed non-soft item still gates
    blocking = {i.name for i in result.blocking_items()}
    assert "openai" in blocking


def test_soft_coordination_db_missing_does_not_block_green(tmp_path: Path) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    missing_db = tmp_path / "does-not-exist.db"
    result = run_preflight(
        trial_id, runs_root, _pass_deps(coordination_db_path=missing_db)
    )
    coord = next(i for i in result.items if i.name == "coordination-db-readable")
    assert coord.state == "missed"  # soft item records honestly
    assert result.all_green is True  # ... but never gates spawn
    assert "coordination-db-readable" not in {i.name for i in result.blocking_items()}


def test_env_keys_missing_is_a_hard_fail(tmp_path: Path) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    deps = _pass_deps(env={"LANGSMITH_API_KEY": "ls"})  # OPENAI_API_KEY absent
    result = run_preflight(trial_id, runs_root, deps)
    env_item = next(i for i in result.items if i.name == "env-keys-present")
    assert env_item.state == "fail"
    assert "OPENAI_API_KEY" in (env_item.output or "")
    assert result.all_green is False


def test_langsmith_env_presence_pass_and_missed(tmp_path: Path) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    # present -> pass
    present = run_preflight(trial_id, runs_root, _pass_deps())
    ls = next(i for i in present.items if i.name == "langsmith")
    assert ls.state == "pass"
    # absent -> missed (env has no LANGSMITH_API_KEY); env-keys also fails, but
    # the langsmith heartbeat itself is `missed`, not `fail`.
    trial2 = uuid4()
    _seed_registered(trial2, runs_root)
    absent = run_preflight(
        trial2, runs_root, _pass_deps(env={"OPENAI_API_KEY": "sk"})
    )
    ls2 = next(i for i in absent.items if i.name == "langsmith")
    assert ls2.state == "missed"


def test_notifier_alive_item_included_when_fn_present(tmp_path: Path) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    result = run_preflight(
        trial_id, runs_root, _pass_deps(notifier_alive_fn=lambda: False)
    )
    notifier = next(i for i in result.items if i.name == "notifier-process-alive")
    assert notifier.state == "fail"
    assert result.all_green is False


# --------------------------------------------------------------------------
# healthz identity probe (AD-7/AD-8) — wrong-server-on-port
# --------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, payload: dict[str, object], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.headers: dict[str, str] = {}

    def json(self) -> dict[str, object]:
        return self._payload


def test_healthz_passes_on_identity_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = uuid4()
    nonce = "nonce-abc"
    monkeypatch.setattr(
        pf.httpx,
        "get",
        lambda *a, **k: _FakeResponse(
            {"trial_id": str(trial_id), "launch_nonce": nonce, "mode": "session"}
        ),
    )
    deps = PreflightDeps(
        healthz_url="http://127.0.0.1:8791/healthz",
        expected_trial_id=str(trial_id),
        expected_launch_nonce=nonce,
    )
    item = pf._default_healthz_item(deps)
    assert item.state == "pass"
    assert item.latency_ms is not None


def test_healthz_fails_wrong_server_on_port(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A different server answering the port (200, foreign identity) => FAIL."""
    bound_id = uuid4()
    other_id = uuid4()
    monkeypatch.setattr(
        pf.httpx,
        "get",
        lambda *a, **k: _FakeResponse(
            {"trial_id": str(other_id), "launch_nonce": "someone-else", "mode": "session"}
        ),
    )
    deps = PreflightDeps(
        healthz_url="http://127.0.0.1:8791/healthz",
        expected_trial_id=str(bound_id),
        expected_launch_nonce="my-nonce",
    )
    item = pf._default_healthz_item(deps)
    assert item.state == "fail"
    assert "wrong-server-on-port" in (item.output or "")


def test_healthz_nonce_mismatch_same_trial_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trial_id = uuid4()
    monkeypatch.setattr(
        pf.httpx,
        "get",
        lambda *a, **k: _FakeResponse(
            {"trial_id": str(trial_id), "launch_nonce": "STALE", "mode": "session"}
        ),
    )
    deps = PreflightDeps(
        healthz_url="http://127.0.0.1:8791/healthz",
        expected_trial_id=str(trial_id),
        expected_launch_nonce="FRESH",
    )
    assert pf._default_healthz_item(deps).state == "fail"


def test_healthz_item_wired_into_run_preflight(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    monkeypatch.setattr(
        pf.httpx,
        "get",
        lambda *a, **k: _FakeResponse(
            {"trial_id": str(trial_id), "launch_nonce": "N", "mode": "session"}
        ),
    )
    deps = _pass_deps(
        healthz_url="http://127.0.0.1:8791/healthz",
        expected_trial_id=str(trial_id),
        expected_launch_nonce="N",
    )
    result = run_preflight(trial_id, runs_root, deps)
    healthz = next(i for i in result.items if i.name == "hud-server-healthz")
    assert healthz.state == "pass"


# --------------------------------------------------------------------------
# launch_hud_server — env contract + launch-failure never raises
# --------------------------------------------------------------------------


def test_launch_hud_server_sets_env_contract(tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def _fake_popen(argv, **kwargs):  # noqa: ANN001
        captured["argv"] = argv
        captured["env"] = kwargs["env"]

        class _P:
            def poll(self) -> None:
                return None

            def terminate(self) -> None:  # pragma: no cover
                return None

        return _P()

    run_dir = tmp_path / "run"
    proc = launch_hud_server(
        trial_id="11111111-1111-4111-8111-111111111111",
        run_dir=run_dir,
        launch_nonce="nonce-xyz",
        port=8791,
        popen=_fake_popen,
    )
    assert proc is not None
    env = captured["env"]
    assert env["HUD_TRIAL_ID"] == "11111111-1111-4111-8111-111111111111"
    assert env["HUD_RUN_DIR"] == str(run_dir)
    assert env["HUD_LAUNCH_NONCE"] == "nonce-xyz"
    assert env["HUD_PORT"] == "8791"
    assert env["HUD_MODE"] == "session"
    assert captured["argv"][1:] == ["-m", "app.hud.server"]


def test_launch_hud_server_returns_none_never_raises_on_failure(
    tmp_path: Path,
) -> None:
    def _boom(argv, **kwargs):  # noqa: ANN001
        raise OSError("cannot spawn")

    proc = launch_hud_server(
        trial_id="11111111-1111-4111-8111-111111111111",
        run_dir=tmp_path / "run",
        launch_nonce="n",
        port=8791,
        popen=_boom,
    )
    assert proc is None  # a launch failure is a FAIL item upstream, not a raise


# --------------------------------------------------------------------------
# L3 LIVE — real OpenAI + Gamma heartbeats (NFR5). Excluded by xdist default.
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_heartbeats_real_calls(tmp_path: Path) -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY absent; live heartbeat test requires real keys")
    trial_id = uuid4()
    runs_root = tmp_path / "runs"
    _seed_registered(trial_id, runs_root)
    deps = PreflightDeps(env=dict(os.environ))
    result = run_preflight(trial_id, runs_root, deps)
    openai = next(i for i in result.items if i.name == "openai")
    assert openai.state in ("pass", "fail")  # real reachability, no mock
    assert openai.latency_ms is not None
