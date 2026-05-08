"""Contract pins for Story 31-4 blueprint producer."""

from __future__ import annotations

import app.marcus.lesson_plan.blueprint_producer as blueprint_producer_module
from app.marcus.lesson_plan.modality_registry import MODALITY_REGISTRY, SCHEMA_VERSION
from app.marcus.lesson_plan.produced_asset import SCHEMA_VERSION as PRODUCED_ASSET_SCHEMA_VERSION


def test_blueprint_registry_backfill_points_at_concrete_producer() -> None:
    entry = MODALITY_REGISTRY["blueprint"]
    assert entry.status == "ready"
    assert (
        entry.producer_class_path
        == "app.marcus.lesson_plan.blueprint_producer.BlueprintProducer"
    )


def test_no_schema_bump_and_public_surface_stays_expected() -> None:
    assert SCHEMA_VERSION == "1.0"
    assert PRODUCED_ASSET_SCHEMA_VERSION == "1.0"
    assert set(blueprint_producer_module.__all__) == {
        "BlueprintProducer",
        "BlueprintScopeError",
        "DEFAULT_BLUEPRINT_OUTPUT_ROOT",
        "HUMAN_REVIEW_SECTION_HEADING",
        "IRENE_REVIEW_MARKER",
        "SIGNOFF_STATUS_MARKER",
        "WRITER_SIGNOFF_MARKER",
        "compose_blueprint_markdown",
        "render_blueprint_body",
    }
