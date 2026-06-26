"""advance_lo transition-guard tests (Story G0-S1 AC-S1-3 / AC-S1-8). RED-first.

Closed edge map: (mint)->provisional:g0, provisional->refined:irene,
refined->ratified:operator. Everything else raises IllegalTransition. irene may
never produce ratified.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.learning_objective import (
    IllegalTransition,
    LearningObjective,
    SourceAdequacy,
    SourceRef,
    advance_lo,
)


def _ref() -> SourceRef:
    return SourceRef(source_id="s1", locator="p1", quoted_span="span")


def _adq() -> SourceAdequacy:
    return SourceAdequacy(verdict="adequate", rationale="r", missing=[])


def _provisional() -> LearningObjective:
    return LearningObjective(
        objective_id="obj-1",
        statement="Analyze the macro trends",
        status="provisional",
        confidence="medium",
    )


def _refinable() -> LearningObjective:
    # A provisional LO that carries the substrate required to BECOME refined.
    return LearningObjective(
        objective_id="obj-1",
        statement="Analyze the macro trends",
        status="provisional",
        confidence="medium",
        source_refs=[_ref()],
        adequacy=_adq(),
        bloom_level="analyze",
    )


def _refined() -> LearningObjective:
    return advance_lo(_refinable(), "refined", actor="irene")


# --------------------------------------------------------------------------- #
# Legal edges                                                                 #
# --------------------------------------------------------------------------- #
def test_legal_provisional_to_refined_by_irene() -> None:
    lo = advance_lo(_refinable(), "refined", actor="irene")
    assert lo.status == "refined"
    # immutable id carried through
    assert lo.objective_id == "obj-1"


def test_legal_refined_to_ratified_by_operator() -> None:
    lo = advance_lo(_refined(), "ratified", actor="operator")
    assert lo.status == "ratified"


# --------------------------------------------------------------------------- #
# A legal edge still re-checks invariants (ValidationError, not Illegal)       #
# --------------------------------------------------------------------------- #
def test_provisional_to_refined_without_substrate_raises_validation_error() -> None:
    # The EDGE is legal (provisional->refined:irene) but the data isn't ready;
    # the model invariant rejects it. Distinct from IllegalTransition.
    bare = _provisional()
    with pytest.raises(ValidationError):
        advance_lo(bare, "refined", actor="irene")


# --------------------------------------------------------------------------- #
# Idempotent replay                                                           #
# --------------------------------------------------------------------------- #
def test_idempotent_replay_provisional_by_g0_is_noop() -> None:
    lo = _provisional()
    assert advance_lo(lo, "provisional", actor="g0") is lo


def test_idempotent_replay_refined_by_irene_is_noop() -> None:
    lo = _refined()
    assert advance_lo(lo, "refined", actor="irene") is lo


def test_idempotent_replay_ratified_by_operator_is_noop() -> None:
    lo = advance_lo(_refined(), "ratified", actor="operator")
    assert advance_lo(lo, "ratified", actor="operator") is lo


def test_same_status_wrong_actor_is_illegal_not_silent() -> None:
    lo = _provisional()
    with pytest.raises(IllegalTransition):
        advance_lo(lo, "provisional", actor="irene")


# --------------------------------------------------------------------------- #
# Illegal matrix (>= 8 cases incl. irene->ratified)                           #
# --------------------------------------------------------------------------- #
_ILLEGAL_CASES = [
    # (from_status, target, actor)
    ("provisional", "ratified", "operator"),  # skip a stage
    ("provisional", "ratified", "g0"),  # skip + wrong actor
    ("provisional", "refined", "g0"),  # right edge, wrong actor
    ("provisional", "refined", "operator"),  # right edge, wrong actor
    ("refined", "ratified", "irene"),  # *** irene may never ratify ***
    ("refined", "ratified", "g0"),  # right edge, wrong actor
    ("refined", "provisional", "irene"),  # backward
    ("ratified", "refined", "operator"),  # backward
    ("ratified", "provisional", "g0"),  # backward
    ("provisional", "provisional", "irene"),  # same-status wrong actor
    ("refined", "refined", "operator"),  # same-status wrong actor
]


def _at_status(status: str) -> LearningObjective:
    if status == "provisional":
        return _refinable()
    if status == "refined":
        return _refined()
    if status == "ratified":
        return advance_lo(_refined(), "ratified", actor="operator")
    raise AssertionError(status)


@pytest.mark.parametrize("from_status,target,actor", _ILLEGAL_CASES)
def test_illegal_transition_matrix_raises(from_status, target, actor) -> None:
    lo = _at_status(from_status)
    with pytest.raises(IllegalTransition):
        advance_lo(lo, target, actor=actor)  # type: ignore[arg-type]


def test_irene_to_ratified_specifically_raises() -> None:
    # The headline forbidden edge gets its own named assertion.
    refined = _refined()
    with pytest.raises(IllegalTransition):
        advance_lo(refined, "ratified", actor="irene")


# --------------------------------------------------------------------------- #
# AC-S1-8 — full-lifecycle demonstration (offline live-segment proof)         #
# --------------------------------------------------------------------------- #
def test_demo_full_lifecycle_mint_refine_ratify_and_reject_irene_ratify() -> None:
    # mint: construct a provisional LO (the g0 mint state).
    lo = _refinable()
    assert lo.status == "provisional"

    # provisional -> refined by irene.
    refined = advance_lo(lo, "refined", actor="irene")
    assert refined.status == "refined"

    # refined -> ratified by operator.
    ratified = advance_lo(refined, "ratified", actor="operator")
    assert ratified.status == "ratified"

    # irene -> ratified is rejected.
    with pytest.raises(IllegalTransition):
        advance_lo(refined, "ratified", actor="irene")
