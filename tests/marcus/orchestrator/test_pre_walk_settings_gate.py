"""Story 42.5 — pre-walk settings confirm-or-change gate (WALK test).

Acceptance (Murat, AC-5) is a WALK test, not a snapshot: the run HALTS on the
pre-walk settings surface BEFORE G0 / the first spend, the surface carries all 16
toggles, a ``change`` (edit) mutates a setting and the walk then proceeds with the
NEW value, and a ``confirm`` (approve) proceeds unchanged. The pause/resume/change
round-trip is exercised end-to-end against the shared runner functions with a fake
adapter + stubbed preflight/cost — hermetic, no live LLM, no network, no windows.

Design (option B — see g_settings.py): the pre-walk gate is a PRE-PIPELINE pause
(no specialist, not a manifest node) that reuses the canonical DecisionCard pause
-> OperatorVerdict -> resume_from_verdict machinery every production gate uses.
"""

from __future__ import annotations

import json
import textwrap
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import operator_surface_assembler as osa
from app.marcus.orchestrator import package_builders
from app.marcus.orchestrator import production_runner as pr
from app.models.decision_cards import GSettingsCard
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.runtime.operator_surface import RUN_SETTINGS_TOGGLES
from app.models.state.operator_verdict import OperatorVerdict

_CORPUS = Path("tests/fixtures/trial_corpus/README.md")
_OPERATOR = "operator_test"

