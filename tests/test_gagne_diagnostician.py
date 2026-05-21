"""Tests for Story 29-2 Gagne diagnostician."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.marcus.lesson_plan.digest import compute_digest
from app.marcus.lesson_plan.gagne_diagnostician import (
    DEFAULT_BUDGET_FALLBACK_MODE,
    DuplicateDiagnosisTargetError,
    PriorDeclinedRationale,
    UnsupportedGagneEventTypeError,
    diagnose_lesson_plan,
    diagnose_plan_unit,
)
from app.marcus.lesson_plan.schema import (
    Dials,
    LearningModel,
    LessonPlan,
    PlanUnit,
    ScopeDecision,
)


def _make_plan_unit(
    unit_id: str,
    *,
    weather_band: str = "green",
    scope: str = "in-scope",
    modality_ref: str | None = None,
    source_fitness_diagnosis: str = "Source coverage is acceptable.",
    event_type: str | None = None,
) -> PlanUnit:
    dials = Dials(enrichment=0.0, corroboration=0.0)
    if scope not in {"in-scope", "delegated"}:
        dials = None
    return PlanUnit(
        unit_id=unit_id,
        event_type=event_type or unit_id,
        source_fitness_diagnosis=source_fitness_diagnosis,
        scope_decision=ScopeDecision(
            state="proposed",
            scope=scope,
            proposed_by="system",
            _internal_proposed_by="irene",
        ),
        weather_band=weather_band,
        modality_ref=modality_ref,
        rationale="",
        gaps=[],
        dials=dials,
    )


def _make_plan(units: list[PlanUnit]) -> LessonPlan:
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        structure={},
        plan_units=units,
        revision=3,
        updated_at=datetime.now(tz=UTC),
        digest="",
    )
    return plan.model_copy(update={"digest": compute_digest(plan)})


def test_diagnose_plan_unit_returns_fit_diagnosis() -> None:
    diagnosis = diagnose_plan_unit(_make_plan_unit("gagne-event-1"))
    assert diagnosis.unit_id == "gagne-event-1"
    assert diagnosis.fitness == "sufficient"
    assert diagnosis.recommended_scope_decision == "in-scope"


def test_diagnose_lesson_plan_returns_one_diagnosis_per_unit_in_order() -> None:
    plan = _make_plan(
        [
            _make_plan_unit("gagne-event-1", weather_band="green"),
            _make_plan_unit("gagne-event-2", weather_band="amber"),
            _make_plan_unit("gagne-event-3", weather_band="gray"),
        ]
    )
    report = diagnose_lesson_plan(plan, source_ref="tests/fixtures/trial_corpus/case.md")
    assert [d.unit_id for d in report.diagnoses] == [
        "gagne-event-1",
        "gagne-event-2",
        "gagne-event-3",
    ]
    assert [d.fitness for d in report.diagnoses] == [
        "sufficient",
        "partial",
        "absent",
    ]


def test_duplicate_plan_unit_ids_fail_fast() -> None:
    plan = _make_plan(
        [
            _make_plan_unit("gagne-event-1"),
            _make_plan_unit("gagne-event-1", weather_band="amber"),
        ]
    )
    with pytest.raises(DuplicateDiagnosisTargetError):
        diagnose_lesson_plan(plan, source_ref="tests/fixtures/trial_corpus/case.md")


@pytest.mark.parametrize(
    ("modality_ref", "scope", "expected_fitness"),
    [
        (None, "in-scope", "sufficient"),
        ("slides", "in-scope", "sufficient"),
        ("leader-guide", "delegated", "partial"),
        ("unknown-modality", "in-scope", "absent"),
    ],
)
def test_modality_registry_validation_affects_fit(
    modality_ref: str | None,
    scope: str,
    expected_fitness: str,
) -> None:
    plan = _make_plan(
        [
            _make_plan_unit(
                "gagne-event-1",
                weather_band="green",
                scope=scope,
                modality_ref=modality_ref,
            )
        ]
    )
    report = diagnose_lesson_plan(plan, source_ref="tests/fixtures/trial_corpus/case.md")
    assert report.diagnoses[0].fitness == expected_fitness
    if modality_ref == "unknown-modality":
        assert "not present in MODALITY_REGISTRY" in report.diagnoses[0].commentary


def test_prior_declined_rationale_is_carried_forward() -> None:
    plan = _make_plan(
        [
            _make_plan_unit(
                "gagne-event-4",
                weather_band="gray",
                scope="out-of-scope",
            )
        ]
    )
    report = diagnose_lesson_plan(
        plan,
        source_ref="tests/fixtures/trial_corpus/case.md",
        prior_declined_rationales=[
            PriorDeclinedRationale(
                unit_id="gagne-event-4",
                rationale="Already declined because the source never supports this move.",
            )
        ],
    )
    assert "Prior Declined rationale carried forward" in report.diagnoses[0].commentary
    assert report.diagnoses[0].recommended_scope_decision == "out-of-scope"


def test_unsupported_event_type_rejected() -> None:
    plan = _make_plan(
        [
            _make_plan_unit(
                "custom-unit",
                event_type="custom-event",
            )
        ]
    )
    with pytest.raises(UnsupportedGagneEventTypeError):
        diagnose_lesson_plan(plan, source_ref="tests/fixtures/trial_corpus/case.md")


def test_generated_at_is_timezone_aware_and_plan_ref_is_fresh() -> None:
    plan = _make_plan([_make_plan_unit("gagne-event-1")])
    report = diagnose_lesson_plan(plan, source_ref="tests/fixtures/trial_corpus/case.md")
    assert report.generated_at.tzinfo is not None
    assert report.plan_ref.lesson_plan_revision == plan.revision
    assert report.plan_ref.lesson_plan_digest == plan.digest


def test_diagnostician_is_deterministic_across_replays() -> None:
    plan = _make_plan(
        [
            _make_plan_unit("gagne-event-1", weather_band="green"),
            _make_plan_unit("gagne-event-2", weather_band="amber"),
            _make_plan_unit("gagne-event-3", weather_band="gray", scope="out-of-scope"),
        ]
    )
    baseline = diagnose_lesson_plan(plan, source_ref="tests/fixtures/trial_corpus/case.md")
    for _ in range(9):
        replay = diagnose_lesson_plan(plan, source_ref="tests/fixtures/trial_corpus/case.md")
        assert [
            (d.fitness, d.recommended_scope_decision, d.recommended_weather_band)
            for d in replay.diagnoses
        ] == [
            (d.fitness, d.recommended_scope_decision, d.recommended_weather_band)
            for d in baseline.diagnoses
        ]


def test_summary_only_fallback_contract_activates_on_budget_breach() -> None:
    plan = _make_plan(
        [
            _make_plan_unit(
                "gagne-event-1",
                source_fitness_diagnosis="Detailed diagnostic text.",
            )
        ]
    )
    ticks = iter([0.0, 31.0, 31.0, 32.0])
    report = diagnose_lesson_plan(
        plan,
        source_ref="tests/fixtures/trial_corpus/case.md",
        budget_threshold_ms=30_000,
        fallback_mode=DEFAULT_BUDGET_FALLBACK_MODE,
        time_source=lambda: next(ticks),
    )
    assert report.irene_budget_ms == 31000
    assert report.diagnoses[0].commentary == (
        "gagne-event-1: sufficient; Detailed diagnostic text."
    )


def test_prior_declined_mapping_duplicate_unit_ids_rejected() -> None:
    plan = _make_plan([_make_plan_unit("gagne-event-1")])
    with pytest.raises(DuplicateDiagnosisTargetError):
        diagnose_lesson_plan(
            plan,
            source_ref="tests/fixtures/trial_corpus/case.md",
            prior_declined_rationales=[
                PriorDeclinedRationale(unit_id="gagne-event-1", rationale="a"),
                PriorDeclinedRationale(unit_id="gagne-event-1", rationale="b"),
            ],
        )
