"""Tests for Story 31-5 Quinn-R two-branch gate."""

from __future__ import annotations

import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan.blueprint_coauthor import coauthor_blueprint
from app.marcus.lesson_plan.blueprint_producer import BlueprintProducer
from app.marcus.lesson_plan.digest import compute_digest
from app.marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext
from app.marcus.lesson_plan.quinn_r_gate import (
    QuinnRGateError,
    emit_quinn_r_gate_artifact,
    evaluate_quinn_r_two_branch_gate,
    extract_prior_declined_rationales,
)
from app.marcus.lesson_plan.schema import LearningModel, LessonPlan, PlanUnit, ScopeDecision

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def output_root() -> Path:
    path = REPO_ROOT / "_bmad-output" / "test-artifacts" / "quinn-r-gate" / uuid.uuid4().hex
    yield path
    shutil.rmtree(path, ignore_errors=True)


def _make_plan_unit(
    unit_id: str,
    *,
    scope: str,
    rationale: str = "Default rationale.",
    modality_ref: str | None = None,
) -> PlanUnit:
    return PlanUnit(
        unit_id=unit_id,
        event_type=unit_id,
        source_fitness_diagnosis="Source status for this unit.",
        scope_decision=ScopeDecision(
            state="proposed",
            scope=scope,
            proposed_by="system",
            _internal_proposed_by="marcus",
        ),
        weather_band="gray" if scope in {"blueprint", "out-of-scope"} else "green",
        modality_ref=modality_ref,
        rationale=rationale,
        gaps=[],
        dials=None,
    )


def _make_plan(*units: PlanUnit) -> LessonPlan:
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        structure={},
        plan_units=list(units),
        revision=7,
        updated_at=datetime.now(tz=UTC),
        digest="",
    )
    return plan.model_copy(update={"digest": compute_digest(plan)})


def _make_asset(unit_id: str) -> ProducedAsset:
    return ProducedAsset(
        asset_ref=f"asset-{unit_id}@7",
        modality_ref="slides",
        source_plan_unit_id=unit_id,
        asset_path=f"_bmad-output/test-artifacts/assets/{unit_id}@7.md",
        fulfills=f"{unit_id}@7",
    )


def test_quinn_r_gate_imports_and_returns_typed_result() -> None:
    unit = _make_plan_unit("gagne-event-1", scope="in-scope")
    plan = _make_plan(unit)
    asset = _make_asset(unit.unit_id)

    result = evaluate_quinn_r_two_branch_gate(
        plan,
        produced_assets=[asset],
        quality_passed_asset_refs={asset.asset_ref},
    )

    assert result.passed is True
    assert result.unit_verdicts[0].unit_id == unit.unit_id


def test_non_blueprint_unit_passes_with_quality_approved_asset() -> None:
    unit = _make_plan_unit("gagne-event-2", scope="in-scope")
    plan = _make_plan(unit)
    asset = _make_asset(unit.unit_id)

    result = evaluate_quinn_r_two_branch_gate(
        plan,
        produced_assets=[asset],
        quality_passed_asset_refs={asset.asset_ref},
    )

    verdict = result.unit_verdicts[0]
    assert verdict.branch == "produced-asset"
    assert verdict.passed is True
    assert verdict.asset_ref == asset.asset_ref


def test_non_blueprint_unit_fails_without_quality_approval() -> None:
    unit = _make_plan_unit("gagne-event-3", scope="delegated")
    plan = _make_plan(unit)
    asset = _make_asset(unit.unit_id)

    result = evaluate_quinn_r_two_branch_gate(plan, produced_assets=[asset])

    verdict = result.unit_verdicts[0]
    assert verdict.branch == "produced-asset"
    assert verdict.passed is False
    assert "explicitly marked quality-passed" in verdict.reason


