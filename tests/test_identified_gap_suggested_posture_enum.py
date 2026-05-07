"""SF-12 — ``IdentifiedGap.suggested_posture`` Literal enum pin test.

Asserts the three postures ``embellish | corroborate | gap_fill`` are
pinned and cannot drift without an explicit schema version bump. The
three values map to the three operator-memory parameter families
(enrichment / evidence-bolster / derivative-artifact gap-filling) per the
schema docstring.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.schema import IdentifiedGap


@pytest.mark.parametrize("posture", ["embellish", "corroborate", "gap_fill"])
def test_suggested_posture_accepts_three_valid_values(posture: str) -> None:
    gap = IdentifiedGap(
        gap_id="g1",
        description="test description",
        suggested_posture=posture,  # type: ignore[arg-type]
    )
    assert gap.suggested_posture == posture


@pytest.mark.parametrize("posture", ["defer", "challenge", "", "enrich", "corroborate-strong"])
def test_suggested_posture_rejects_non_pinned_values(posture: str) -> None:
    with pytest.raises(ValidationError):
        IdentifiedGap(
            gap_id="g1",
            description="test description",
            suggested_posture=posture,  # type: ignore[arg-type]
        )


def test_suggested_posture_rejects_none() -> None:
    """Posture is required — ``None`` is not accepted (not an Optional field)."""
    with pytest.raises(ValidationError):
        IdentifiedGap(
            gap_id="g1",
            description="test description",
            suggested_posture=None,  # type: ignore[arg-type]
        )
