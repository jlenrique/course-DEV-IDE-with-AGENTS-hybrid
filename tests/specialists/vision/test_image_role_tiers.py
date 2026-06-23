from __future__ import annotations

import pytest

from app.models.perception import PerceptionArtifact
from scripts.utilities.image_role_scoring import (
    fold_scored_tier,
    score_image_role_agreement,
    tier_rubric_metadata,
)
from scripts.utilities.reading_path_classifier import with_classified_reading_path


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


def test_s2_backfills_pure_decorative_role_tier_1() -> None:
    classified = with_classified_reading_path(
        _artifact(
            [
                {
                    "id": "title",
                    "kind": "text",
                    "label": "Design for the encounter",
                    "bbox": [0.10, 0.10, 0.56, 0.20],
                },
                {
                    "id": "wash",
                    "kind": "decorative background image",
                    "label": "",
                    "bbox": [0.00, 0.00, 1.00, 1.00],
                },
            ],
            layout_description="Decorative edge-bleed wash behind text.",
        )
    )

    assert classified.image_roles == ["1", "1"]


def test_s2_photo_backfills_supporting_role_tier_2() -> None:
    classified = with_classified_reading_path(
        _artifact(
            [
                {
                    "id": "copy",
                    "kind": "text",
                    "label": "Teams need time to coordinate.",
                    "bbox": [0.08, 0.20, 0.42, 0.58],
                },
                {
                    "id": "clinic",
                    "kind": "photo",
                    "label": "clinic hallway",
                    "bbox": [0.55, 0.12, 0.92, 0.78],
                },
            ],
            layout_description="Text beside supporting photo.",
        )
    )

    assert classified.image_roles == ["1", "2"]


def test_s2_chart_with_caption_records_provisional_evidentiary_side_channel() -> None:
    classified = with_classified_reading_path(
        _artifact(
            [
                {
                    "id": "chart",
                    "kind": "chart",
                    "label": "adoption by month",
                    "bbox": [0.18, 0.18, 0.78, 0.62],
                },
                {
                    "id": "caption",
                    "kind": "caption text",
                    "label": "Monthly adoption increased after training.",
                    "bbox": [0.20, 0.65, 0.76, 0.72],
                },
            ],
            layout_description="Chart with caption.",
        )
    )

    assert classified.image_roles == ["2_5", "1"]
    assert classified.image_role_flags == ["tier_2_5_candidate"]


def test_s2_instructional_diagram_is_quarantined_tier_3_with_side_channel() -> None:
    classified = with_classified_reading_path(
        _artifact(
            [
                {
                    "id": "diagram",
                    "kind": "diagram",
                    "label": "load-bearing framework flow",
                    "bbox": [0.20, 0.15, 0.80, 0.76],
                },
                {
                    "id": "internal-label",
                    "kind": "text label",
                    "label": "Intake",
                    "bbox": [0.34, 0.28, 0.44, 0.34],
                },
            ],
            layout_description="Foreground framework diagram.",
        )
    )

    assert classified.image_roles == ["3", "1"]
    assert classified.image_role_flags == ["tier_3_quarantined"]


def test_s2_icon_logo_small_area_locks_tier_4_over_perceiver_label() -> None:
    classified = with_classified_reading_path(
        _artifact(
            [
                {
                    "id": "chip",
                    "kind": "icon",
                    "label": "",
                    "role_tier": "2",
                    "bbox": [0.10, 0.10, 0.18, 0.18],
                }
            ]
        )
    )

    assert classified.image_roles == ["4"]


@pytest.mark.parametrize(
    "element",
    [
        {
            "id": "decor-diagram",
            "kind": "diagram decorative background",
            "label": "",
            "bbox": [0.10, 0.08, 0.90, 0.90],
        },
        {
            "id": "empty-diagram",
            "kind": "diagram",
            "label": "",
            "role_tier": "3",
            "bbox": [0.20, 0.20, 0.80, 0.80],
        },
    ],
)
def test_s2_internal_label_gate_rules_out_tier_3(element: dict[str, object]) -> None:
    classified = with_classified_reading_path(_artifact([element]))

    assert classified.image_roles != ["3"]
    assert classified.image_role_flags is None