# A trimmed manifest with the Story 42.5 G0S pre-walk settings gate at the HEAD
# (mirrors the real manifest wiring) then a single `cd` @ 4.75 specialist — so
# "proceeding past the settings gate" dispatches exactly one specialist and
# completes, without dragging in the §06 builder's plan-authority contract.
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
    mp = tmp_path / "manifest.yaml"
    mp.write_text(_CD_ONLY_MANIFEST_YAML, encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # Wake the G0S pre-walk settings gate (operator-steered real run; the runner
    # traverses it byte-identically when the flag is unset — the G0E/G0R convention).
    monkeypatch.setenv("MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE", "1")
    # env toggles start from a known baseline so monkeypatch restores them at
    # teardown even after the walk mutates os.environ from the override file.
    monkeypatch.setenv("MARCUS_TRIAL_BUDGET_USD", "0")
    monkeypatch.setenv("MARCUS_RESEARCH_DISPATCH_LIVE", "on")
    spy = _SpyAdapter()
    monkeypatch.setattr(pr, "ProductionDispatchAdapter", lambda: spy)
    monkeypatch.setattr(
        pr,
        "_run_start_preflight_gate",
        lambda *a, **k: SimpleNamespace(all_green=True, blocking_items=lambda: []),
    )
    monkeypatch.setattr(
        pr, "_record_cost", lambda **_k: tmp_path / "cost-report.json"
    )
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


def _load_card_json(tmp_path: Path, trial_id: UUID) -> dict:
    return json.loads(
        (tmp_path / str(trial_id) / f"decision-card-{pr.PRE_WALK_SETTINGS_GATE_ID}.json")
        .read_text(encoding="utf-8")
    )


def _verdict(
    trial_id: UUID, card_json: dict, verb: str, edit_payload: dict | None = None
) -> OperatorVerdict:
    kwargs: dict = {
        "trial_id": trial_id,
        "gate_id": pr.PRE_WALK_SETTINGS_GATE_ID,
        "verb": verb,
        "card_id": UUID(card_json["card"]["card_id"]),
        "decision_card_digest": card_json["digest"],
        "operator_id": _OPERATOR,
        "verdict_id": uuid4(),
        "timestamp": datetime.now(UTC),
    }
    if edit_payload is not None:
        kwargs["edit_payload"] = edit_payload
    return OperatorVerdict(**kwargs)


# --------------------------------------------------------------------------- #
# AC-1 — the walk halts on the settings surface BEFORE G0 / the first spend.
# --------------------------------------------------------------------------- #


def test_ac1_operator_run_pauses_at_settings_before_first_spend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("aaaaaaaa-1111-4111-8111-111111111111")
    mp, spy = _prep(tmp_path, monkeypatch)
    envelope = _start(tmp_path, mp, trial_id)

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == pr.PRE_WALK_SETTINGS_GATE_ID
    # Nothing spent: the specialist adapter was never called at the pre-walk pause.
    assert spy.dispatched == []
    assert envelope.production_envelope.get_contribution("cd", node_id="4.75") is None
    # checkpoint re-enters the walk PAST the G0S head gate (node_index=0 ->
    # next_node_index=1) so a confirm continues into the first real node.
    checkpoint = json.loads(
        (tmp_path / str(trial_id) / "checkpoint.json").read_text(encoding="utf-8")
    )
    assert checkpoint["gate_id"] == pr.PRE_WALK_SETTINGS_GATE_ID
    assert checkpoint["next_node_index"] == 1


def test_ac1_settings_card_carries_all_16_toggles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("aaaaaaaa-2222-4222-8222-222222222222")
    mp, _ = _prep(tmp_path, monkeypatch)
    _start(tmp_path, mp, trial_id)

    card = _load_card_json(tmp_path, trial_id)["card"]
    readout = card["run_settings"]
    for field, _label in RUN_SETTINGS_TOGGLES:
        assert field in readout, f"settings surface missing toggle {field}"
    assert len(RUN_SETTINGS_TOGGLES) == 16


# --------------------------------------------------------------------------- #
# Reuse-of-primitive pin (AC-4) + neutrality pin (AC-2).
# --------------------------------------------------------------------------- #


def test_settings_gate_reuses_the_decision_card_primitive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The pause is a real GSettingsCard registered through the canonical
    register/checkpoint/decision-card machinery — not a bespoke pause."""
    trial_id = UUID("aaaaaaaa-3333-4333-8333-333333333333")
    mp, _ = _prep(tmp_path, monkeypatch)
    _start(tmp_path, mp, trial_id)
    card_json = _load_card_json(tmp_path, trial_id)
    # The registered card round-trips as a GSettingsCard (the shared union adapter).
    from app.models.decision_cards import AnyDecisionCardAdapter

    parsed = AnyDecisionCardAdapter.validate_python(card_json["card"])
    assert isinstance(parsed, GSettingsCard)
    # A verdict validates through the shared resume_from_verdict digest/nonce path.
    stored = pr.get_registered_decision_card(trial_id, pr.PRE_WALK_SETTINGS_GATE_ID)
    assert stored is not None and stored.digest == card_json["digest"]


def test_neutrality_no_preselected_verb(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("aaaaaaaa-4444-4444-8444-444444444444")
    mp, _ = _prep(tmp_path, monkeypatch)
    _start(tmp_path, mp, trial_id)
    card = _load_card_json(tmp_path, trial_id)["card"]
    # confirm(approve)/change(edit) presented neutrally — no preselected verdict.
    assert card["allowed_verbs"] == ["approve", "edit"]


# --------------------------------------------------------------------------- #
# AC-2/AC-5 — CONFIRM proceeds unchanged (the walk runs, one specialist dispatches).
# --------------------------------------------------------------------------- #


def test_confirm_proceeds_and_walk_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("bbbbbbbb-1111-4111-8111-111111111111")
    mp, spy = _prep(tmp_path, monkeypatch)
    _start(tmp_path, mp, trial_id)
    card_json = _load_card_json(tmp_path, trial_id)

    resumed = pr.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(trial_id, card_json, "approve"),
        runs_root=tmp_path,
    )
    assert resumed.status == "completed"
    # CONFIRM crossed the pre-walk gate and the walk dispatched the specialist.
    assert "cd" in spy.dispatched
    assert resumed.production_envelope.get_contribution("cd", node_id="4.75") is not None


def test_ac4_confirm_survives_process_boundary_via_disk_rehydration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-4 both-walk / process-boundary pin: clearing the in-memory card registry
    (a fresh resume process) still resumes — the card rehydrates from disk through
    the shared union adapter and the resume goes through _continue_production_walk."""
    trial_id = UUID("bbbbbbbb-2222-4222-8222-222222222222")
    mp, spy = _prep(tmp_path, monkeypatch)
    _start(tmp_path, mp, trial_id)
    card_json = _load_card_json(tmp_path, trial_id)
    verdict = _verdict(trial_id, card_json, "approve")

    clear_resume_registry()  # simulate the fresh resume process (empty _CARD_STORE)
    resumed = pr.resume_production_trial(
        trial_id=trial_id, verdict=verdict, runs_root=tmp_path
    )
    assert resumed.status == "completed"
    assert "cd" in spy.dispatched


# --------------------------------------------------------------------------- #
# AC-3/AC-5 — CHANGE writes to the ONE resolution point; the walk observes it.
# --------------------------------------------------------------------------- #


def test_change_re_presents_updated_readout_then_confirm_walk_observes_new_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("cccccccc-1111-4111-8111-111111111111")
    mp, spy = _prep(tmp_path, monkeypatch)
    _start(tmp_path, mp, trial_id)
    card_json = _load_card_json(tmp_path, trial_id)

    # CHANGE budget + a live-toggle. The change re-presents the settings surface
    # (loop until confirm) — it does NOT proceed with the walk.
    change = pr.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(
            trial_id,
            card_json,
            "edit",
            edit_payload={"trial_budget_usd": "5.00", "research_dispatch_live": "off"},
        ),
        runs_root=tmp_path,
    )
    assert change.status == "paused-at-gate"
    assert change.paused_gate == pr.PRE_WALK_SETTINGS_GATE_ID
    assert spy.dispatched == []  # no spend on a change

    # The ONE resolution point recorded the change, and the RE-PRESENTED readout
    # reflects it (AC-3 "reflected in the standing readout for the rest of the run").
    overrides = osa.load_run_settings_overrides(tmp_path / str(trial_id))
    assert overrides == {"trial_budget_usd": "5.00", "research_dispatch_live": "off"}
    changed_card = _load_card_json(tmp_path, trial_id)["card"]
    assert changed_card["run_settings"]["trial_budget_usd"] == "5.00"
    assert changed_card["run_settings"]["research_dispatch_live"] == "off"

    # CONFIRM the changed settings -> the walk proceeds AND observes the new value.
    # Re-read the FRESH card written by the change re-pause (new card_id/digest).
    confirm = pr.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(trial_id, _load_card_json(tmp_path, trial_id), "approve"),
        runs_root=tmp_path,
    )
    assert confirm.status == "completed"
    assert "cd" in spy.dispatched
    # The walk read the overridden values from the single resolution point (projected
    # to the env the walk resolves FIRST at the walk-entry seam).
    import os

    assert os.environ["MARCUS_TRIAL_BUDGET_USD"] == "5.00"
    assert os.environ["MARCUS_RESEARCH_DISPATCH_LIVE"] == "off"
    assert pr._research_dispatch_live() is False