def test_blueprint_unit_requires_completed_signoff(output_root: Path) -> None:
    producer = BlueprintProducer(output_root=output_root / "drafts")
    blueprint_unit = _make_plan_unit(
        "gagne-event-4",
        scope="blueprint",
        modality_ref="blueprint",
        rationale="Needs a blueprint branch.",
    )
    context = ProductionContext(lesson_plan_revision=7, lesson_plan_digest="digest-31-5")
    asset = producer.produce(blueprint_unit, context)
    signed_unit = coauthor_blueprint(
        blueprint_unit,
        asset,
        irene_commentary="Irene approves the branch.",
        writer_commentary="Writer approves the branch.",
        signoff_root=output_root / "signoffs",
        signed_at=datetime(2026, 4, 19, 12, 0, tzinfo=UTC),
    )

    passed_result = evaluate_quinn_r_two_branch_gate(_make_plan(signed_unit))
    failed_result = evaluate_quinn_r_two_branch_gate(_make_plan(blueprint_unit))

    assert passed_result.unit_verdicts[0].branch == "blueprint-signoff"
    assert passed_result.unit_verdicts[0].passed is True
    assert failed_result.unit_verdicts[0].passed is False


def test_out_of_scope_unit_emits_declined_carry_forward_entry() -> None:
    unit = _make_plan_unit(
        "gagne-event-5",
        scope="out-of-scope",
        rationale="Already settled as out of scope for this run.",
    )
    result = evaluate_quinn_r_two_branch_gate(_make_plan(unit))

    verdict = result.unit_verdicts[0]
    assert verdict.branch == "declined-audit"
    assert verdict.passed is True
    carry_forward = extract_prior_declined_rationales(result)
    assert carry_forward[0].unit_id == unit.unit_id
    assert carry_forward[0].rationale == unit.rationale


def test_out_of_scope_unit_without_rationale_fails() -> None:
    unit = _make_plan_unit("gagne-event-6", scope="out-of-scope", rationale="")
    result = evaluate_quinn_r_two_branch_gate(_make_plan(unit))

    verdict = result.unit_verdicts[0]
    assert verdict.branch == "declined-audit"
    assert verdict.passed is False
    assert "must preserve a verbatim Declined rationale" in verdict.reason


def test_missing_scope_decision_is_rejected() -> None:
    unit = PlanUnit(
        unit_id="gagne-event-7",
        event_type="gagne-event-7",
        source_fitness_diagnosis="Missing scope.",
        scope_decision=None,
        weather_band="amber",
        modality_ref=None,
        rationale="",
        gaps=[],
        dials=None,
    )
    with pytest.raises(QuinnRGateError):
        evaluate_quinn_r_two_branch_gate(_make_plan(unit))


def test_declined_carry_forward_entries_preserve_plan_order() -> None:
    plan = _make_plan(
        _make_plan_unit("gagne-event-8", scope="out-of-scope", rationale="First."),
        _make_plan_unit("gagne-event-9", scope="out-of-scope", rationale="Second."),
    )
    result = evaluate_quinn_r_two_branch_gate(plan)

    assert [entry.unit_id for entry in extract_prior_declined_rationales(result)] == [
        "gagne-event-8",
        "gagne-event-9",
    ]


def test_gate_artifact_emission_is_deterministic(output_root: Path) -> None:
    unit = _make_plan_unit(
        "gagne-event-10",
        scope="out-of-scope",
        rationale="Stable rationale for deterministic JSON.",
    )
    result = evaluate_quinn_r_two_branch_gate(
        _make_plan(unit),
        evaluated_at=datetime(2026, 4, 19, 13, 0, tzinfo=UTC),
    )

    first_path = emit_quinn_r_gate_artifact(result, output_root=output_root)
    first_text = (REPO_ROOT / first_path).read_text(encoding="utf-8")

    second_path = emit_quinn_r_gate_artifact(result, output_root=output_root)
    second_text = (REPO_ROOT / second_path).read_text(encoding="utf-8")

    assert second_path == first_path
    assert second_text == first_text

