"""Story 42.6 (rider R1) — G0S per-run WAKE SENTINEL (default-ON for operator runs).

42.5 shipped the pre-walk settings confirm gate (G0S) woken ONLY by the env flag
``MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE`` (default OFF ⇒ traversed byte-identically).
42.6 adds a per-run WAKE SENTINEL so the operator CLI start path defaults the gate
ON WITHOUT the ``os.environ.setdefault`` leak that would push the pause into the
~13 direct ``start_trial`` test callers.

These are WALK / helper tests exercised against the shared runner functions with a
fake adapter + stubbed preflight/cost — hermetic, no live LLM, no network, no
windows. The env flag is NOT set here (that is the 42.5 test's job); the sentinel
alone must wake the gate, and OR semantics with the env flag are pinned explicitly.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest

from app.marcus.orchestrator import package_builders
from app.marcus.orchestrator import production_runner as pr
from app.models.runtime import ProductionEnvelope, SpecialistContribution

_CORPUS = Path("tests/fixtures/trial_corpus/README.md")
_OPERATOR = "operator_test"

# Same trimmed manifest shape as the 42.5 walk test: G0S at the HEAD, then a single
# `cd` @ 4.75 specialist so "proceeding past the settings gate" dispatches exactly
# one specialist and completes.
_CD_ONLY_MANIFEST_YAML = textwrap.dedent(
    """
    schema_version: "1.0"
    lane: "run_graph"
    entrypoint: "pre-walk-settings-gate"
    frozen_graph_version: "v42"
    nodes:
      - id: "pre-walk-settings-gate"
        specialist_id: null
        gate: true
        gate_code: "G0S"
      - id: "4.75"
        specialist_id: "cd"
    edges:
      - from: "__start__"
        to: "pre-walk-settings-gate"
      - from: "pre-walk-settings-gate"
        to: "4.75"
      - from: "4.75"
        to: "__end__"
    """
).lstrip()


class _SpyAdapter:
    """Deterministic dispatcher that records every specialist it dispatches."""

    def __init__(self) -> None:
        self.dispatched: list[str] = []

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict,
        cost_usd: float,
        base_state=None,
        node_id: str | None = None,
        runner_supplied_payload: dict | None = None,
        projection_map: dict | None = None,
    ) -> ProductionEnvelope:
        del dependency_map, base_state, runner_supplied_payload, projection_map, cost_usd
        self.dispatched.append(specialist_id)
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={"specialist_id": specialist_id},
                model_used=package_builders.BUILDER_MODEL_MARKER,
                cost_usd=0.0,
                node_id=node_id,
            )
        )
        return updated


def _prep(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, _SpyAdapter]:
    """Prepare a hermetic runner WITHOUT setting the G0S env wake flag.

    The env flag is deliberately left UNSET (delete any ambient value) so the
    sentinel is the sole wake signal under test.
    """
    mp = tmp_path / "manifest.yaml"
    mp.write_text(_CD_ONLY_MANIFEST_YAML, encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv(pr.PREWALK_SETTINGS_CONFIRM_ACTIVE_ENV, raising=False)
    monkeypatch.setenv("MARCUS_TRIAL_BUDGET_USD", "0")
    monkeypatch.setenv("MARCUS_RESEARCH_DISPATCH_LIVE", "on")
    spy = _SpyAdapter()
    monkeypatch.setattr(pr, "ProductionDispatchAdapter", lambda: spy)
    monkeypatch.setattr(
        pr,
        "_run_start_preflight_gate",
        lambda *a, **k: SimpleNamespace(all_green=True, blocking_items=lambda: []),
    )
    monkeypatch.setattr(pr, "_record_cost", lambda **_k: tmp_path / "cost-report.json")
    return mp, spy


def _start(tmp_path: Path, mp: Path, trial_id: UUID, **kwargs):
    return pr.run_production_trial(
        _CORPUS,
        "production",
        _OPERATOR,
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=mp,
        **kwargs,
    )


# --------------------------------------------------------------------------- #
# AC-1 — the per-run sentinel wakes G0S (start walk).
# --------------------------------------------------------------------------- #


def test_ac1_sentinel_present_wakes_and_pauses_start_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("11111111-1111-4111-8111-111111111111")
    mp, spy = _prep(tmp_path, monkeypatch)
    # Write the per-run sentinel into the run dir (what the operator CLI start path
    # does by default) — NO env flag set.
    pr.write_prewalk_settings_confirm_sentinel(tmp_path / str(trial_id))

    envelope = _start(tmp_path, mp, trial_id)

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == pr.PRE_WALK_SETTINGS_GATE_ID
    assert spy.dispatched == []  # nothing spent at the pre-walk pause


def test_ac3_sentinel_absent_and_env_unset_is_dormant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No sentinel + no env flag ⇒ G0S dormant ⇒ the walk traverses it and runs
    (byte-identical to the 42.5 default-OFF behavior — the ~13 direct start_trial
    test callers rely on exactly this)."""
    trial_id = UUID("22222222-2222-4222-8222-222222222222")
    mp, spy = _prep(tmp_path, monkeypatch)
    # No sentinel written.
    assert not (tmp_path / str(trial_id) / pr.PREWALK_SETTINGS_CONFIRM_SENTINEL_NAME).exists()

    envelope = _start(tmp_path, mp, trial_id)

    assert envelope.paused_gate != pr.PRE_WALK_SETTINGS_GATE_ID
    assert envelope.status == "completed"
    assert "cd" in spy.dispatched