def test_change_rejects_unknown_toggle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A CHANGE naming a non-canonical toggle fails loud (no partial write)."""
    trial_id = UUID("cccccccc-2222-4222-8222-222222222222")
    mp, _ = _prep(tmp_path, monkeypatch)
    _start(tmp_path, mp, trial_id)
    card_json = _load_card_json(tmp_path, trial_id)
    with pytest.raises(osa.UnknownRunSettingError):
        pr.resume_production_trial(
            trial_id=trial_id,
            verdict=_verdict(
                trial_id, card_json, "edit", edit_payload={"not_a_toggle": "x"}
            ),
            runs_root=tmp_path,
        )


# --------------------------------------------------------------------------- #
# AC-6 — opt-out honesty: non-interactive / offline SKIP the pause, explicitly.
# --------------------------------------------------------------------------- #


def test_ac6_non_interactive_skips_settings_pause_explicitly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("dddddddd-1111-4111-8111-111111111111")
    mp, spy = _prep(tmp_path, monkeypatch)
    # pause_at_gates=False: a non-interactive run does NOT pause at settings; the
    # walk proceeds (and the skip is traced, never silent).
    envelope = _start(tmp_path, mp, trial_id, pause_at_gates=False)
    assert envelope.paused_gate != pr.PRE_WALK_SETTINGS_GATE_ID
    surface = json.loads(
        (tmp_path / str(trial_id) / "operator-surface.json").read_text(encoding="utf-8")
    )
    events = [e["event"] for e in (surface.get("trace") or {}).get("events", [])]
    assert "prewalk-settings-skipped" in events


def test_ac6_offline_harness_skips_settings_pause_explicitly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = UUID("dddddddd-2222-4222-8222-222222222222")
    mp, _ = _prep(tmp_path, monkeypatch)
    envelope = _start(tmp_path, mp, trial_id, allow_offline_cost_report=True)
    assert envelope.paused_gate != pr.PRE_WALK_SETTINGS_GATE_ID
    surface = json.loads(
        (tmp_path / str(trial_id) / "operator-surface.json").read_text(encoding="utf-8")
    )
    events = [e["event"] for e in (surface.get("trace") or {}).get("events", [])]
    assert "prewalk-settings-skipped" in events
