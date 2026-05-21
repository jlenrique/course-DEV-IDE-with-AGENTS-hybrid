"""AC-T.10 — Plan-revision monotonicity test.

``LessonPlan.revision`` is a monotonic counter. Reconciling a plan with a
stale revision (equal to or less than the current committed revision) via
:meth:`LessonPlan.apply_revision` raises :class:`StaleRevisionError`.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.marcus.lesson_plan.digest import compute_digest
from app.marcus.lesson_plan.schema import (
    LearningModel,
    LessonPlan,
    StaleRevisionError,
)


def _base_plan(revision: int) -> LessonPlan:
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[],
        revision=revision,
        updated_at=datetime.now(tz=UTC),
    )


def test_revision_field_ge_zero() -> None:
    plan = _base_plan(0)
    assert plan.revision == 0


def test_bump_revision_increases_by_one() -> None:
    plan = _base_plan(5)
    bumped = plan.bump_revision()
    assert bumped.revision == 6


def test_stale_revision_lower_raises_stale_revision_error() -> None:
    """Applying a strictly-lower revision raises :class:`StaleRevisionError`."""
    current = _base_plan(10)
    stale = _base_plan(3)
    with pytest.raises(StaleRevisionError) as exc:
        current.apply_revision(stale)
    assert "3" in str(exc.value) and "10" in str(exc.value)


def test_stale_revision_equal_raises_stale_revision_error() -> None:
    """Applying an equal revision (not strictly greater) raises StaleRevisionError."""
    current = _base_plan(10)
    equal = _base_plan(10)
    with pytest.raises(StaleRevisionError) as exc:
        current.apply_revision(equal)
    assert "not greater than" in str(exc.value)


def test_apply_revision_accepts_strictly_greater_and_recomputes_digest() -> None:
    """A new plan with revision > current succeeds and digest is recomputed."""
    current = _base_plan(5)
    new_plan = current.model_copy(
        update={
            "revision": current.revision + 1,
            "updated_at": datetime.now(tz=UTC),
        }
    )
    applied = current.apply_revision(new_plan)
    assert applied.revision == 6
    # Digest recomputed on the returned plan; compute_digest always clears the
    # digest field before hashing, so recomputing on ``applied`` returns the
    # same stored value.
    assert applied.digest == compute_digest(applied)
    assert applied.digest != ""


def test_apply_revision_bump_by_one_via_model_copy() -> None:
    """Caller bumps revision by 1 via model_copy, apply_revision accepts + digests."""
    current = _base_plan(7)
    new_plan = current.model_copy(update={"revision": current.revision + 1})
    applied = current.apply_revision(new_plan)
    assert applied.revision == 8


def test_revision_monotonic_across_sequential_bumps() -> None:
    plan = _base_plan(0)
    for expected in range(1, 11):
        plan = plan.bump_revision()
        assert plan.revision == expected
