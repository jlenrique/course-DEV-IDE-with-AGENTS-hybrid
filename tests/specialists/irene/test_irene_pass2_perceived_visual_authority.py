"""P2-3: Irene Pass 2 consumes perceived visuals as sole visual authority."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.models.perception import PerceptionArtifact as RichPerceptionArtifact
from app.specialists.irene.authoring.pass_2_template import (
    project_rich_perception_for_authoring,
)
from app.specialists.irene.graph import (
    EXPECTED_VISUAL_PLAN_HEADER,
    UNVERIFIED_VISUAL_AUTHORITY,
    VISUAL_AUTHORITY_HEADER,
    _assemble_pass_2_prompt,
    _slide_roster,
)
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
    _, authority, expected = _prompt_regions(payload)

    assert "$4.5T" in authority
    assert "building photo" in authority
    assert "$5.2T" not in authority
    assert "line+bars" not in authority

    assert "$5.2T" in expected
    assert "line+bars" in expected
    assert "subordinate" in expected
    assert "may be stale" in expected
    assert "defer to perceived" in expected


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
    assert "$5.2T" in expected

    # T11 party-mode C1 (Murat A3 anti-vacuity hardening): pin the FULL prompt,
    # not only the sliced authority region. The brief figure must be framed-only
    # (it appears in the demoted `expected` region) and never in authority. Any
    # other $5.2T occurrence in `user` originates from the inert
    # `## Envelope payload` sorted-keys JSON dump — pre-existing Pass-2 structure
    # pinned by the NFR-I6 byte-stability fixture — whose tail is guarded at
    # OUTPUT by the G5 Quinn-R fidelity detector, not by prompt shape. See
    # deferred-inventory `pass2-envelope-payload-brief-unframed-in-prompt-tail`.
    assert UNVERIFIED_VISUAL_AUTHORITY in user
    assert authority.count("$5.2T") == 0
    assert expected.count("$5.2T") >= 1

    payload.pop("perception_artifacts")
    missing_user, missing_authority, _ = _prompt_regions(payload)
    assert UNVERIFIED_VISUAL_AUTHORITY in missing_authority
    assert "$5.2T" not in missing_authority
    assert UNVERIFIED_VISUAL_AUTHORITY in missing_user


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
    _, authority, expected = _prompt_regions(payload)
    assert "74%" in authority
    assert "bar chart" in authority
    assert "80%" not in authority
    assert "line chart" not in authority
    assert "80%" in expected

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
