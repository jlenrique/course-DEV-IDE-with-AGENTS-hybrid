"""Slice-1 unit tests for the deterministic warm_callback safety core.

Story concierge-leg1b-warm-callback (Slice 1 — the deterministic safety core).
NO MOCKS: real pedagogy_annotation / figure_tokens / voice_provider_text helpers
on real-shaped fixtures.

Covers:
  * grounding anchor selection (AC2/AC7) — strictly-prior teachable parents only;
  * the R7 gate-with-teeth (AC5) — block-by-omission, never strip;
  * the 07G read-path teeth (close-bar #4) — raise on a fired callback line.
"""

from __future__ import annotations

import pytest

from app.marcus.lesson_plan.pedagogy_annotation import build_pedagogy_annotations
from app.specialists.irene.authoring.warm_callback import (
    WarmCallbackGateResult,
    gate_warm_callback,
    select_grounded_callback_anchors,
)
from app.specialists.irene.graph import (
    Pass2ReadingPathError,
    _slide_roster,
    assert_callback_reading_path,
)

# --------------------------------------------------------------------------- #
# Grounding fixtures (real universal-md front-matter shape)
# --------------------------------------------------------------------------- #


def _corpus() -> list[dict[str, object]]:
    """Four components: a resolved prior, a failed prior, the target, a later one."""
    return [
        {
            "component_id": "c1-slide",
            "type": "slide",
            "doc_ordinal": 1,
            "locator": "deck#1",
            "resolution_status": "resolved",
        },
        {
            "component_id": "c2-slide-failed",
            "type": "slide",
            "doc_ordinal": 2,
            "locator": "deck#2",
            "resolution_status": "failed",
        },
        {
            "component_id": "c3-narration-target",
            "type": "narration",
            "doc_ordinal": 3,
            "locator": "deck#3",
            "resolution_status": "resolved",
        },
        {
            "component_id": "c4-slide-after",
            "type": "slide",
            "doc_ordinal": 4,
            "locator": "deck#4",
            "resolution_status": "resolved",
        },
    ]


def _annotations(components: list[dict[str, object]]):
    # Real P3 overlay (offline deterministic pass) — no mock teachable verdicts.
    return build_pedagogy_annotations(components, [])


def test_grounding_selects_strictly_prior_teachable_anchor() -> None:
    components = _corpus()
    annotations = _annotations(components)

    anchors = select_grounded_callback_anchors(
        "c3-narration-target", components, annotations
    )

    # c1 is strictly-prior AND resolved -> selected.
    assert "c1-slide" in anchors
    # c2 is strictly-prior but failed -> EXCLUDED.
    assert "c2-slide-failed" not in anchors
    # c4 is strictly-AFTER the target -> EXCLUDED.
    assert "c4-slide-after" not in anchors
    # Anchor identity is the PARENT component_id (never a source_point #ordinal).
    assert anchors == ("c1-slide",)


def test_grounding_excludes_non_teachable_prior_component() -> None:
    components = _corpus()
    annotations = _annotations(components)

    anchors = select_grounded_callback_anchors(
        "c3-narration-target", components, annotations
    )

    assert all(not a.endswith("failed") for a in anchors)


def test_grounding_negative_trap_only_unteachable_prior_yields_empty() -> None:
    # teaches_after points ONLY at a teachable=False component => empty tuple.
    components = [
        {
            "component_id": "only-prior-failed",
            "type": "slide",
            "doc_ordinal": 1,
            "locator": "deck#1",
            "resolution_status": "ungrounded",
        },
        {
            "component_id": "target",
            "type": "narration",
            "doc_ordinal": 2,
            "locator": "deck#2",
            "resolution_status": "resolved",
        },
    ]
    annotations = _annotations(components)

    anchors = select_grounded_callback_anchors("target", components, annotations)

    assert anchors == ()


def test_grounding_strictly_after_component_excluded() -> None:
    components = _corpus()
    annotations = _annotations(components)
    # Target is the FIRST component -> nothing strictly-prior at all.
    anchors = select_grounded_callback_anchors("c1-slide", components, annotations)
    assert anchors == ()


# --------------------------------------------------------------------------- #
# R7 gate-with-teeth (AC5) — block-by-omission, never strip
# --------------------------------------------------------------------------- #


def test_gate_connective_callback_zero_new_tokens_kept() -> None:
    result = gate_warm_callback(
        "Recall what we established earlier about the framework.",
        "Earlier we established the framework and its guiding principles.",
    )
    assert isinstance(result, WarmCallbackGateResult)
    assert result.kept is True
    assert result.reason is None
    assert result.audit["status"] == "PASS"


def test_gate_unsourced_figure_blocked_by_omission() -> None:
    result = gate_warm_callback(
        "Remember, that was about 40%.",
        "Earlier we discussed the framework and its guiding principles.",
    )
    assert result.kept is False
    assert result.reason is not None
    assert result.audit["status"] == "FAIL"
    # The audit names the unsourced figure (percent:40), never a strip.
    assert "percent:40" in result.audit["unsourced"]["numerals_units"]


def test_gate_clinical_leg_deferred_when_no_lexicon() -> None:
    result = gate_warm_callback(
        "Recall what we established earlier about the framework.",
        "Earlier we established the framework and its guiding principles.",
        clinical_terms=None,
    )
    assert result.audit["clinical_terms_leg"] == "deferred (no lexicon)"


# --------------------------------------------------------------------------- #
# 07G read-path teeth (close-bar #4) — raise on a fired callback line
# --------------------------------------------------------------------------- #


def _payload() -> dict[str, object]:
    return {
        "gary_slide_output": [
            {
                "slide_id": "slide-01",
                "visual_description": "Z layout with headline and callout.",
            }
        ],
        "perception_artifacts": [
            {
                "slide_id": "slide-01",
                "confidence": "HIGH",
                "coverage": "perceived",
                "reading_path": "z_pattern",
                "visual_elements": [
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
            }
        ],
    }


def _parsed(order: list[str]) -> dict[str, object]:
    return {
        "narration_script": [{"slide_id": "slide-01", "narration_text": "Fixture"}],
        "segment_manifest_deltas": [
            {
                "id": "seg-01",
                "visual_references": [
                    {"perception_source": "slide-01", "element_id": element}
                    for element in order
                ],
            }
        ],
    }


def test_callback_reading_path_teeth_raise_on_wrong_order() -> None:
    roster = _slide_roster(_payload())
    parsed = _parsed(["body", "hero"])  # violates z_pattern monotonic scan order

    with pytest.raises(Pass2ReadingPathError):
        assert_callback_reading_path(parsed=parsed, roster=roster)


def test_callback_reading_path_teeth_clean_on_correct_order() -> None:
    roster = _slide_roster(_payload())
    parsed = _parsed(["headline", "hero", "body", "cta"])

    # Must not raise on a conforming callback line.
    assert_callback_reading_path(parsed=parsed, roster=roster)