def test_ac1_env_flag_still_wakes_or_semantics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """OR semantics: the env flag ALONE (no sentinel) still wakes G0S — the 42.5
    override path is preserved (fence: NO removal of the env flag)."""
    trial_id = UUID("33333333-3333-4333-8333-333333333333")
    mp, spy = _prep(tmp_path, monkeypatch)
    monkeypatch.setenv(pr.PREWALK_SETTINGS_CONFIRM_ACTIVE_ENV, "1")
    assert not (tmp_path / str(trial_id) / pr.PREWALK_SETTINGS_CONFIRM_SENTINEL_NAME).exists()

    envelope = _start(tmp_path, mp, trial_id)

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == pr.PRE_WALK_SETTINGS_GATE_ID
    assert spy.dispatched == []


# --------------------------------------------------------------------------- #
# AC-1 both-walk parity — the shared disposition helper reads the run-dir sentinel
# identically for the start walk AND the continuation walk (it computes run_dir the
# same way from trial_id + runs_root, so pinning the helper pins both walks).
# --------------------------------------------------------------------------- #


def test_ac1_disposition_reads_sentinel_from_run_dir_both_walks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("44444444-4444-4444-8444-444444444444")
    monkeypatch.delenv(pr.PREWALK_SETTINGS_CONFIRM_ACTIVE_ENV, raising=False)
    run_dir = tmp_path / str(trial_id)

    # Absent ⇒ traverse (both walks).
    assert (
        pr._prewalk_settings_gate_disposition(
            trial_id=trial_id,
            runs_root=tmp_path,
            pause_at_gates=True,
            allow_offline_cost_report=False,
        )
        == "traverse"
    )
    # Present ⇒ pause (both walks; the continuation walk passes pause_at_gates=True).
    pr.write_prewalk_settings_confirm_sentinel(run_dir)
    assert (
        pr._prewalk_settings_gate_disposition(
            trial_id=trial_id,
            runs_root=tmp_path,
            pause_at_gates=True,
            allow_offline_cost_report=False,
        )
        == "pause"
    )