def test_s2_borderline_fixtures_are_stable_across_supported_folds() -> None:
    tier_1_2 = with_classified_reading_path(
        _artifact(
            [
                {
                    "id": "photo",
                    "kind": "photo",
                    "label": "doctor portrait",
                    "bbox": [0.58, 0.15, 0.90, 0.68],
                }
            ]
        )
    )
    tier_2_2_5 = with_classified_reading_path(
        _artifact(
            [
                {
                    "id": "chart",
                    "kind": "chart",
                    "label": "response rates",
                    "bbox": [0.18, 0.18, 0.78, 0.62],
                },
                {
                    "id": "caption",
                    "kind": "caption",
                    "label": "Rates improved.",
                    "bbox": [0.20, 0.65, 0.76, 0.72],
                },
            ]
        )
    )

    assert tier_1_2.image_roles == ["2"]
    assert tier_2_2_5.image_roles == ["2_5", "1"]


def test_s2_empty_visual_elements_are_controlled_not_unclassifiable() -> None:
    classified = with_classified_reading_path(
        _artifact(
            [],
            extracted_text="A plain text slide with no returned elements.",
            layout_description="No positioned elements returned.",
        )
    )

    assert classified.reading_path == "top_down"
    assert classified.macro_layout == "single_text_block"
    assert classified.image_roles == []


def test_t11_image_roles_preserve_index_alignment_with_bboxless_elements() -> None:
    elements: list[dict[str, object]] = [
        {
            "id": "support-photo",
            "kind": "photo",
            "label": "doctor portrait",
            "bbox": [0.58, 0.15, 0.90, 0.68],
        },
        {
            "id": "bboxless-gap",
            "kind": "photo",
            "label": "provider returned no geometry",
        },
        {
            "id": "small-icon",
            "kind": "icon",
            "label": "",
            "bbox": [0.10, 0.10, 0.18, 0.18],
        },
    ]

    classified = with_classified_reading_path(_artifact(elements))

    assert len(classified.image_roles or []) == len(classified.visual_elements)
    assert classified.image_roles == ["2", None, "4"]


def test_t11_invalid_role_tier_is_flagged_when_backfilled() -> None:
    classified = with_classified_reading_path(
        _artifact(
            [
                {
                    "id": "photo",
                    "kind": "photo",
                    "label": "doctor portrait",
                    "role_tier": "bogus",
                    "bbox": [0.58, 0.15, 0.90, 0.68],
                }
            ]
        )
    )

    assert classified.image_roles == ["2"]
    assert classified.image_role_flags == ["dropped_invalid_tier"]


def test_s2_scored_tier_fold_and_agreement_report_exclude_quarantined_tier_3() -> None:
    assert fold_scored_tier("2_5") == "2"
    assert fold_scored_tier("3") is None

    report = score_image_role_agreement(
        ["1", "2", "2_5", "3", "4", "1", "2"],
        ["1", "2", "2", "3", "4", "1", "1"],
    )

    assert report.quarantined_count == 1
    assert report.confusion_matrix["1"]["1"] == 2
    assert report.confusion_matrix["2"]["2"] == 2
    assert report.kappa >= 0.6
    assert report.soft_middle_kappa >= 0.6
    assert report.passes


@pytest.mark.parametrize(
    ("left", "right"),
    [
        (["3", "4"], ["4", "3"]),
        (["3", "2"], ["2", "2"]),
    ],
)
def test_t11_tier_3_disagreement_is_visible(left: list[str], right: list[str]) -> None:
    report = score_image_role_agreement(left, right)

    assert report.tier3_disagreement > 0
    assert not report.passes


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ([], []),
        (["3", "3"], ["3", "3"]),
    ],
)
def test_t11_empty_or_all_quarantined_scoring_never_passes(
    left: list[str], right: list[str]
) -> None:
    report = score_image_role_agreement(left, right)

    assert report.scored_pair_count == 0
    assert not report.passes


def test_s2_rubric_metadata_marks_candidate_tiers_for_retest() -> None:
    metadata = tier_rubric_metadata()

    assert set(metadata) == {"1", "2", "2_5", "3", "4"}
    assert metadata["2_5"]["retest_marker"] == "provisional"
    assert metadata["3"]["retest_marker"] == "provisional"
    assert metadata["1"]["eye_verb"] == "feel"
