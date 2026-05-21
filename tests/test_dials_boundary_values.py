"""MF-5 — AC-B.3 ``Dials`` boundary-value coverage (Acceptance Auditor gap).

AC-B.3 was zero-coverage at G5 close — the ``Dials`` constraints
(`0.0 <= enrichment <= 1.0`, `0.0 <= corroboration <= 1.0`, `None`
accepted) had no parametrized boundary tests. This file fills that gap:

    - Accepts: 0.0, 1.0, 0.5, None on both dials independently.
    - Rejects: -0.01, 1.01, -1.0, 2.0 on both dials.
    - Rejects: NaN, +inf, -inf on both dials.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.schema import Dials

# ---------------------------------------------------------------------------
# Accept cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0.0, 0.5, 1.0, None])
def test_enrichment_accepts_valid_and_none(value: float | None) -> None:
    dials = Dials(enrichment=value, corroboration=None)
    assert dials.enrichment == value


@pytest.mark.parametrize("value", [0.0, 0.5, 1.0, None])
def test_corroboration_accepts_valid_and_none(value: float | None) -> None:
    dials = Dials(enrichment=None, corroboration=value)
    assert dials.corroboration == value


def test_both_dials_unset_accepted() -> None:
    dials = Dials()
    assert dials.enrichment is None
    assert dials.corroboration is None


def test_both_dials_set_to_valid_accepted() -> None:
    dials = Dials(enrichment=0.3, corroboration=0.8)
    assert dials.enrichment == 0.3
    assert dials.corroboration == 0.8


# ---------------------------------------------------------------------------
# Reject out-of-range
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [-0.01, 1.01, -1.0, 2.0])
def test_enrichment_rejects_out_of_range(value: float) -> None:
    with pytest.raises(ValidationError):
        Dials(enrichment=value, corroboration=None)


@pytest.mark.parametrize("value", [-0.01, 1.01, -1.0, 2.0])
def test_corroboration_rejects_out_of_range(value: float) -> None:
    with pytest.raises(ValidationError):
        Dials(enrichment=None, corroboration=value)


# ---------------------------------------------------------------------------
# Reject NaN / inf
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), float("-inf")]
)
def test_enrichment_rejects_nan_and_inf(value: float) -> None:
    with pytest.raises(ValidationError):
        Dials(enrichment=value, corroboration=None)


@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), float("-inf")]
)
def test_corroboration_rejects_nan_and_inf(value: float) -> None:
    with pytest.raises(ValidationError):
        Dials(enrichment=None, corroboration=value)
