"""P2-3: Irene Pass 2 consumes perceived visuals as sole visual authority."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.models.perception import PerceptionArtifact as RichPerceptionArtifact
from app.specialists._shared import figure_tokens as shared_figure_tokens
from app.specialists.irene.authoring.pass_2_template import (
    project_rich_perception_for_authoring,
)
from app.specialists.irene.graph import (
    EXPECTED_VISUAL_PLAN_HEADER,
    PERCEIVED_SPEAKABLE_FIGURES_HEADER,
    UNVERIFIED_VISUAL_AUTHORITY,
    VISUAL_AUTHORITY_HEADER,
    Pass2GroundingError,
    _assemble_pass_2_prompt,
    _assert_figure_citations_within_perceived,
    _slide_roster,
)
from app.specialists.quinn_r import fidelity_detector as quinn_fidelity_detector
from app.specialists.quinn_r.fidelity_detector import detect_fidelity
from app.specialists.quinn_r.quality_control_dispatch import FidelityError

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "specialists" / "irene"


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _prompt_regions(payload: dict[str, Any]) -> tuple[str, str, str]:
    roster = _slide_roster(payload)
    _, user = _assemble_pass_2_prompt(
        payload,
        extracted_source="# Source corpus\n\nHealthcare operations.",
        slide_roster=roster,
    )
    authority_start = user.index(VISUAL_AUTHORITY_HEADER) + len(VISUAL_AUTHORITY_HEADER)
    expected_start = user.index(EXPECTED_VISUAL_PLAN_HEADER)
    sanctum_start = user.index("## Sanctum digest")
    authority = user[authority_start:expected_start]
    expected = user[expected_start:sanctum_start]
    return user, authority, expected


def test_authority_region_uses_perceived_visuals_and_demotes_stale_brief() -> None:
    payload = _load("p2_3_contradiction_fixture.json")
    user, authority, expected = _prompt_regions(payload)

    assert PERCEIVED_SPEAKABLE_FIGURES_HEADER in user
    assert "$4.5T" in authority
    assert "building photo" in authority
    assert "$5.2T" not in authority
    assert "line+bars" not in authority

    assert "$5.2T" not in user
    assert "[REDACTED: figure absent from perceived authority for slide-01]" in expected
    assert "line+bars" in expected
    assert "subordinate" in expected
    assert "may be stale" in expected
    assert "defer to perceived" in expected


def test_speakable_figures_block_always_present_even_when_empty() -> None:
    payload = _figure_free_payload_with_stale_brief()
    user, _, _ = _prompt_regions(payload)
    assert PERCEIVED_SPEAKABLE_FIGURES_HEADER in user
    assert "slide-figure-free: <none" in user
    assert "MUST be ⊆ that slide's perceived speakable set" in user


def test_missing_or_low_confidence_perception_never_falls_back_to_brief() -> None:
    payload = _load("p2_3_contradiction_fixture.json")
    payload["perception_artifacts"] = [
        {
            **payload["perception_artifacts"][0],
            "coverage": "low-confidence",
            "confidence": "LOW",
        }
    ]
    user, authority, expected = _prompt_regions(payload)

    assert UNVERIFIED_VISUAL_AUTHORITY in authority
    assert "$5.2T" not in authority
    assert "line+bars" not in authority
    assert "$5.2T" not in expected

    # Pin the full prompt, not only the sliced authority region: stale brief
    # figures are redacted before Irene sees them.
    assert UNVERIFIED_VISUAL_AUTHORITY in user
    assert authority.count("$5.2T") == 0
    assert expected.count("$5.2T") == 0
    assert user.count("$5.2T") == 0

    payload.pop("perception_artifacts")
    missing_user, missing_authority, _ = _prompt_regions(payload)
    assert UNVERIFIED_VISUAL_AUTHORITY in missing_authority
    assert "$5.2T" not in missing_authority
    assert UNVERIFIED_VISUAL_AUTHORITY in missing_user
    assert "$5.2T" not in missing_user


def test_detector_judges_post_fix_narration_green_and_prefix_hallucination_red() -> None:
    payload = _load("p2_3_contradiction_fixture.json")
    green = [
        {
            "slide_id": "slide-01",
            "narration_text": "The building photo anchors the $4.5T scale.",
        }
    ]
    assert detect_fidelity(green, payload["perception_artifacts"]) == {
        "blocking": [],
        "evaluated_segments": 1,
    }

    red = [
        {
            "slide_id": "slide-01",
            "narration_text": "The line chart and paired bars show $5.2T.",
        }
    ]
    with pytest.raises(FidelityError):
        detect_fidelity(red, payload["perception_artifacts"])


def test_held_out_contradicted_slide_prevents_single_fixture_overfit() -> None:
    payload = _load("p2_3_held_out_fixture.json")
    user, authority, expected = _prompt_regions(payload)
    assert "74%" in authority
    assert "bar chart" in authority
    assert "80%" not in authority
    assert "line chart" not in authority
    assert "80%" not in user
    assert "[REDACTED: figure absent from perceived authority for slide-02]" in expected

    assert detect_fidelity(
        [{"slide_id": "slide-02", "narration_text": "The bar chart highlights 74%."}],
        payload["perception_artifacts"],
    )["blocking"] == []
    with pytest.raises(FidelityError):
        detect_fidelity(
            [{"slide_id": "slide-02", "narration_text": "The line chart shows 80%."}],
            payload["perception_artifacts"],
        )


def test_authoring_projection_is_minimal_compatibility_not_runtime_authority() -> None:
    rich = RichPerceptionArtifact.model_validate(
        _load("p2_3_contradiction_fixture.json")["perception_artifacts"][0]
    )
    minimal = project_rich_perception_for_authoring(rich)

    assert minimal.slide_id == rich.slide_id
    assert minimal.source_image_path == rich.source_png_path
    assert minimal.visual_elements == rich.visual_elements
    assert set(type(minimal).model_fields) == {
        "slide_id",
        "source_image_path",
        "visual_elements",
    }


def _figure_free_payload_with_stale_brief() -> dict[str, Any]:
    artifact = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "fixtures"
            / "specialists"
            / "quinn_r"
            / "fidelity"
            / "green-corpus"
            / "green-03.json"
        ).read_text(encoding="utf-8")
    )["perception_artifacts"][0]
    artifact["slide_id"] = "slide-figure-free"
    return {
        "bundle_reference": "bundle",
        "lesson_plan": {"title": "Training Gap"},
        "gary_slide_output": [
            {
                "slide_id": "slide-figure-free",
                "visual_description": (
                    "Blueprint prose about the training gap; 18% formal training."
                ),
            }
        ],
        "slide_briefs": [
            {
                "slide_id": "slide-figure-free",
                "prompt": "Variant B should avoid charts but source brief mentions 18%.",
            }
        ],
        "perception_artifacts": [artifact],
    }


def test_verified_figure_free_variant_redacts_stale_brief_figures_everywhere() -> None:
    payload = _figure_free_payload_with_stale_brief()
    user, authority, expected = _prompt_regions(payload)

    assert "18%" not in user
    assert "18%" not in authority
    assert "18%" not in expected
    assert "[REDACTED: figure absent from perceived authority for slide-figure-free]" in user


def test_perceived_figures_are_not_redacted_from_prompt() -> None:
    payload = _load("p2_3_contradiction_fixture.json")
    payload["gary_slide_output"][0]["visual_description"] = "Callout for $4.5T scale."
    payload["slide_briefs"][0]["prompt"] = "Use a stat callout showing $4.5T."

    user, authority, expected = _prompt_regions(payload)

    assert "$4.5T" in authority
    assert "$4.5T" in expected
    assert "$4.5T" in user


def test_figure_citation_post_check_blocks_unperceived_figures_and_allows_paraphrase() -> None:
    payload = _figure_free_payload_with_stale_brief()
    roster = _slide_roster(payload)
    parsed = {
        "narration_script": [
            {
                "id": "seg-1",
                "slide_id": "slide-figure-free",
                "narration_text": "Formal leadership training remains scarce.",
            }
        ],
        "segment_manifest_deltas": [],
    }
    _assert_figure_citations_within_perceived(parsed, roster)

    parsed["narration_script"][0]["narration_text"] = "Only 18% receive formal training."
    with pytest.raises(Pass2GroundingError) as excinfo:
        _assert_figure_citations_within_perceived(parsed, roster)

    assert excinfo.value.tag == "irene.pass2.figure-contradiction"
    assert "scope=narration" in str(excinfo.value)
    assert "percent:18" in str(excinfo.value)


def test_figure_citation_post_check_allows_perceived_figures_and_pins_money_boundary() -> None:
    payload = _load("p2_3_contradiction_fixture.json")
    roster = _slide_roster(payload)

    _assert_figure_citations_within_perceived(
        {
            "narration_script": [
                {"slide_id": "slide-01", "narration_text": "The scale reaches $4.5T."}
            ],
            "segment_manifest_deltas": [],
        },
        roster,
    )

    with pytest.raises(Pass2GroundingError) as excinfo:
        _assert_figure_citations_within_perceived(
            {
                "narration_script": [
                    {"slide_id": "slide-01", "narration_text": "Enrollment costs $5."}
                ],
                "segment_manifest_deltas": [],
            },
            roster,
        )
    assert "money-bare:5" in str(excinfo.value)


def test_irene_and_g5_share_figure_extractor() -> None:
    assert quinn_fidelity_detector._figures is shared_figure_tokens._figures
    sample = "Spend is $4.5T, not $5, with 74% and 3x growth."
    assert quinn_fidelity_detector._figures(sample) == shared_figure_tokens._figures(sample)
