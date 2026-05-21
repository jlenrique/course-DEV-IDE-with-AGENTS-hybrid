"""Story 30-3a — scope_decision.set intake tests.

Covers:
* AC-T.3 parametrized intake across the 4 scope literals
* AC-T.6 rationale verbatim roundtrip
"""

from __future__ import annotations

from datetime import UTC, datetime
from functools import partial
from pathlib import Path

import pytest

from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.schema import LearningModel, LessonPlan, PlanUnit, ScopeDecision
from app.marcus.orchestrator.dispatch import dispatch_orchestrator_event
from app.marcus.orchestrator.loop import FourAState, intake_scope_decision


def _single_unit_plan(unit_id: str) -> LessonPlan:
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[
            PlanUnit(
                unit_id=unit_id,
                event_type="gain_attention",
                source_fitness_diagnosis="diag",
                weather_band="green",
                rationale="",
            )
        ],
        revision=0,
        updated_at=datetime.now(tz=UTC),
    )


def _dispatch(tmp_path: Path):
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    return partial(dispatch_orchestrator_event, log=log), log


# ---------------------------------------------------------------------------
# AC-T.3 — parametrized over 4 scope literals
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "scope",
    ["in-scope", "out-of-scope", "delegated", "blueprint"],
)
def test_intake_scope_decision_emits_per_scope_value(
    scope: str, tmp_path: Path
) -> None:
    """AC-T.3 — each scope literal emits a scope_decision.set with correct payload."""
    dispatch, log = _dispatch(tmp_path)
    state = FourAState(draft_plan=_single_unit_plan("u1"))
    decision = ScopeDecision(
        state="ratified",
        scope=scope,  # type: ignore[arg-type]
        proposed_by="operator",
        ratified_by="maya",
    )

    new_state = intake_scope_decision(
        state, "u1", decision, f"rationale for {scope}", dispatch=dispatch
    )

    # State transitions correctly.
    assert "u1" in new_state.ratified_units
    assert new_state.pending_units == ()

    # Single scope_decision.set event with correct payload.
    events = list(log.read_events())
    assert len(events) == 1
    assert events[0].event_type == "scope_decision.set"
    assert events[0].payload["unit_id"] == "u1"
    assert events[0].payload["scope"] == scope
    assert events[0].payload["rationale"] == f"rationale for {scope}"
    assert events[0].payload["ratified_by"] == "maya"


# ---------------------------------------------------------------------------
# AC-T.6 — rationale verbatim roundtrip
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rationale",
    [
        "",
        "simple",
        "⚠️ rethinking this",
        "要再考虑",
        "   keep   ",
        "x" * 10_000,
    ],
)
def test_rationale_stored_verbatim_across_surfaces(
    rationale: str, tmp_path: Path
) -> None:
    """AC-T.6 — rationale is byte-identical across event payload + plan unit."""
    dispatch, log = _dispatch(tmp_path)
    state = FourAState(draft_plan=_single_unit_plan("u1"))
    decision = ScopeDecision(
        state="ratified",
        scope="in-scope",
        proposed_by="operator",
        ratified_by="maya",
    )

    new_state = intake_scope_decision(
        state, "u1", decision, rationale, dispatch=dispatch
    )

    # Event payload preserves the rationale verbatim.
    events = list(log.read_events())
    assert events[0].payload["rationale"] == rationale

    # PlanUnit on the new draft state preserves the rationale verbatim.
    plan_unit = next(u for u in new_state.draft_plan.plan_units if u.unit_id == "u1")
    assert plan_unit.rationale == rationale

    # Log file contains exactly one line (the scope_decision.set envelope).
    # Single-writer discipline is tested by the AST contract tests
    # (test_marcus_single_writer_routing + test_30_2b_dispatch_monopoly).
    log_lines = (
        (tmp_path / "lesson_plan_log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    assert len(log_lines) == 1
