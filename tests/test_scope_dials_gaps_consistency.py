"""AC-T.12 — scope-state ↔ dials/gaps consistency validator.

Rules:
    - ``scope == in-scope`` AND ``gaps not empty`` → valid.
    - ``scope != in-scope`` AND ``gaps not empty`` → rejected.
    - ``scope in {in-scope, delegated}`` AND ``dials set`` → valid.
    - ``scope in {out-of-scope, blueprint}`` AND ``dials set`` → rejected.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.schema import Dials, IdentifiedGap, PlanUnit, ScopeDecision


def _sd(scope: str) -> ScopeDecision:
    return ScopeDecision(
        state="proposed",
        scope=scope,  # type: ignore[arg-type]
        proposed_by="system",
        _internal_proposed_by="marcus",
    )


def _gap() -> IdentifiedGap:
    return IdentifiedGap(gap_id="g1", description="x", suggested_posture="embellish")


def _unit(
    *,
    scope: str,
    gaps: list[IdentifiedGap] | None = None,
    dials: Dials | None = None,
) -> PlanUnit:
    return PlanUnit(
        unit_id="gagne-event-3",
        event_type="gagne-event-3",
        source_fitness_diagnosis="ok",
        scope_decision=_sd(scope),
        weather_band="gold",
        rationale="",
        gaps=gaps or [],
        dials=dials,
    )


def test_in_scope_with_gaps_is_valid() -> None:
    pu = _unit(scope="in-scope", gaps=[_gap()])
    assert pu.gaps


@pytest.mark.parametrize("bad_scope", ["out-of-scope", "delegated", "blueprint"])
def test_non_in_scope_with_gaps_rejected(bad_scope: str) -> None:
    with pytest.raises(ValidationError) as exc:
        _unit(scope=bad_scope, gaps=[_gap()])
    assert "gaps only valid on in-scope" in str(exc.value)


@pytest.mark.parametrize("ok_scope", ["in-scope", "delegated"])
def test_dials_valid_on_in_or_delegated(ok_scope: str) -> None:
    pu = _unit(scope=ok_scope, dials=Dials(enrichment=0.5, corroboration=0.5))
    assert pu.dials is not None


@pytest.mark.parametrize("bad_scope", ["out-of-scope", "blueprint"])
def test_dials_rejected_on_out_of_scope_or_blueprint(bad_scope: str) -> None:
    with pytest.raises(ValidationError) as exc:
        _unit(scope=bad_scope, dials=Dials(enrichment=0.1))
    assert "dials only valid" in str(exc.value)
