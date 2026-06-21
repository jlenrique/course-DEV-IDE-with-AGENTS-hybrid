from __future__ import annotations

import pytest

from app.models.perception import PerceptionArtifact
from scripts.utilities.reading_path_classifier import (
    REQUIRED_PERCEPTION_FIELDS,
    ReadingPathClassificationError,
    classify_reading_path,
    ordered_element_keys_for_reading_path,
)


def _artifact(elements: list[dict[str, object]], **overrides: object) -> PerceptionArtifact:
    payload = {
        "slide_id": "slide-01",
        "confidence": "HIGH",
        "coverage": "perceived",
        "visual_elements": elements,
        "extracted_text": "",
        "layout_description": "",
        "slide_title": "Fixture",
    }
    payload.update(overrides)
    return PerceptionArtifact.model_validate(payload)


def test_classifier_reads_only_fields_on_rich_perception_artifact() -> None:
    assert set(PerceptionArtifact.model_fields) >= REQUIRED_PERCEPTION_FIELDS


def test_anti_vacuity_z_pattern_beats_dom_or_top_down_default() -> None:
    artifact = _artifact(
        [
            {
                "id": "body",
                "kind": "text",
                "label": "body copy",
                "bbox": [0.08, 0.55, 0.42, 0.78],
            },
            {
                "id": "hero",
                "kind": "visual",
                "label": "right hero image",
                "bbox": [0.58, 0.10, 0.90, 0.42],
            },
            {
                "id": "headline",
                "kind": "headline",
                "label": "top left headline",
                "bbox": [0.05, 0.05, 0.45, 0.18],
            },
            {
                "id": "cta",
                "kind": "callout",
                "label": "bottom right callout",
                "bbox": [0.58, 0.65, 0.90, 0.85],
            },
        ],
        layout_description="Z layout with headline, hero image, body, and callout.",
    )

    naive_order = [str(item["id"]) for item in artifact.visual_elements]

    assert classify_reading_path(artifact) == "z_pattern"
    assert ordered_element_keys_for_reading_path(artifact) == [
        "headline",
        "hero",
        "body",
        "cta",
    ]
    assert ordered_element_keys_for_reading_path(artifact) != naive_order


def test_sequence_numbered_uses_numbered_cadence() -> None:
    artifact = _artifact(
        [
            {
                "id": "first",
                "kind": "step",
                "label": "1. Intake",
                "bbox": [0.10, 0.15, 0.30, 0.30],
            },
            {
                "id": "second",
                "kind": "step",
                "label": "2. Analyze",
                "bbox": [0.38, 0.15, 0.58, 0.30],
            },
            {
                "id": "third",
                "kind": "step",
                "label": "3. Route",
                "bbox": [0.66, 0.15, 0.86, 0.30],
            },
        ]
    )

    assert classify_reading_path(artifact) == "sequence_numbered"
    assert ordered_element_keys_for_reading_path(artifact) == ["first", "second", "third"]


def test_classifier_fails_loud_when_perceived_geometry_is_absent() -> None:
    artifact = _artifact([{"id": "metric", "kind": "callout", "text": "metric"}])

    with pytest.raises(ReadingPathClassificationError):
        classify_reading_path(artifact)


def test_non_numeric_bbox_skips_to_controlled_failure_not_raw_valueerror() -> None:
    # P2-4a T11 (party-mode 5/5, Cluster 3b): a non-numeric bbox entry must be
    # SKIPPED (treated as no geometry) and surface the controlled
    # ReadingPathClassificationError — NOT a raw ValueError escaping float().
    # ReadingPathClassificationError is a ValueError subclass, so a raw
    # float() ValueError would NOT match this raises() and the test would fail.
    artifact = _artifact(
        [{"id": "bad", "kind": "text", "label": "bad", "bbox": ["a", "b", "c", "d"]}]
    )

    with pytest.raises(ReadingPathClassificationError):
        classify_reading_path(artifact)
