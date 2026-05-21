"""No-leak grep on fit_report.py public error-message strings (Story 29-1, AC-T.8).

AC-T.8 specifies: grep scans all strings returned by StaleFitReportError,
UnknownUnitIdError, and any public emission-path error; asserts neither
"intake" nor "orchestrator" appears in any user-facing message. This file
implements that runtime-error-message scan. Internal identifiers like the
WriterIdentity enum values and Marcus-Orchestrator caller-invariant
docstrings are exempt — AC-T.8 protects user-facing output only.

Enforces R1 amendment 17 / R2 rider S-3 for the 29-1 module surface.
Matches the 31-1 AC-T.14 pattern.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

import pytest

from app.marcus.lesson_plan.digest import compute_digest
from app.marcus.lesson_plan.fit_report import (
    StaleFitReportError,
    UnknownUnitIdError,
    validate_fit_report,
)
from app.marcus.lesson_plan.schema import (
    Dials,
    FitDiagnosis,
    FitReport,
    LearningModel,
    LessonPlan,
    PlanRef,
    PlanUnit,
    ScopeDecision,
)

FORBIDDEN_TOKEN_PATTERN = re.compile(
    r"\b(intake|orchestrator)\b",
    flags=re.IGNORECASE,
)


def _make_plan_and_report() -> tuple[LessonPlan, FitReport]:
    unit = PlanUnit(
        unit_id="gagne-event-1",
        event_type="gagne-event-1",
        source_fitness_diagnosis="placeholder",
        scope_decision=ScopeDecision(
            state="proposed",
            scope="in-scope",
            proposed_by="system",
            _internal_proposed_by="marcus",
        ),
        weather_band="gold",
        modality_ref=None,
        rationale="",
        gaps=[],
        dials=Dials(enrichment=0.0, corroboration=0.0),
    )
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        structure={},
        plan_units=[unit],
        revision=1,
        updated_at=datetime(2026, 4, 18, tzinfo=UTC),
        digest="",
    )
    plan = plan.model_copy(update={"digest": compute_digest(plan)})
    report = FitReport(
        source_ref="tests/fixtures/canonical.md",
        plan_ref=PlanRef(
            lesson_plan_revision=plan.revision,
            lesson_plan_digest=plan.digest,
        ),
        diagnoses=[
            FitDiagnosis(
                unit_id="gagne-event-1",
                fitness="sufficient",
                commentary="ok",
            ),
        ],
        generated_at=datetime(2026, 4, 18, 12, 0, 0, tzinfo=UTC),
        irene_budget_ms=0,
    )
    return plan, report


@pytest.mark.parametrize(
    "scenario",
    ["stale_fit_report_error", "unknown_unit_id_error"],
)
def test_public_error_messages_no_leak(scenario: str) -> None:
    """AC-T.8 — public exception messages are Marcus-duality-clean.

    Parametrized across both domain exceptions (StaleFitReportError,
    UnknownUnitIdError) raised by the fit_report.py public surface.
    """
    plan, _ = _make_plan_and_report()
    if scenario == "stale_fit_report_error":
        bad = FitReport(
            source_ref="x",
            plan_ref=PlanRef(
                lesson_plan_revision=99,
                lesson_plan_digest="d" * 64,
            ),
            diagnoses=[],
            generated_at=datetime(2026, 4, 18, tzinfo=UTC),
            irene_budget_ms=0,
        )
        expected_exc: type[ValueError] = StaleFitReportError
    else:
        bad = FitReport(
            source_ref="x",
            plan_ref=PlanRef(
                lesson_plan_revision=plan.revision,
                lesson_plan_digest=plan.digest,
            ),
            diagnoses=[
                FitDiagnosis(
                    unit_id="gagne-event-99",
                    fitness="sufficient",
                    commentary="missing",
                ),
            ],
            generated_at=datetime(2026, 4, 18, tzinfo=UTC),
            irene_budget_ms=0,
        )
        expected_exc = UnknownUnitIdError

    with pytest.raises(expected_exc) as exc_info:
        validate_fit_report(bad, plan=plan)

    match = FORBIDDEN_TOKEN_PATTERN.search(str(exc_info.value))
    assert match is None, (
        f"Forbidden token {match.group()!r} in "
        f"{expected_exc.__name__} message: {exc_info.value!s}"
    )


