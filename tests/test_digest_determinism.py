"""AC-T.7 — Digest determinism (R2 rider AM-3 swap).

Asserts:
    - 100-invocation digest stability on the same plan.
    - Key-insertion-order invariance (canonical JSON).
    - Mutation sensitivity (any field change -> different digest).
    - Nested-list-order sensitivity (``gaps=[a,b]`` != ``gaps=[b,a]``; R2 AM-3).
    - None-vs-missing-field identity (``scope_decision=None`` == absent; R2 AM-3).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.marcus.lesson_plan.digest import assert_digest_matches, compute_digest
from app.marcus.lesson_plan.schema import (
    IdentifiedGap,
    LearningModel,
    LessonPlan,
    PlanUnit,
    ScopeDecision,
)


def _ts() -> datetime:
    return datetime(2026, 4, 18, 12, 0, 0, tzinfo=UTC)


def _sd() -> ScopeDecision:
    return ScopeDecision(
        state="proposed",
        scope="in-scope",
        proposed_by="system",
        _internal_proposed_by="marcus",
    )


def _plan_with_gaps(gap_ids: list[str]) -> LessonPlan:
    gaps = [
        IdentifiedGap(gap_id=g, description="x", suggested_posture="embellish")
        for g in gap_ids
    ]
    pu = PlanUnit(
        unit_id="gagne-event-3",
        event_type="gagne-event-3",
        source_fitness_diagnosis="ok",
        scope_decision=_sd(),
        weather_band="green",
        rationale="stable",
        gaps=gaps,
    )
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[pu],
        revision=1,
        updated_at=_ts(),
    )


def _plan_baseline() -> LessonPlan:
    return _plan_with_gaps([])


def test_digest_deterministic_across_100_invocations() -> None:
    plan = _plan_baseline()
    first = compute_digest(plan)
    for _ in range(100):
        assert compute_digest(plan) == first


def test_digest_stable_across_key_insertion_order() -> None:
    """Two logically-equivalent plans built in different attribute order digest the same."""
    plan_a = _plan_baseline()
    # Build the "same" plan by round-tripping through a reordered dict.
    payload = plan_a.model_dump(mode="json")
    reordered = {k: payload[k] for k in sorted(payload.keys(), reverse=True)}
    plan_b = LessonPlan.model_validate(reordered)
    assert compute_digest(plan_a) == compute_digest(plan_b)


@pytest.mark.parametrize(
    "mutation",
    [
        {"revision": 99},
        {"updated_at": datetime(9999, 1, 1, tzinfo=UTC)},
    ],
)
def test_digest_sensitive_to_field_mutation(mutation: dict) -> None:
    plan = _plan_baseline()
    base = compute_digest(plan)
    mutated = plan.model_copy(update=mutation)
    assert compute_digest(mutated) != base


def test_digest_sensitive_to_nested_list_order_gaps() -> None:
    """R2 AM-3: gaps list order is SEMANTIC on the digest."""
    plan_abc = _plan_with_gaps(["a", "b", "c"])
    plan_acb = _plan_with_gaps(["a", "c", "b"])
    assert compute_digest(plan_abc) != compute_digest(plan_acb), (
        "gaps list order must change the digest — per R2 AM-3 the order is semantic."
    )


def test_digest_none_equals_missing_field() -> None:
    """R2 AM-3: ``scope_decision=None`` digests IDENTICALLY to the field being absent."""
    pu_with_none = PlanUnit(
        unit_id="gagne-event-3",
        event_type="gagne-event-3",
        source_fitness_diagnosis="ok",
        scope_decision=None,
        weather_band="amber",
        rationale="",
    )
    plan_with_none = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[pu_with_none],
        revision=1,
        updated_at=_ts(),
    )
    # Reconstruct via dict with the field stripped entirely — the same digest.
    raw = plan_with_none.model_dump(mode="json")
    pu_raw = raw["plan_units"][0]
    pu_raw.pop("scope_decision", None)  # remove the field entirely
    plan_without_field = LessonPlan.model_validate(raw)
    assert compute_digest(plan_with_none) == compute_digest(plan_without_field), (
        "None-valued field must digest identically to a missing field (R2 AM-3)."
    )


def test_assert_digest_matches_accepts_valid_digest() -> None:
    plan = _plan_baseline()
    stored = compute_digest(plan)
    plan2 = plan.model_copy(update={"digest": stored})
    assert_digest_matches(plan2)  # no exception


def test_assert_digest_matches_rejects_wrong_digest() -> None:
    plan = _plan_baseline()
    plan2 = plan.model_copy(update={"digest": "deadbeef" * 8})
    with pytest.raises(ValueError):
        assert_digest_matches(plan2)