def test_wake_check_or_semantics_unit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The run_dir-aware wake check: env OR sentinel; env-only overload for callers
    without a run dir."""
    monkeypatch.delenv(pr.PREWALK_SETTINGS_CONFIRM_ACTIVE_ENV, raising=False)
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    assert pr._prewalk_settings_confirm_active(run_dir) is False
    assert pr._prewalk_settings_confirm_active(None) is False  # env-only overload

    # Sentinel alone wakes.
    pr.write_prewalk_settings_confirm_sentinel(run_dir)
    assert pr._prewalk_settings_confirm_active(run_dir) is True
    # ...but the env-only overload (no run dir) still sees only the env.
    assert pr._prewalk_settings_confirm_active(None) is False

    # Env alone wakes regardless of run dir.
    monkeypatch.setenv(pr.PREWALK_SETTINGS_CONFIRM_ACTIVE_ENV, "yes")
    assert pr._prewalk_settings_confirm_active(None) is True
    assert pr._prewalk_settings_confirm_active(tmp_path / "no-sentinel-here") is True


# --------------------------------------------------------------------------- #
# AC-4 — opt-out honesty preserved: offline / non-interactive with the sentinel
# present still SKIP the pause explicitly + traced (never a silent skip).
# --------------------------------------------------------------------------- #


def test_ac4_offline_with_sentinel_skips_explicitly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("55555555-5555-4555-8555-555555555555")
    mp, _ = _prep(tmp_path, monkeypatch)
    pr.write_prewalk_settings_confirm_sentinel(tmp_path / str(trial_id))

    envelope = _start(tmp_path, mp, trial_id, allow_offline_cost_report=True)

    assert envelope.paused_gate != pr.PRE_WALK_SETTINGS_GATE_ID
    surface = json.loads(
        (tmp_path / str(trial_id) / "operator-surface.json").read_text(encoding="utf-8")
    )
    events = [e["event"] for e in (surface.get("trace") or {}).get("events", [])]
    assert "prewalk-settings-skipped" in events


def test_ac4_non_interactive_with_sentinel_skips_explicitly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("66666666-6666-4666-8666-666666666666")
    mp, _ = _prep(tmp_path, monkeypatch)
    pr.write_prewalk_settings_confirm_sentinel(tmp_path / str(trial_id))

    envelope = _start(tmp_path, mp, trial_id, pause_at_gates=False)

    assert envelope.paused_gate != pr.PRE_WALK_SETTINGS_GATE_ID
    surface = json.loads(
        (tmp_path / str(trial_id) / "operator-surface.json").read_text(encoding="utf-8")
    )
    events = [e["event"] for e in (surface.get("trace") or {}).get("events", [])]
    assert "prewalk-settings-skipped" in events


# --------------------------------------------------------------------------- #
# AC-2 — start_trial writes the sentinel iff prewalk_settings_confirm=True (the
# function default is OFF, which is why the ~13 direct callers stay deterministic).
# --------------------------------------------------------------------------- #


def _stub_runner(monkeypatch: pytest.MonkeyPatch, captured: dict) -> None:
    from app.marcus.cli import trial as trial_cli

    def _fake_run(**kwargs):
        rd = kwargs["runs_root"] / str(kwargs["trial_id"])
        captured["sentinel_at_walk"] = (
            rd / pr.PREWALK_SETTINGS_CONFIRM_SENTINEL_NAME
        ).exists()
        rd.mkdir(parents=True, exist_ok=True)  # the real runner materializes the run dir
        return SimpleNamespace(
            status="registered-offline",
            cost_report_path=None,
            production_clone_launch_evidence=False,
        )

    monkeypatch.setattr(trial_cli, "run_production_trial", _fake_run)


def test_ac2_start_trial_writes_sentinel_when_true(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.marcus.cli import trial as trial_cli

    captured: dict = {}
    _stub_runner(monkeypatch, captured)
    trial_id = UUID("77777777-7777-4777-8777-777777777777")

    trial_cli.start_trial(
        preset="production",
        input_path=_CORPUS,
        operator_id=_OPERATOR,
        trial_id=trial_id,
        runs_root=tmp_path,
        allow_offline_cost_report=True,
        prewalk_settings_confirm=True,
    )

    assert captured["sentinel_at_walk"] is True
    assert (tmp_path / str(trial_id) / pr.PREWALK_SETTINGS_CONFIRM_SENTINEL_NAME).exists()


def test_ac3_start_trial_default_off_writes_no_sentinel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The function default (OFF) writes NO sentinel — this is the whole reason the
    ~13 direct start_trial test callers stay deterministic (G0S dormant)."""
    from app.marcus.cli import trial as trial_cli

    captured: dict = {}
    _stub_runner(monkeypatch, captured)
    trial_id = UUID("88888888-8888-4888-8888-888888888888")

    # No prewalk_settings_confirm kwarg ⇒ function default OFF.
    trial_cli.start_trial(
        preset="production",
        input_path=_CORPUS,
        operator_id=_OPERATOR,
        trial_id=trial_id,
        runs_root=tmp_path,
        allow_offline_cost_report=True,
    )

    assert captured["sentinel_at_walk"] is False
    assert not (
        tmp_path / str(trial_id) / pr.PREWALK_SETTINGS_CONFIRM_SENTINEL_NAME
    ).exists()


# --------------------------------------------------------------------------- #
# AC-2 / AC-5 — the CLI flag defaults ON (writes the sentinel) and
# --no-prewalk-settings-confirm opts out (writes nothing).
# --------------------------------------------------------------------------- #


def _parse_start(argv: list[str]):
    import argparse

    from app.marcus.cli import trial as trial_cli

    parser = argparse.ArgumentParser()
    trial_cli.build_trial_parser(parser)
    return parser.parse_args(argv)


def test_ac5_cli_flag_defaults_on() -> None:
    args = _parse_start(["start", "--input", str(_CORPUS)])
    assert args.prewalk_settings_confirm is True


def test_ac5_cli_no_flag_opts_out() -> None:
    args = _parse_start(
        ["start", "--input", str(_CORPUS), "--no-prewalk-settings-confirm"]
    )
    assert args.prewalk_settings_confirm is False


def test_ac2_start_trial_cli_threads_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """start_trial_cli passes the Namespace flag straight through to start_trial."""
    from app.marcus.cli import trial as trial_cli

    captured: dict = {}

    def _fake_start_trial(**kwargs):
        captured["prewalk_settings_confirm"] = kwargs.get("prewalk_settings_confirm")
        return {"status": "registered-offline"}

    monkeypatch.setattr(trial_cli, "start_trial", _fake_start_trial)
    monkeypatch.setattr(trial_cli, "_emit_gate_surface_if_paused", lambda *a, **k: None)

    # Default-ON Namespace (the argparse default).
    args_on = _parse_start(["start", "--input", str(_CORPUS)])
    args_on.runs_root = str(tmp_path)
    trial_cli.start_trial_cli(args_on)
    assert captured["prewalk_settings_confirm"] is True

    # Opt-out Namespace.
    args_off = _parse_start(
        ["start", "--input", str(_CORPUS), "--no-prewalk-settings-confirm"]
    )
    args_off.runs_root = str(tmp_path)
    trial_cli.start_trial_cli(args_off)
    assert captured["prewalk_settings_confirm"] is False
