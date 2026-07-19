"""Hermetic (direct-emit) tests for the per-run ``fence_state`` block + honest
``silent_bypass_events`` detector (Story Q1.4a).

These call ``production_runner._emit_run_summary_yaml(...)`` DIRECTLY with a tmp
run dir — NOT the live-preflight ``run_production_trial`` integration path (which
has a pre-existing, unrelated Epic-41 preflight-gate failure). No live calls.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from app.marcus.cli import hil_tabular_projector
from app.marcus.orchestrator import (
    coverage_gate_wiring,
    production_runner,
    udac_wiring,
)
from app.models.runtime.trial_economics_report import (
    BudgetStatus,
    TrialEconomicsReport,
)
from app.models.state.component_selection import ComponentSelection

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
DEFAULT_MANIFEST_PATH = production_runner.DEFAULT_MANIFEST_PATH

_FIDELITY_FN = "app.specialists.irene.graph.narration_figure_fidelity_active"


def _emit(tmp_path: Path, **overrides) -> dict:
    kwargs = dict(
        trial_id=TRIAL_ID,
        terminal_gate="G1",
        runs_root=tmp_path,
        manifest_path=DEFAULT_MANIFEST_PATH,
        langsmith_trace_id=None,
    )
    kwargs.update(overrides)
    path = production_runner._emit_run_summary_yaml(**kwargs)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _fences_off(monkeypatch: pytest.MonkeyPatch) -> None:
    # Deterministic default env: all three fences OFF unless a test flips them.
    monkeypatch.setattr(coverage_gate_wiring, "coverage_gate_active", lambda: False)
    monkeypatch.setattr(udac_wiring, "udac_active", lambda: False)
    monkeypatch.setattr(_FIDELITY_FN, lambda: False)


# ---------------------------------------------------------------- AC1 / shape
def test_fence_state_present_and_shape(tmp_path: Path) -> None:
    payload = _emit(tmp_path)
    fs = payload["fence_state"]
    assert set(fs) == {
        "fences_enabled",
        "silent_bypass_events",
        "hil_allowlist_empty",
        "pack_hash_binding",
        "conversation_chain_digest",
        "cost_posture",
    }
    assert set(fs["fences_enabled"]) == {"fidelity", "coverage", "udac"}
    # References the already-computed payload values, not a recompute.
    assert fs["pack_hash_binding"] == payload["pack_hash_binding"]
    assert fs["conversation_chain_digest"] == payload["conversation_chain_digest"]


# ---------------------------------------------------------- AC2 / GL-8 matrix
def test_silent_bypass_undetected_when_no_signal(tmp_path: Path) -> None:
    payload = _emit(tmp_path)
    assert payload["fence_state"]["silent_bypass_events"] == "undetected"


def test_silent_bypass_reports_seeded_synthetic_event(tmp_path: Path) -> None:
    payload = _emit(tmp_path, silent_bypass_events=2)
    assert payload["fence_state"]["silent_bypass_events"] == 2


def test_silent_bypass_real_zero_when_detector_ran(tmp_path: Path) -> None:
    payload = _emit(tmp_path, silent_bypass_events=0)
    assert payload["fence_state"]["silent_bypass_events"] == 0


def test_silent_bypass_negative_floored_to_undetected(tmp_path: Path) -> None:
    # FIX-A: a negative int is never an honest count — floor to the sentinel.
    payload = _emit(tmp_path, silent_bypass_events=-1)
    assert payload["fence_state"]["silent_bypass_events"] == "undetected"


def test_silent_bypass_bool_signal_is_undetected_and_not_logged(
    tmp_path: Path, caplog
) -> None:
    # FIX-A: a bool signal is treated like the detector treats it (→ undetected),
    # never logged as "expected 0, got True".
    caplog.set_level("DEBUG", logger=production_runner.__name__)
    payload = _emit(tmp_path, silent_bypass_events=True)
    assert payload["fence_state"]["silent_bypass_events"] == "undetected"
    assert "got True" not in caplog.text
    assert "expected 0" not in caplog.text


def test_top_level_silent_bypass_key_removed(tmp_path: Path) -> None:
    # The dishonest hardcoded top-level 0 stamp is gone (GL-8); the honest value
    # lives only inside fence_state.
    payload = _emit(tmp_path)
    assert "silent_bypass_events" not in payload


# ------------------------------------------------------------ AC4 both walks
@pytest.mark.parametrize(
    "extra",
    [
        pytest.param({}, id="resume-walk-early-reject-no-composed-manifest"),
        pytest.param(
            {"selection": ComponentSelection()},
            id="start-walk-with-selection",
        ),
    ],
)
def test_fence_state_present_in_both_walks(tmp_path: Path, extra: dict) -> None:
    payload = _emit(tmp_path, **extra)
    assert "fence_state" in payload
    assert set(payload["fence_state"]["fences_enabled"]) == {
        "fidelity",
        "coverage",
        "udac",
    }


# --------------------------------------------------------------- AC5 env truth
@pytest.mark.parametrize(
    ("fidelity", "coverage", "udac"),
    [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (True, True, True),
    ],
)
def test_fences_enabled_reflects_env_truth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fidelity: bool,
    coverage: bool,
    udac: bool,
) -> None:
    monkeypatch.setattr(_FIDELITY_FN, lambda: fidelity)
    monkeypatch.setattr(coverage_gate_wiring, "coverage_gate_active", lambda: coverage)
    monkeypatch.setattr(udac_wiring, "udac_active", lambda: udac)
    payload = _emit(tmp_path)
    assert payload["fence_state"]["fences_enabled"] == {
        "fidelity": fidelity,
        "coverage": coverage,
        "udac": udac,
    }


@pytest.mark.parametrize("bad", [None, "off", 1, object()])
def test_fences_enabled_non_bool_return_is_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad: object
) -> None:
    # FIX-B: a gate fn that returns a NON-bool must degrade to the honest marker,
    # never be silently bool()-coerced (None->False would report a fence
    # definitely-OFF when the truth is actually unknown).
    monkeypatch.setattr(_FIDELITY_FN, lambda: bad)
    monkeypatch.setattr(coverage_gate_wiring, "coverage_gate_active", lambda: bad)
    monkeypatch.setattr(udac_wiring, "udac_active", lambda: bad)
    payload = _emit(tmp_path)
    assert payload["fence_state"]["fences_enabled"] == {
        "fidelity": "unavailable",
        "coverage": "unavailable",
        "udac": "unavailable",
    }


@pytest.mark.parametrize(
    ("allowlist", "expected"),
    [(frozenset(), True), (frozenset({"07C"}), False)],
)
def test_hil_allowlist_empty_reflects_allowlist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    allowlist: frozenset,
    expected: bool,
) -> None:
    monkeypatch.setattr(hil_tabular_projector, "KNOWN_UNRENDERED_ALLOWLIST", allowlist)
    payload = _emit(tmp_path)
    assert payload["fence_state"]["hil_allowlist_empty"] is expected


# ----------------------------------------------------------- AC6 fail-soft
def _raise(*_a, **_k):
    raise RuntimeError("boom")


def test_fail_soft_fidelity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_FIDELITY_FN, _raise)
    payload = _emit(tmp_path)
    assert payload["fence_state"]["fences_enabled"]["fidelity"] == "unavailable"
    # A neighbouring field must NOT be collateral-degraded.
    assert payload["fence_state"]["fences_enabled"]["coverage"] is False


def test_fail_soft_coverage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(coverage_gate_wiring, "coverage_gate_active", _raise)
    payload = _emit(tmp_path)
    assert payload["fence_state"]["fences_enabled"]["coverage"] == "unavailable"
    assert payload["fence_state"]["fences_enabled"]["udac"] is False


def test_fail_soft_udac(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(udac_wiring, "udac_active", _raise)
    payload = _emit(tmp_path)
    assert payload["fence_state"]["fences_enabled"]["udac"] == "unavailable"


def test_fail_soft_allowlist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class _Boom:
        def __len__(self) -> int:
            raise RuntimeError("boom")

    monkeypatch.setattr(hil_tabular_projector, "KNOWN_UNRENDERED_ALLOWLIST", _Boom())
    payload = _emit(tmp_path)
    assert payload["fence_state"]["hil_allowlist_empty"] == "unavailable"


def test_fail_soft_pack_hash_binding_still_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # FIX-C (AC6 always-write): on a reject/resume emit (no composed_manifest)
    # _pack_hash_binding forces a LIVE compose that can raise. A raise must NOT
    # abort the emit — the file is still written and the value degrades to the
    # honest marker in BOTH the top-level key and the fence_state reference.
    monkeypatch.setattr(production_runner, "_pack_hash_binding", _raise)
    payload = _emit(tmp_path)
    assert (tmp_path / str(TRIAL_ID) / "run_summary.yaml").is_file()
    assert payload["pack_hash_binding"] == "unavailable"
    assert payload["fence_state"]["pack_hash_binding"] == "unavailable"


def test_fail_soft_conversation_chain_digest_still_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # FIX-C: a directive.yaml read race in _conversation_chain_digest must not
    # abort the emit either.
    monkeypatch.setattr(production_runner, "_conversation_chain_digest", _raise)
    payload = _emit(tmp_path)
    assert (tmp_path / str(TRIAL_ID) / "run_summary.yaml").is_file()
    assert payload["conversation_chain_digest"] == "unavailable"
    assert payload["fence_state"]["conversation_chain_digest"] == "unavailable"


def test_fail_soft_cost(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A malformed cost-report degrades cost_posture to the honest marker, not a raise.
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "cost-report.json").write_text("{not valid json", encoding="utf-8")
    payload = _emit(tmp_path)
    assert payload["fence_state"]["cost_posture"] == "unavailable"


# ------------------------------------------------------ AC1 cost_posture
def _valid_report_json() -> str:
    report = TrialEconomicsReport(
        trial_id=str(TRIAL_ID),
        measured_at=datetime(2026, 7, 19, tzinfo=UTC),
        total_cost_usd=1.23,
        per_agent_breakdown={},
        per_model_breakdown={},
        cascade_config_digest="a" * 64,
        pricing_table_digest="b" * 64,
        budget_status=BudgetStatus(state="no-cap", over_by_usd=0.0),
        cost_posture="exact",
        unavailable_attempt_count=0,
    )
    return report.model_dump_json()


def test_cost_posture_from_report(tmp_path: Path) -> None:
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "cost-report.json").write_text(_valid_report_json(), encoding="utf-8")
    payload = _emit(tmp_path)
    assert payload["fence_state"]["cost_posture"] == "exact"


def test_cost_posture_unavailable_without_report(tmp_path: Path) -> None:
    payload = _emit(tmp_path)
    assert payload["fence_state"]["cost_posture"] == "unavailable"


# ----------------------------------------------- AC3 static breadcrumb, no doc read
def test_quality_scorecard_is_static_breadcrumb(tmp_path: Path) -> None:
    payload = _emit(tmp_path)
    assert payload["quality_scorecard"] == {
        "source": "docs/quality/project-quality-scorecard.md",
        "note": "project-level-not-this-run",
    }


def test_no_scorecard_doc_read_during_emit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # If a doc-read is (re)introduced into the emit path, this spy fires -> RED.
    import app.quality.scorecard as scorecard_mod

    called = {"n": 0}

    def _spy(*_a, **_k):
        called["n"] += 1
        raise AssertionError("scorecard doc must not be read during run_summary emit")

    monkeypatch.setattr(scorecard_mod, "did_score_ref", _spy)
    monkeypatch.setattr(scorecard_mod, "dimension_ref", _spy)
    payload = _emit(tmp_path)
    assert called["n"] == 0
    assert payload["quality_scorecard"]["note"] == "project-level-not-this-run"
