from __future__ import annotations

from app.specialists.irene.graph import (
    _assemble_pass_2_prompt,
    _assert_reading_path_conformance,
    _slide_roster,
)


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


def test_reading_path_conformance_records_wrong_order_narration() -> None:
    roster = _slide_roster(_payload())
    parsed = _parsed(["body", "hero"])

    _assert_reading_path_conformance(roster=roster, parsed=parsed)

    assert parsed["reading_path_conformance_warnings"] == [
        {
            "tag": "irene.pass2.reading-path-order-failed",
            "slide_id": "slide-01",
            "reading_path": "z_pattern",
            "element_key": "hero",
            "previous_scan_index": 2,
            "message": (
                "Pass-2 narration visual reference order violates z_pattern for "
                "slide-01: 'hero' appears after scan index 2"
            ),
        }
    ]


def test_reading_path_conformance_accepts_scan_order_narration() -> None:
    roster = _slide_roster(_payload())

    _assert_reading_path_conformance(
        roster=roster,
        parsed=_parsed(["headline", "hero", "body", "cta"]),
    )


def test_referenced_slide_without_reading_path_records_warning() -> None:
    payload = _payload()
    del payload["perception_artifacts"][0]["reading_path"]  # type: ignore[index]
    roster = _slide_roster(payload)
    parsed = _parsed(["headline"])

    _assert_reading_path_conformance(roster=roster, parsed=parsed)

    assert parsed["reading_path_conformance_warnings"] == [
        {
            "tag": "irene.pass2.reading-path-missing",
            "slide_id": "slide-01",
            "message": "slide slide-01 is referenced but missing reading_path",
        }
    ]


def test_prompt_includes_reading_path_cadence_guidance() -> None:
    roster = _slide_roster(_payload())
    _, user = _assemble_pass_2_prompt(
        _payload(),
        extracted_source="# Source\n\nHealthcare operations.",
        slide_roster=roster,
    )

    assert "## Reading path cadence guidance" in user
    assert "slide-01: reading_path=z_pattern" in user
    assert "headline -> hero -> body -> cta" in user
