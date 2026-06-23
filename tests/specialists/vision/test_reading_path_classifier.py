from __future__ import annotations

import pytest

from app.models.perception import PerceptionArtifact
from scripts.utilities.reading_path_classifier import (
    REQUIRED_PERCEPTION_FIELDS,
    ReadingPathClassificationError,
    ReadingPathLLMPrimaryError,
    _llm_primary_prompt,
    assert_default_ceiling,
    classify_reading_path,
    classify_reading_path_batch,
    ordered_element_keys_for_reading_path,
    parse_live_reading_path_tuple,
    with_classified_reading_path,
    with_llm_primary_reading_path,
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


def test_additive_z_pattern_fixture_resolves_to_stable_primary_name() -> None:
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

    assert classify_reading_path(artifact) == "split_image_text"
    assert ordered_element_keys_for_reading_path(artifact) == [
        "headline",
        "hero",
        "body",
        "cta",
    ]
    assert ordered_element_keys_for_reading_path(artifact) != naive_order


def test_numbered_summary_list_downgrades_to_peer_boxes_primary() -> None:
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

    classified = with_classified_reading_path(artifact)

    assert classified.reading_path == "top_down"
    assert classified.text_substructure == "peer_boxes"
    assert ordered_element_keys_for_reading_path(artifact) == ["first", "second", "third"]


def test_transform_sequence_uses_enumerated_process() -> None:
    artifact = _artifact(
        [
            {
                "id": "first",
                "kind": "step",
                "label": "Assess need",
                "bbox": [0.10, 0.15, 0.25, 0.30],
            },
            {
                "id": "arrow",
                "kind": "arrow",
                "label": "then",
                "bbox": [0.30, 0.20, 0.36, 0.24],
            },
            {
                "id": "second",
                "kind": "step",
                "label": "becomes a pilot that produces evidence",
                "bbox": [0.40, 0.15, 0.58, 0.30],
            },
            {
                "id": "third",
                "kind": "step",
                "label": "launch and iterate",
                "bbox": [0.66, 0.15, 0.86, 0.30],
            },
        ],
        layout_description="Flow process with arrows.",
    )

    classified = with_classified_reading_path(artifact)

    assert classified.reading_path == "enumerated_process"
    assert classified.text_substructure == "enumerated_process"
    assert ordered_element_keys_for_reading_path(classified) == [
        "first",
        "arrow",
        "second",
        "third",
    ]


def test_two_wide_coordinate_peer_slide_emits_counted_multi_column() -> None:
    artifact = _artifact(
        [
            {
                "id": "left",
                "kind": "text_box",
                "label": "Clinician lens",
                "bbox": [0.10, 0.20, 0.42, 0.70],
            },
            {
                "id": "right",
                "kind": "text_box",
                "label": "Population lens",
                "bbox": [0.58, 0.20, 0.90, 0.70],
            },
        ],
        layout_description="Two coordinate peer columns with no versus cue.",
    )

    classified = with_classified_reading_path(artifact)
    summary = classify_reading_path_batch([artifact])

    assert classified.reading_path == "multi_column"
    assert classified.macro_layout == "multi_column"
    assert summary.counts["multi_column"] == 1
    assert summary.total == 1


def test_oppositional_two_pane_cue_flags_but_does_not_upgrade_in_s1() -> None:
    artifact = _artifact(
        [
            {
                "id": "left",
                "kind": "text_box",
                "label": "Option A",
                "bbox": [0.10, 0.20, 0.42, 0.70],
            },
            {
                "id": "right",
                "kind": "text_box",
                "label": "Option B",
                "bbox": [0.58, 0.20, 0.90, 0.70],
            },
        ],
        layout_description="Option A versus Option B.",
    )

    classified = with_classified_reading_path(artifact)

    assert classified.reading_path == "multi_column"
    assert classified.macro_layout == "multi_column"
    assert classified.text_substructure == "peer_boxes"
    assert classified.reading_path_flags == ["oppositional_cue"]


@pytest.mark.parametrize(
    "label",
    [
        "before the meeting",
        "after the meeting",
        "pro tip",
        "conventional wisdom",
    ],
)
def test_bare_opposition_tokens_do_not_create_comparison_pair(label: str) -> None:
    artifact = _artifact(
        [
            {
                "id": "left",
                "kind": "text_box",
                "label": label,
                "bbox": [0.10, 0.20, 0.42, 0.70],
            },
            {
                "id": "right",
                "kind": "text_box",
                "label": "Population lens",
                "bbox": [0.58, 0.20, 0.90, 0.70],
            },
        ],
        layout_description="Two coordinate peer columns.",
    )

    classified = with_classified_reading_path(artifact)

    assert classified.reading_path == "multi_column"
    assert classified.text_substructure == "peer_boxes"
    assert classified.reading_path_flags is None


def test_paired_before_after_cue_flags_without_s1_upgrade() -> None:
    artifact = _artifact(
        [
            {
                "id": "left",
                "kind": "text_box",
                "label": "Before launch",
                "bbox": [0.10, 0.20, 0.42, 0.70],
            },
            {
                "id": "right",
                "kind": "text_box",
                "label": "After launch",
                "bbox": [0.58, 0.20, 0.90, 0.70],
            },
        ],
        layout_description="Two coordinate peer columns.",
    )

    classified = with_classified_reading_path(artifact)

    assert classified.reading_path == "multi_column"
    assert classified.text_substructure == "peer_boxes"
    assert classified.reading_path_flags == ["oppositional_cue"]


def test_transform_verb_in_single_prose_blob_is_not_enumerated_process() -> None:
    artifact = _artifact(
        [
            {
                "id": "body",
                "kind": "text",
                "label": "We assess the need, then produce a pilot and launch later.",
                "bbox": [0.10, 0.18, 0.88, 0.60],
            }
        ],
        extracted_text="We assess the need, then produce a pilot and launch later.",
    )

    classified = with_classified_reading_path(artifact)

    assert classified.reading_path == "top_down"
    assert classified.text_substructure != "enumerated_process"


def test_card_grid_precedence_is_reachable_before_multi_column() -> None:
    artifact = _artifact(
        [
            {
                "id": "tl",
                "kind": "card grid item",
                "label": "Learn",
                "bbox": [0.10, 0.12, 0.34, 0.32],
            },
            {
                "id": "tr",
                "kind": "card grid item",
                "label": "Practice",
                "bbox": [0.58, 0.12, 0.82, 0.32],
            },
            {
                "id": "bl",
                "kind": "card grid item",
                "label": "Apply",
                "bbox": [0.10, 0.56, 0.34, 0.76],
            },
            {
                "id": "br",
                "kind": "card grid item",
                "label": "Reflect",
                "bbox": [0.58, 0.56, 0.82, 0.76],
            },
        ],
        layout_description="Four item grid.",
    )

    classified = with_classified_reading_path(artifact)

    assert classified.macro_layout == "card_grid"
    assert classified.reading_path == "grid_quadrant"


def test_permutable_peer_elements_have_same_tuple_when_input_order_changes() -> None:
    left = {
        "id": "left",
        "kind": "text_box",
        "label": "Clinician lens",
        "bbox": [0.10, 0.20, 0.42, 0.70],
    }
    right = {
        "id": "right",
        "kind": "text_box",
        "label": "Population lens",
        "bbox": [0.58, 0.20, 0.90, 0.70],
    }

    first = with_classified_reading_path(_artifact([left, right]))
    second = with_classified_reading_path(_artifact([right, left]))

    assert first.reading_path == second.reading_path == "multi_column"
    assert first.macro_layout == second.macro_layout == "multi_column"
    assert first.text_substructure == second.text_substructure == "peer_boxes"


def test_true_process_order_follows_structure_not_input_order() -> None:
    start = {
        "id": "start",
        "kind": "step",
        "label": "Assess need",
        "bbox": [0.10, 0.15, 0.25, 0.30],
    }
    arrow = {
        "id": "arrow",
        "kind": "arrow connector",
        "label": "",
        "bbox": [0.30, 0.20, 0.36, 0.24],
    }
    finish = {
        "id": "finish",
        "kind": "step",
        "label": "Launch pilot",
        "bbox": [0.42, 0.15, 0.58, 0.30],
    }

    artifact = with_classified_reading_path(_artifact([finish, arrow, start]))

    assert artifact.reading_path == "enumerated_process"
    assert artifact.text_substructure == "enumerated_process"
    assert ordered_element_keys_for_reading_path(artifact) == ["start", "arrow", "finish"]


def test_explicit_primary_names_are_derived_without_default_collapse() -> None:
    center = _artifact(
        [
            {
                "id": "center",
                "kind": "center hero",
                "label": "You",
                "bbox": [0.42, 0.38, 0.58, 0.55],
            },
            {
                "id": "orbit",
                "kind": "text",
                "label": "Support",
                "bbox": [0.10, 0.12, 0.28, 0.25],
            },
        ],
        layout_description="Radial center-out hero.",
    )
    diagram = _artifact(
        [
            {
                "id": "framework",
                "kind": "diagram",
                "label": "load-bearing framework flow",
                "bbox": [0.20, 0.15, 0.80, 0.75],
            }
        ],
        layout_description="Foreground load-bearing framework diagram.",
    )

    center_classified = with_classified_reading_path(center)
    diagram_classified = with_classified_reading_path(diagram)

    assert center_classified.macro_layout == "center_out"
    assert center_classified.reading_path == "center_out"
    assert diagram_classified.macro_layout == "diagram_driven"
    assert diagram_classified.reading_path == "diagram_driven"


def test_s2_classification_populates_image_roles_but_leaves_callout_intent_unpopulated() -> None:
    artifact = _artifact(
        [
            {
                "id": "left",
                "kind": "text_box",
                "label": "Clinician lens",
                "bbox": [0.10, 0.20, 0.42, 0.70],
            },
            {
                "id": "right",
                "kind": "text_box",
                "label": "Population lens",
                "bbox": [0.58, 0.20, 0.90, 0.70],
            },
        ]
    )

    classified = with_classified_reading_path(artifact)

    assert classified.image_roles == ["1", "1"]
    assert classified.callout_intent is None


def test_diagram_driven_foreground_gate_negative_control() -> None:
    artifact = _artifact(
        [
            {
                "id": "title",
                "kind": "text",
                "label": "Critical gap",
                "bbox": [0.08, 0.10, 0.52, 0.22],
            },
            {
                "id": "decor",
                "kind": "image",
                "label": "decorative background diagram",
                "bbox": [0.55, 0.05, 0.95, 0.95],
            },
        ],
        layout_description="Semi-transparent decorative background diagram.",
    )

    assert classify_reading_path(artifact) != "diagram_driven"


def test_kind_diagram_is_not_instructional_without_load_bearing_foreground() -> None:
    artifact = _artifact(
        [
            {
                "id": "diagram",
                "kind": "diagram",
                "label": "illustrative background Venn shape",
                "bbox": [0.55, 0.12, 0.92, 0.78],
            },
            {
                "id": "message",
                "kind": "text",
                "label": "Design thinking gives structure",
                "bbox": [0.08, 0.18, 0.48, 0.55],
            },
        ],
        layout_description="Diagram is illustrative, not foreground instructional.",
    )

    assert classify_reading_path(artifact) != "diagram_driven"


def test_tightened_looks_z_no_longer_fires_on_focal_hero_slide() -> None:
    artifact = _artifact(
        [
            {
                "id": "headline",
                "kind": "headline",
                "label": "Modern clinician dilemma",
                "bbox": [0.07, 0.08, 0.45, 0.20],
            },
            {
                "id": "copy",
                "kind": "text",
                "label": "A concise message-led text block",
                "bbox": [0.08, 0.28, 0.45, 0.62],
            },
            {
                "id": "hero",
                "kind": "photo",
                "label": "large hero photo",
                "bbox": [0.55, 0.08, 0.94, 0.82],
            },
            {
                "id": "small",
                "kind": "icon",
                "label": "small decorative icon",
                "bbox": [0.75, 0.84, 0.88, 0.94],
            },
        ],
        layout_description="Focal hero image with text side.",
    )

    assert classify_reading_path(artifact) == "split_image_text"


def test_default_degradation_counter_fails_over_default_batch() -> None:
    batch = [
        _artifact(
            [
                {
                    "id": f"body-{index}",
                    "kind": "text",
                    "label": "Plain paragraph text",
                    "bbox": [0.10, 0.10, 0.90, 0.35],
                }
            ],
            slide_id=f"slide-{index}",
        )
        for index in range(4)
    ]

    summary = classify_reading_path_batch(batch)

    assert summary.default_count == 4
    with pytest.raises(ReadingPathClassificationError, match="DEFAULT"):
        assert_default_ceiling(summary)


def test_out_of_range_and_inverted_bbox_is_normalized_not_skewed() -> None:
    artifact = _artifact(
        [
            {
                "id": "right",
                "kind": "text_box",
                "label": "Right column",
                "bbox": [1.20, 0.20, 0.80, 0.65],
            },
            {
                "id": "left",
                "kind": "text_box",
                "label": "Left column",
                "bbox": [-0.20, 0.20, 0.22, 0.65],
            },
        ],
        layout_description="Two coordinate peer columns.",
    )

    assert classify_reading_path(artifact) == "multi_column"


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


def test_llm_primary_parser_accepts_strict_json_and_normalizes_inform_callout() -> None:
    result = parse_live_reading_path_tuple(
        """
        ```json
        {
          "macro_layout": "split_image_text",
          "image_role": "3",
          "text_substructure": "dense_exposition",
          "narration_cadence": "moderate",
          "callout_intent": "inform",
          "rationale": {"macro_layout": "image plus text"}
        }
        ```
        """
    )

    assert result.macro_layout == "split_image_text"
    assert result.image_role == "3"
    assert result.callout_intent is None


def test_llm_primary_parser_rejects_out_of_contract_tuple() -> None:
    with pytest.raises(ReadingPathLLMPrimaryError):
        parse_live_reading_path_tuple(
            """
            {
              "macro_layout": "triptych",
              "image_role": "3",
              "text_substructure": "dense_exposition",
              "narration_cadence": "moderate",
              "callout_intent": null,
              "rationale": {}
            }
            """
        )


def test_llm_primary_transport_failure_safe_defaults_without_hard_block(monkeypatch) -> None:
    artifact = _artifact(
        [
            {
                "id": "body",
                "kind": "text",
                "label": "Plain paragraph text",
                "bbox": [0.10, 0.10, 0.90, 0.40],
            }
        ]
    )

    def _raise(*args: object, **kwargs: object) -> None:
        raise RuntimeError("transport down")

    monkeypatch.setattr(
        "scripts.utilities.reading_path_classifier.request_live_reading_path_tuple",
        _raise,
    )

    classified = with_llm_primary_reading_path(artifact)

    assert classified.reading_path == "top_down"
    assert classified.macro_layout == "single_text_block"
    assert classified.dominant_image_role is None
    assert classified.reading_path_source == "safe_default"
    assert classified.reading_path_degraded is True
    assert classified.reading_path_rationale == {"degraded": "transport down"}
    assert classified.reading_path_geometry is not None


def test_llm_primary_prompt_sharpens_decorative_vs_illustrative_boundary() -> None:
    prompt = _llm_primary_prompt(
        _artifact(
            [
                {
                    "id": "mood-photo",
                    "kind": "photo",
                    "label": "large unlabelled mood photo",
                    "bbox": [0.52, 0.05, 0.96, 0.88],
                }
            ]
        )
    )

    assert "Tier 1 image_role means DECORATIVE or evocative" in prompt
    assert "full-bleed photo or illustration is still tier 1" in prompt
    assert "Do not promote a mood/subject photo to tier 2 just because it is large" in prompt
    assert "Return tier 2 only when the slide text explicitly depends" in prompt
    assert "If uncertain between tier 1 and tier 2, choose tier 1" in prompt
    assert "do not return null for image_role" in prompt


def test_llm_primary_null_image_role_falls_back_to_largest_image_tier(monkeypatch) -> None:
    artifact = _artifact(
        [
            {
                "id": "copy",
                "kind": "text",
                "label": "Clinical leadership requires judgment.",
                "bbox": [0.08, 0.18, 0.45, 0.62],
            },
            {
                "id": "decor-photo",
                "kind": "photo",
                "label": "decorative full bleed photo",
                "role_tier": "1",
                "bbox": [0.52, 0.05, 0.96, 0.88],
            },
        ]
    )

    monkeypatch.setattr(
        "scripts.utilities.reading_path_classifier.request_live_reading_path_tuple",
        lambda *_a, **_k: parse_live_reading_path_tuple(
            """
            {
              "macro_layout": "split_image_text",
              "image_role": null,
              "text_substructure": "dense_exposition",
              "narration_cadence": "moderate",
              "callout_intent": null,
              "rationale": {}
            }
            """
        ),
    )

    classified = with_llm_primary_reading_path(artifact)

    assert classified.dominant_image_role == "1"
    assert classified.reading_path_source == "llm_primary"
    assert classified.reading_path_degraded is False


def test_llm_primary_plain_photo_tier_two_is_demoted_to_decorative(monkeypatch) -> None:
    artifact = _artifact(
        [
            {
                "id": "copy",
                "kind": "text",
                "label": "Clinical leadership requires judgment.",
                "bbox": [0.08, 0.18, 0.45, 0.62],
            },
            {
                "id": "mood-photo",
                "kind": "photo",
                "label": "large mood photo",
                "role_tier": "2",
                "bbox": [0.52, 0.05, 0.96, 0.88],
            },
        ]
    )

    monkeypatch.setattr(
        "scripts.utilities.reading_path_classifier.request_live_reading_path_tuple",
        lambda *_a, **_k: parse_live_reading_path_tuple(
            """
            {
              "macro_layout": "split_image_text",
              "image_role": "2",
              "text_substructure": "dense_exposition",
              "narration_cadence": "moderate",
              "callout_intent": null,
              "rationale": {}
            }
            """
        ),
    )

    classified = with_llm_primary_reading_path(artifact)

    assert classified.dominant_image_role == "1"


def test_llm_primary_chart_with_caption_keeps_evidentiary_role(monkeypatch) -> None:
    artifact = _artifact(
        [
            {
                "id": "chart",
                "kind": "chart",
                "label": "adoption by month",
                "role_tier": "2_5",
                "bbox": [0.18, 0.16, 0.78, 0.62],
            },
            {
                "id": "caption",
                "kind": "caption text",
                "label": "Monthly adoption increased after training.",
                "bbox": [0.20, 0.65, 0.76, 0.72],
            },
        ]
    )

    monkeypatch.setattr(
        "scripts.utilities.reading_path_classifier.request_live_reading_path_tuple",
        lambda *_a, **_k: parse_live_reading_path_tuple(
            """
            {
              "macro_layout": "single_text_block",
              "image_role": "2_5",
              "text_substructure": "dense_exposition",
              "narration_cadence": "moderate",
              "callout_intent": null,
              "rationale": {}
            }
            """
        ),
    )

    classified = with_llm_primary_reading_path(artifact)

    assert classified.dominant_image_role == "2_5"
