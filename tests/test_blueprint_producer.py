"""Tests for Story 31-4 blueprint producer."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest

from app.marcus.lesson_plan.blueprint_producer import (
    HUMAN_REVIEW_SECTION_HEADING,
    IRENE_REVIEW_MARKER,
    WRITER_SIGNOFF_MARKER,
    BlueprintProducer,
    BlueprintScopeError,
)
from app.marcus.lesson_plan.produced_asset import ProductionContext
from app.marcus.lesson_plan.schema import Dials, PlanUnit, ScopeDecision

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def output_root() -> Path:
    path = (
        REPO_ROOT
        / "_bmad-output"
        / "test-artifacts"
        / "blueprint-producer"
        / uuid.uuid4().hex
    )
    yield path
    shutil.rmtree(path, ignore_errors=True)


def _make_plan_unit(
    unit_id: str = "gagne-event-7",
    *,
    scope: str = "blueprint",
    modality_ref: str | None = "blueprint",
    rationale: str = "The source needs a human-authored blueprint draft.",
) -> PlanUnit:
    dials = (
        Dials(enrichment=0.0, corroboration=0.0)
        if scope in {"in-scope", "delegated"}
        else None
    )
    return PlanUnit(
        unit_id=unit_id,
        event_type=unit_id,
        source_fitness_diagnosis="The source supports a structured blueprint draft.",
        scope_decision=ScopeDecision(
            state="proposed",
            scope=scope,
            proposed_by="system",
            _internal_proposed_by="marcus",
        ),
        weather_band="gray",
        modality_ref=modality_ref,
        rationale=rationale,
        gaps=[],
        dials=dials,
    )


def _make_context() -> ProductionContext:
    return ProductionContext(
        lesson_plan_revision=4,
        lesson_plan_digest="digest-abc123",
    )


def test_blueprint_producer_imports_and_instantiates(output_root: Path) -> None:
    producer = BlueprintProducer(output_root=output_root)
    assert producer.modality_ref == "blueprint"
    assert producer.status == "ready"


def test_produce_writes_markdown_and_returns_produced_asset(output_root: Path) -> None:
    producer = BlueprintProducer(output_root=output_root)
    unit = _make_plan_unit()
    context = _make_context()

    asset = producer.produce(unit, context)

    written_path = REPO_ROOT / asset.asset_path
    assert written_path.exists()
    assert asset.modality_ref == "blueprint"
    assert asset.source_plan_unit_id == unit.unit_id
    assert asset.fulfills == f"{unit.unit_id}@{context.lesson_plan_revision}"
    assert asset.created_at.tzinfo is not None


def test_non_blueprint_scope_is_rejected(output_root: Path) -> None:
    producer = BlueprintProducer(output_root=output_root)
    with pytest.raises(BlueprintScopeError):
        producer.produce(_make_plan_unit(scope="delegated"), _make_context())


def test_conflicting_modality_ref_is_rejected(output_root: Path) -> None:
    producer = BlueprintProducer(output_root=output_root)
    with pytest.raises(BlueprintScopeError):
        producer.produce(
            _make_plan_unit(modality_ref="slides"),
            _make_context(),
        )


def test_rendered_markdown_contains_review_markers(output_root: Path) -> None:
    producer = BlueprintProducer(output_root=output_root)
    asset = producer.produce(_make_plan_unit(), _make_context())
    markdown = (REPO_ROOT / asset.asset_path).read_text(encoding="utf-8")
    assert HUMAN_REVIEW_SECTION_HEADING in markdown
    assert IRENE_REVIEW_MARKER in markdown
    assert WRITER_SIGNOFF_MARKER in markdown


def test_replay_is_deterministic_for_body_and_asset_path(output_root: Path) -> None:
    producer = BlueprintProducer(output_root=output_root)
    unit = _make_plan_unit()
    context = _make_context()

    first = producer.produce(unit, context)
    first_markdown = (REPO_ROOT / first.asset_path).read_text(encoding="utf-8")

    second = producer.produce(unit, context)
    second_markdown = (REPO_ROOT / second.asset_path).read_text(encoding="utf-8")

    assert second.asset_path == first.asset_path
    assert second.fulfills == first.fulfills
    assert second_markdown == first_markdown


def test_injected_body_renderer_overrides_draft_body_not_review_markers(
    output_root: Path,
) -> None:
    def custom_body_renderer(plan_unit: PlanUnit, context: ProductionContext) -> str:
        return (
            "### Draft Blueprint\n"
            f"Custom body for {plan_unit.unit_id} at revision "
            f"{context.lesson_plan_revision}."
        )

    producer = BlueprintProducer(
        output_root=output_root,
        body_renderer=custom_body_renderer,
    )
    asset = producer.produce(_make_plan_unit(), _make_context())
    markdown = (REPO_ROOT / asset.asset_path).read_text(encoding="utf-8")
    assert "Custom body for gagne-event-7 at revision 4." in markdown
    assert HUMAN_REVIEW_SECTION_HEADING in markdown
