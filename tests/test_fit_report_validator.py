"""Tests for fit_report.validate_fit_report (Story 29-1, AC-T.1/2/3/6/10)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

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


def _make_plan_unit(unit_id: str = "gagne-event-1") -> PlanUnit:
    return PlanUnit(
        unit_id=unit_id,
        event_type=unit_id,
        source_fitness_diagnosis="placeholder diagnosis",
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


def _make_plan(unit_ids: tuple[str, ...] = ("gagne-event-1",)) -> LessonPlan:
    units = [_make_plan_unit(uid) for uid in unit_ids]
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        structure={},
        plan_units=units,
        revision=1,
        updated_at=datetime.now(tz=UTC),
        digest="",
    )
    return plan.model_copy(update={"digest": compute_digest(plan)})


def _make_report(
    plan: LessonPlan,
    *,
    revision_override: int | None = None,
    digest_override: str | None = None,
    diagnosis_unit_ids: tuple[str, ...] = ("gagne-event-1",),
) -> FitReport:
    return FitReport(
        source_ref="tests/fixtures/trial_corpus/canonical.md",
        plan_ref=PlanRef(
            lesson_plan_revision=(
                revision_override if revision_override is not None else plan.revision
            ),
            lesson_plan_digest=(
                digest_override if digest_override is not None else plan.digest
            ),
        ),
        diagnoses=[
            FitDiagnosis(
                unit_id=uid,
                fitness="sufficient",
                commentary="ok",
            )
            for uid in diagnosis_unit_ids
        ],
        generated_at=datetime.now(tz=UTC),
        irene_budget_ms=1234,
    )


# ---------------------------------------------------------------------------
# AC-T.1 — validator happy path (three input forms)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("input_form", ["instance", "dict", "json_str"])
def test_validate_fit_report_fresh_plan_succeeds(input_form: str) -> None:
    """AC-T.1 — validator accepts FitReport, dict, or JSON str inputs."""
    plan = _make_plan()
    report = _make_report(plan)

    if input_form == "instance":
        passed: FitReport | dict | str = report
    elif input_form == "dict":
        passed = report.model_dump(mode="json")
    else:
        passed = report.model_dump_json()

    result = validate_fit_report(passed, plan=plan)
    assert isinstance(result, FitReport)
    assert result.plan_ref.lesson_plan_revision == plan.revision
    assert result.plan_ref.lesson_plan_digest == plan.digest


# ---------------------------------------------------------------------------
# AC-T.2 — stale-revision / stale-digest rejection + AC-B.2.1 precedence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("stale_revision", "stale_digest", "unit_ids_unknown_in_plan"),
    [
        (True, False, False),
        (False, True, False),
        (True, True, False),
        # Q-2 precedence: stale + unknown-unit-id simultaneously → staleness wins.
        (True, True, True),
    ],
    ids=["stale-rev", "stale-digest", "stale-both", "stale-and-unknown-precedence"],
)
def test_validate_fit_report_rejects_stale(
    stale_revision: bool,
    stale_digest: bool,
    unit_ids_unknown_in_plan: bool,
) -> None:
    """AC-T.2 — staleness rejection with AC-B.2.1 precedence check."""
    plan = _make_plan()
    diagnosis_ids = (
        ("gagne-event-99",) if unit_ids_unknown_in_plan else ("gagne-event-1",)
    )
    report = _make_report(
        plan,
        revision_override=(plan.revision + 7) if stale_revision else None,
        digest_override="d" * 64 if stale_digest else None,
        diagnosis_unit_ids=diagnosis_ids,
    )

    with pytest.raises(StaleFitReportError) as exc_info:
        validate_fit_report(report, plan=plan)

    msg = str(exc_info.value)
    if stale_revision:
        assert str(plan.revision) in msg
    if stale_digest:
        assert plan.digest in msg


# ---------------------------------------------------------------------------
# AC-T.3 — unknown-unit-id rejection (plan_ref fresh)
# ---------------------------------------------------------------------------


def test_validate_fit_report_rejects_unknown_unit_id() -> None:
    """AC-T.3 — fresh plan_ref + unknown unit_id → UnknownUnitIdError."""
    plan = _make_plan()
    report = _make_report(plan, diagnosis_unit_ids=("gagne-event-99",))

    with pytest.raises(UnknownUnitIdError) as exc_info:
        validate_fit_report(report, plan=plan)

    assert "gagne-event-99" in str(exc_info.value)


def test_unknown_unit_id_error_does_not_leak_full_plan_id_list() -> None:
    """29-1 #4-leak (party-mode 2026-04-19): error names ONLY the unknown ids
    plus a count of total plan units; full plan-unit identifier list MUST NOT
    appear (defense-in-depth against sensitive identifiers in non-Gagne plans).
    """
    plan = _make_plan()  # has at least one known plan unit
    known_ids = [pu.unit_id for pu in plan.plan_units]
    report = _make_report(plan, diagnosis_unit_ids=("gagne-event-99",))

    with pytest.raises(UnknownUnitIdError) as exc_info:
        validate_fit_report(report, plan=plan)

    msg = str(exc_info.value)
    # Unknown id IS named.
    assert "gagne-event-99" in msg
    # Count of plan units is reported (parenthesized).
    assert f"({len(known_ids)} unit_ids in plan)" in msg
    # Known plan-unit ids MUST NOT appear in the message.
    for known in known_ids:
        assert known not in msg, (
            f"#4-leak regression: error message leaked known plan_unit_id "
            f"{known!r}; got: {msg}"
        )


# ---------------------------------------------------------------------------
# AC-T.6 — naive-datetime rejected at 31-1 Pydantic surface
# ---------------------------------------------------------------------------


def test_fit_report_rejects_naive_generated_at() -> None:
    """AC-T.6 — naive datetime raises Pydantic ValidationError at construction.

    emit_fit_report is NOT reached because the Pydantic layer rejects the
    value before any 29-1 wrapper code runs.
    """
    plan = _make_plan()
    with pytest.raises(ValidationError):
        FitReport(
            source_ref="tests/fixtures/x.md",
            plan_ref=PlanRef(
                lesson_plan_revision=plan.revision,
                lesson_plan_digest=plan.digest,
            ),
            diagnoses=[],
            generated_at=datetime(2026, 4, 18),
            irene_budget_ms=0,
        )


# ---------------------------------------------------------------------------
# AC-T.10 — validator idempotency perf-shape pin (W-2 rider)
# ---------------------------------------------------------------------------


def test_validate_fit_report_does_not_re_parse_instance_input() -> None:
    """AC-T.10 — already-validated FitReport does NOT re-trigger model_validate.

    Protects against silent perf regressions where a defensive refactor adds
    a re-parse step. The idempotency invariant is AC-B.2.2.
    """
    plan = _make_plan()
    report = _make_report(plan)

    with (
        patch.object(FitReport, "model_validate") as mock_validate,
        patch.object(FitReport, "model_validate_json") as mock_validate_json,
    ):
        result = validate_fit_report(report, plan=plan)

    assert result is report
    assert mock_validate.call_count == 0
    assert mock_validate_json.call_count == 0
