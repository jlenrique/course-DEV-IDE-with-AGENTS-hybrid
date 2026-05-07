"""Tests for marcus/orchestrator/hil_intake.py — Story 32-5.

K = 7, target 9-10 collecting tests.
Tests AC-T.1 through AC-T.9 per story spec.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.schema import LearningModel, LessonPlan, PlanUnit, ScopeDecision
from app.marcus.orchestrator.hil_intake import (
    _FORBIDDEN_TOKENS,
    LogResetNotConfirmedError,
    MissingIntakeDecisionError,
    build_hil_intake_callable,
    reset_lesson_plan_log,
)
from app.marcus.orchestrator.loop import FourAState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_plan(*unit_ids: str) -> LessonPlan:
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        revision=0,
        updated_at=datetime.now(tz=UTC),
        plan_units=[
            PlanUnit(
                unit_id=uid,
                event_type="plan_unit.created",
                source_fitness_diagnosis="Test unit.",
                weather_band="green",
            )
            for uid in unit_ids
        ],
    )


def _make_state(plan: LessonPlan) -> FourAState:
    return FourAState(draft_plan=plan)


# ---------------------------------------------------------------------------
# AC-T.1: build_hil_intake_callable basic contract
# ---------------------------------------------------------------------------

def test_build_hil_intake_callable_returns_callable_and_correct_decision() -> None:
    """AC-T.1: factory returns callable; known unit_id returns (ScopeDecision, rationale)."""
    decisions = {
        "u-01": ("in-scope", "Motion candidate."),
        "u-02": ("out-of-scope", "Learner activity."),
    }
    plan = _make_plan("u-01", "u-02")
    state = _make_state(plan)
    callable_ = build_hil_intake_callable(decisions)

    decision, rationale = callable_(state, "u-01")
    assert isinstance(decision, ScopeDecision)
    assert decision.scope == "in-scope"
    assert decision.state == "ratified"
    assert decision.proposed_by == "operator"
    assert decision.ratified_by == "maya"
    assert rationale == "Motion candidate."

    # Each call returns a fresh ScopeDecision instance — no aliasing
    decision2, _ = callable_(state, "u-01")
    assert decision is not decision2


# ---------------------------------------------------------------------------
# AC-T.2: rationale verbatim — 5 parametrized cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rationale",
    [
        "",                                      # empty string
        "🎓 innovation mindset 🩺",               # emoji
        "x" * 10_000,                            # 10K chars
        "naïve café résumé",                     # non-ASCII characters
        "  leading and trailing whitespace  \t",  # preserve whitespace
    ],
    ids=["empty", "emoji", "10k_chars", "non_ascii", "whitespace"],
)
def test_rationale_stored_verbatim(rationale: str) -> None:
    """AC-T.2: rationale returned byte-for-byte; no strip/coerce/parse."""
    # Inject directly into dict — no normalizing helper
    decisions = {"u-01": ("in-scope", rationale)}
    callable_ = build_hil_intake_callable(decisions)
    plan = _make_plan("u-01")
    state = _make_state(plan)
    _, returned = callable_(state, "u-01")
    assert returned == rationale
    assert len(returned) == len(rationale)


# ---------------------------------------------------------------------------
# AC-T.3: MissingIntakeDecisionError — Voice Register check
# ---------------------------------------------------------------------------

def test_missing_unit_id_raises_with_maya_safe_message() -> None:
    """AC-T.3: missing unit_id raises MissingIntakeDecisionError; message passes Voice Register."""
    decisions = {"u-01": ("in-scope", "")}
    callable_ = build_hil_intake_callable(decisions)
    plan = _make_plan("u-01")
    state = _make_state(plan)

    with pytest.raises(MissingIntakeDecisionError) as exc_info:
        callable_(state, "u-99-unknown")

    message = str(exc_info.value)
    # Voice Register: no forbidden tokens
    for token in _FORBIDDEN_TOKENS:
        assert token not in message.lower(), f"forbidden token {token!r} found in: {message!r}"
    # Message is non-empty human language
    assert len(message) > 10


# ---------------------------------------------------------------------------
# AC-T.4: reset_lesson_plan_log — confirm guard + archive behaviour
# ---------------------------------------------------------------------------

def test_reset_log_without_confirm_raises(tmp_path: Path) -> None:
    """AC-T.4a: reset without confirm=True raises LogResetNotConfirmedError."""
    log_path = tmp_path / "lesson-plan-log.jsonl"
    log_path.write_text("", encoding="utf-8")
    with pytest.raises(LogResetNotConfirmedError):
        reset_lesson_plan_log(tmp_path)


def test_reset_log_archives_and_returns_path(tmp_path: Path) -> None:
    """AC-T.4b: with confirm=True, log is renamed and archive path returned."""
    log_path = tmp_path / "lesson-plan-log.jsonl"
    original_content = '{"event_type": "plan_unit.created"}\n'
    log_path.write_text(original_content, encoding="utf-8")

    archived = reset_lesson_plan_log(tmp_path, confirm=True)

    # Original is gone
    assert not log_path.exists()
    # Archive exists and has the original content
    assert archived is not None
    assert archived.exists()
    assert archived.read_text(encoding="utf-8") == original_content
    # Archive filename matches expected pattern
    assert "STALE-" in archived.name
    assert archived.suffix == ".jsonl"


# ---------------------------------------------------------------------------
# AC-T.5: reset on missing log returns None
# ---------------------------------------------------------------------------

def test_reset_log_on_missing_log_returns_none(tmp_path: Path) -> None:
    """AC-T.5: reset_lesson_plan_log when no log exists returns None (idempotent)."""
    result = reset_lesson_plan_log(tmp_path, confirm=True)
    assert result is None


# ---------------------------------------------------------------------------
# AC-T.5b: idempotent double-reset
# ---------------------------------------------------------------------------

def test_reset_log_idempotent_double_reset(tmp_path: Path) -> None:
    """AC-T.5b: two successive resets produce two distinct archive paths; second returns None."""
    log_path = tmp_path / "lesson-plan-log.jsonl"
    log_path.write_text("first\n", encoding="utf-8")

    archived1 = reset_lesson_plan_log(tmp_path, confirm=True)
    assert archived1 is not None
    assert archived1.exists()

    # Second reset — no log present
    archived2 = reset_lesson_plan_log(tmp_path, confirm=True)
    assert archived2 is None

    # The first archive is still there
    assert archived1.exists()


# ---------------------------------------------------------------------------
# AC-T.6 + AC-T.7: Full 5+3 integration — event counts, ordering, unit_ids
# ---------------------------------------------------------------------------

_IN_SCOPE_UNITS = ["u-01", "u-02", "u-04", "u-05", "u-07"]
_OUT_OF_SCOPE_UNITS = ["u-03", "u-06", "u-08"]
_ALL_UNITS = _IN_SCOPE_UNITS + _OUT_OF_SCOPE_UNITS
_KNOWN_FIXTURE_IDS = frozenset(["u-sensing-loop", "u-fixture-1", "u-fixture-2"])

_DECISIONS_5_3: dict[str, tuple[str, str]] = {
    "u-01": ("in-scope", "Motion candidate."),
    "u-02": ("in-scope", ""),
    "u-03": ("out-of-scope", "Learner activity — not a produced slide."),
    "u-04": ("in-scope", "Cluster head."),
    "u-05": ("in-scope", "Innovation mindset framework."),
    "u-06": ("out-of-scope", "Curated resource reference."),
    "u-07": ("in-scope", "Likely singleton. Recap content."),
    "u-08": ("out-of-scope", "Assessment artifact."),
}


def test_full_5_3_loop_event_counts_and_ordering(tmp_path: Path) -> None:
    """AC-T.6: 5+3 run emits 8 plan_unit.created + 8 scope_decision.set + 1 plan.locked;
    plan.locked index > max(scope_decision.set indices); real FourALoop execution.
    """
    from app.marcus.orchestrator.workflow_runner import route_step_04_gate_to_step_05

    log_path = tmp_path / "lesson-plan-log.jsonl"
    log = LessonPlanLog(path=log_path)
    plan = _make_plan(*_ALL_UNITS)

    result = route_step_04_gate_to_step_05(
        plan,
        pre_collected_decisions=_DECISIONS_5_3,
        log=log,
    )

    assert result.handoff.lesson_plan_revision >= 1

    events = list(log.read_events())
    event_types = [e.event_type for e in events]

    created = [i for i, t in enumerate(event_types) if t == "plan_unit.created"]
    scope_set = [i for i, t in enumerate(event_types) if t == "scope_decision.set"]
    locked = [i for i, t in enumerate(event_types) if t == "plan.locked"]

    assert len(created) == 8, f"Expected 8 plan_unit.created, got {len(created)}"
    assert len(scope_set) == 8, f"Expected 8 scope_decision.set, got {len(scope_set)}"
    assert len(locked) == 1, f"Expected 1 plan.locked, got {len(locked)}"

    # plan.locked must be after all scope_decision.set events
    assert locked[0] > max(scope_set), (
        f"plan.locked at index {locked[0]} must be > max(scope_decision.set) = {max(scope_set)}"
    )


def test_full_5_3_loop_unit_ids_match_decisions_not_fixtures(tmp_path: Path) -> None:
    """AC-T.7: log unit_ids == pre_collected_decisions keys; no fixture IDs contaminate."""
    from app.marcus.orchestrator.workflow_runner import route_step_04_gate_to_step_05

    log_path = tmp_path / "lesson-plan-log.jsonl"
    log = LessonPlanLog(path=log_path)
    plan = _make_plan(*_ALL_UNITS)

    route_step_04_gate_to_step_05(
        plan,
        pre_collected_decisions=_DECISIONS_5_3,
        log=log,
    )

    events = list(log.read_events())
    # Collect all unit_id values from event payloads
    log_unit_ids: set[str] = set()
    for event in events:
        payload = event.payload or {}
        if isinstance(payload, dict) and payload.get("unit_id") is not None:
            log_unit_ids.add(payload["unit_id"])

    expected_ids = set(_DECISIONS_5_3.keys())
    assert log_unit_ids == expected_ids, (
        f"Log unit_ids {log_unit_ids} do not match expected {expected_ids}"
    )
    assert _KNOWN_FIXTURE_IDS.isdisjoint(log_unit_ids), (
        f"Fixture IDs contaminate log: {_KNOWN_FIXTURE_IDS & log_unit_ids}"
    )


# ---------------------------------------------------------------------------
# AC-T.8: reset→run recovery integration
# ---------------------------------------------------------------------------

def test_reset_then_run_produces_clean_log(tmp_path: Path) -> None:
    """AC-T.8: after reset on contaminated log, subsequent run contains only new events."""
    from app.marcus.orchestrator.workflow_runner import route_step_04_gate_to_step_05

    # Seed a "contaminated" log with fixture events
    log_path = tmp_path / "lesson-plan-log.jsonl"
    log_path.write_text(
        '{"event_type": "plan_unit.created", "unit_id": "u-sensing-loop", '
        '"plan_revision": 0, "writer_identity": "marcus-orchestrator", '
        '"schema_version": "1.0"}\n',
        encoding="utf-8",
    )
    assert log_path.exists()

    # Reset
    archived = reset_lesson_plan_log(tmp_path, confirm=True)
    assert archived is not None
    assert not log_path.exists()

    # Run fresh 5+3 loop
    log = LessonPlanLog(path=log_path)
    plan = _make_plan(*_ALL_UNITS)
    route_step_04_gate_to_step_05(
        plan,
        pre_collected_decisions=_DECISIONS_5_3,
        log=log,
    )

    events = list(log.read_events())
    event_types = [e.event_type for e in events]
    # New log contains only the new run's events — no stale fixture event
    all_payload_texts = log_path.read_text(encoding="utf-8")
    assert "u-sensing-loop" not in all_payload_texts
    # Standard counts from new run
    assert event_types.count("plan_unit.created") == 8
    assert event_types.count("scope_decision.set") == 8
    assert event_types.count("plan.locked") == 1


# ---------------------------------------------------------------------------
# G6-P3 (AC-D.2 / AC-T.2): rationale survives scope_decision.set → log → read-back
# ---------------------------------------------------------------------------

def test_rationale_preserved_through_log_round_trip(tmp_path: Path) -> None:
    """G6-P3 / AC-D.2: 10K rationale survives emission, log serialisation, and read-back."""
    from app.marcus.orchestrator.workflow_runner import route_step_04_gate_to_step_05

    long_rationale = "R" * 10_000
    decisions = {
        "u-01": ("in-scope", long_rationale),
        "u-02": ("out-of-scope", "short"),
    }
    plan = _make_plan("u-01", "u-02")
    log_path = tmp_path / "lesson-plan-log.jsonl"
    log = LessonPlanLog(path=log_path)

    route_step_04_gate_to_step_05(
        plan,
        pre_collected_decisions=decisions,
        log=log,
    )

    # Read back all scope_decision.set events and verify u-01 rationale preserved
    events = list(log.read_events())
    scope_events = [e for e in events if e.event_type == "scope_decision.set"]
    rationales_in_log: dict[str, str] = {}
    for event in scope_events:
        payload = event.payload or {}
        if isinstance(payload, dict) and payload.get("unit_id") is not None:
            rationales_in_log[payload["unit_id"]] = payload.get("rationale", "")

    assert "u-01" in rationales_in_log, "u-01 scope_decision.set event not found in log"
    assert rationales_in_log["u-01"] == long_rationale, (
        f"Rationale truncated: expected len {len(long_rationale)}, "
        f"got len {len(rationales_in_log['u-01'])}"
    )


# ---------------------------------------------------------------------------
# G6-P1: both intake_callable and pre_collected_decisions raises ValueError
# ---------------------------------------------------------------------------

def test_both_intake_callable_and_decisions_raises(tmp_path: Path) -> None:
    """G6-P1: providing both intake_callable and pre_collected_decisions is ambiguous."""
    from app.marcus.lesson_plan.schema import ScopeDecision
    from app.marcus.orchestrator.workflow_runner import route_step_04_gate_to_step_05

    def stub(_state: FourAState, _unit_id: str) -> tuple[ScopeDecision, str]:
        return ScopeDecision(state="ratified", scope="in-scope",
                             proposed_by="operator", ratified_by="maya"), ""

    plan = _make_plan("u-01")
    with pytest.raises(ValueError, match="exactly one"):
        route_step_04_gate_to_step_05(
            plan,
            intake_callable=stub,
            pre_collected_decisions={"u-01": ("in-scope", "")},
        )


# ---------------------------------------------------------------------------
# G6-P2: extra unit_ids in pre_collected_decisions raises ValueError
# ---------------------------------------------------------------------------

def test_extra_decision_ids_raise(tmp_path: Path) -> None:
    """G6-P2: pre_collected_decisions with extra unit_ids not in plan fails fast."""
    from app.marcus.orchestrator.workflow_runner import route_step_04_gate_to_step_05

    plan = _make_plan("u-01")
    with pytest.raises(ValueError, match="not in the packet plan"):
        route_step_04_gate_to_step_05(
            plan,
            pre_collected_decisions={
                "u-01": ("in-scope", ""),
                "u-stale": ("in-scope", "stale decision that should fail fast"),
            },
        )
