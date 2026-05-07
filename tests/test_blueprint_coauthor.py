"""Tests for Story 29-3 blueprint co-author protocol."""

from __future__ import annotations

import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan.blueprint_coauthor import (
    IRENE_APPROVED_MARKER,
    WRITER_APPROVED_MARKER,
    BlueprintCoauthorError,
    coauthor_blueprint,
)
from app.marcus.lesson_plan.blueprint_producer import BlueprintProducer
from app.marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit, ScopeDecision

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def output_roots() -> tuple[Path, Path]:
    base = REPO_ROOT / "_bmad-output" / "test-artifacts" / "blueprint-coauthor" / uuid.uuid4().hex
    blueprint_root = base / "drafts"
    signoff_root = base / "signoffs"
    yield blueprint_root, signoff_root
    shutil.rmtree(base, ignore_errors=True)


def _make_plan_unit() -> PlanUnit:
    return PlanUnit(
        unit_id="gagne-event-8",
        event_type="gagne-event-8",
        source_fitness_diagnosis="Source supports a blueprint draft.",
        scope_decision=ScopeDecision(
            state="proposed",
            scope="blueprint",
            proposed_by="system",
            _internal_proposed_by="marcus",
        ),
        weather_band="gray",
        modality_ref="blueprint",
        rationale="The draft needs Irene plus a writer to lock the branch.",
        gaps=[],
        dials=None,
    )


def _make_blueprint_asset(output_root: Path) -> tuple[PlanUnit, ProducedAsset]:
    producer = BlueprintProducer(output_root=output_root)
    unit = _make_plan_unit()
    asset = producer.produce(
        unit,
        ProductionContext(
            lesson_plan_revision=5,
            lesson_plan_digest="digest-blueprint-coauthor",
        ),
    )
    return unit, asset


def test_coauthor_blueprint_imports_and_returns_updated_plan_unit(
    output_roots: tuple[Path, Path],
) -> None:
    blueprint_root, signoff_root = output_roots
    unit, asset = _make_blueprint_asset(blueprint_root)

    updated = coauthor_blueprint(
        unit,
        asset,
        irene_commentary="Irene approves the blueprint structure.",
        writer_commentary="Writer approves this draft as the co-author baseline.",
        signoff_root=signoff_root,
    )

    assert updated.unit_id == unit.unit_id
    assert updated.blueprint_signoff is not None


def test_coauthor_blueprint_writes_signoff_artifact_and_pointer(
    output_roots: tuple[Path, Path],
) -> None:
    blueprint_root, signoff_root = output_roots
    unit, asset = _make_blueprint_asset(blueprint_root)
    signed_at = datetime(2026, 4, 18, 18, 30, tzinfo=UTC)

    updated = coauthor_blueprint(
        unit,
        asset,
        irene_commentary="Irene confirms the draft is instructionally coherent.",
        writer_commentary="Writer signs off on using this draft for the branch.",
        signoff_root=signoff_root,
        signed_at=signed_at,
    )

    assert updated.blueprint_signoff is not None
    pointer = updated.blueprint_signoff
    assert pointer.blueprint_asset_path == asset.asset_path
    assert pointer.irene_review_complete is True
    assert pointer.writer_signoff_complete is True
    assert pointer.signed_at == signed_at

    signoff_path = REPO_ROOT / pointer.signoff_artifact_path
    assert signoff_path.exists()
    text = signoff_path.read_text(encoding="utf-8")
    assert IRENE_APPROVED_MARKER in text
    assert WRITER_APPROVED_MARKER in text


def test_non_blueprint_asset_is_rejected(
    output_roots: tuple[Path, Path],
) -> None:
    _, signoff_root = output_roots
    unit = _make_plan_unit()
    asset = ProducedAsset(
        asset_ref="slides-gagne-event-8@5",
        modality_ref="slides",
        source_plan_unit_id=unit.unit_id,
        asset_path="_bmad-output/artifacts/slides/gagne-event-8@5.md",
        fulfills="gagne-event-8@5",
    )

    with pytest.raises(BlueprintCoauthorError):
        coauthor_blueprint(
            unit,
            asset,
            irene_commentary="Irene note.",
            writer_commentary="Writer note.",
            signoff_root=signoff_root,
        )


def test_asset_for_wrong_unit_is_rejected(
    output_roots: tuple[Path, Path],
) -> None:
    blueprint_root, signoff_root = output_roots
    unit, asset = _make_blueprint_asset(blueprint_root)
    wrong_unit = unit.model_copy(update={"unit_id": "gagne-event-9"})

    with pytest.raises(BlueprintCoauthorError):
        coauthor_blueprint(
            wrong_unit,
            asset,
            irene_commentary="Irene note.",
            writer_commentary="Writer note.",
            signoff_root=signoff_root,
        )


def test_non_blueprint_plan_unit_is_rejected(
    output_roots: tuple[Path, Path],
) -> None:
    blueprint_root, signoff_root = output_roots
    unit, asset = _make_blueprint_asset(blueprint_root)
    non_blueprint_unit = unit.model_copy(
        update={
            "scope_decision": ScopeDecision(
                state="proposed",
                scope="delegated",
                proposed_by="system",
                _internal_proposed_by="marcus",
            ),
            "modality_ref": "blueprint",
        }
    )

    with pytest.raises(BlueprintCoauthorError):
        coauthor_blueprint(
            non_blueprint_unit,
            asset,
            irene_commentary="Irene note.",
            writer_commentary="Writer note.",
            signoff_root=signoff_root,
        )


def test_missing_review_marker_is_rejected(
    output_roots: tuple[Path, Path],
) -> None:
    blueprint_root, signoff_root = output_roots
    unit, asset = _make_blueprint_asset(blueprint_root)
    asset_path = REPO_ROOT / asset.asset_path
    text = asset_path.read_text(encoding="utf-8").replace("- [ ] Writer sign-off complete", "")
    asset_path.write_text(text, encoding="utf-8")

    with pytest.raises(BlueprintCoauthorError):
        coauthor_blueprint(
            unit,
            asset,
            irene_commentary="Irene note.",
            writer_commentary="Writer note.",
            signoff_root=signoff_root,
        )


def test_signoff_path_is_deterministic_for_fixed_timestamp(
    output_roots: tuple[Path, Path],
) -> None:
    blueprint_root, signoff_root = output_roots
    unit, asset = _make_blueprint_asset(blueprint_root)
    signed_at = datetime(2026, 4, 18, 20, 15, tzinfo=UTC)

    first = coauthor_blueprint(
        unit,
        asset,
        irene_commentary="Irene deterministic note.",
        writer_commentary="Writer deterministic note.",
        signoff_root=signoff_root,
        signed_at=signed_at,
    )
    second = coauthor_blueprint(
        unit,
        asset,
        irene_commentary="Irene deterministic note.",
        writer_commentary="Writer deterministic note.",
        signoff_root=signoff_root,
        signed_at=signed_at,
    )

    assert first.blueprint_signoff is not None
    assert second.blueprint_signoff is not None
    assert (
        first.blueprint_signoff.signoff_artifact_path
        == second.blueprint_signoff.signoff_artifact_path
    )
    assert first.blueprint_signoff.signed_at == second.blueprint_signoff.signed_at
