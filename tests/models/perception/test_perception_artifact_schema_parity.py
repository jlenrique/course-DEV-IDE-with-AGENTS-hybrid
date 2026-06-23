from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from app.models.perception.perception_artifact import (
    CalloutIntent,
    ImageRoleFlag,
    ImageRoleTier,
    MacroLayout,
    NarrationCadence,
    PerceptionArtifact,
    ReadingPath,
    ReadingPathFlag,
    ReadingPathSource,
    TextSubstructure,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "state"
    / "config"
    / "schemas"
    / "perception-artifact.schema.json"
)


def _valid_payload() -> dict[str, object]:
    return {
        "slide_id": "slide-01",
        "confidence": "HIGH",
        "coverage": "perceived",
        "provenance": "png-grounded",
        "reading_path": "top_down",
        "macro_layout": "single_text_block",
        "image_roles": None,
        "image_role_flags": None,
        "text_substructure": "dense_exposition",
        "narration_cadence": "dense",
        "callout_intent": None,
        "reading_path_flags": None,
        "dominant_image_role": None,
        "reading_path_source": "llm_primary",
        "reading_path_degraded": False,
        "reading_path_rationale": {"macro_layout": "plain text"},
        "reading_path_geometry": {"macro_layout": "single_text_block"},
        "visual_elements": [{"kind": "callout", "text": "$4.5T"}],
        "extracted_text": "$4.5T spend. Building photo.",
    }


@pytest.fixture(scope="module")
def emitted_schema() -> dict[str, object]:
    assert SCHEMA_PATH.exists(), f"Expected emitted schema at {SCHEMA_PATH}"
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_provenance_is_model_field_but_excluded_from_dump_and_schema(
    emitted_schema: dict[str, object],
) -> None:
    artifact = PerceptionArtifact.model_validate(_valid_payload())

    assert "provenance" in PerceptionArtifact.model_fields
    assert artifact.provenance == "png-grounded"
    assert "provenance" not in artifact.model_dump()
    assert "provenance" not in emitted_schema.get("properties", {})


def test_emitted_schema_matches_live_schema_for_public_fields(
    emitted_schema: dict[str, object],
) -> None:
    live_schema = PerceptionArtifact.model_json_schema()

    assert emitted_schema["properties"] == live_schema["properties"]
    assert emitted_schema.get("additionalProperties") is False
    assert set(emitted_schema.get("required", [])) == set(live_schema.get("required", []))


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("confidence", "MEDIUM"),
        ("coverage", "maybe"),
        ("provenance", "screen-scrape"),
        ("reading_path", "triptych"),
        ("macro_layout", "triptych"),
        ("text_substructure", "ordered_list"),
        ("narration_cadence", "fast"),
        ("callout_intent", "takeaway_imperative"),
        ("reading_path_flags", ["comparison_pair"]),
        ("image_role_flags", ["tier_3_scored"]),
        ("dominant_image_role", "2.5"),
        ("reading_path_source", "mock"),
    ],
)
def test_closed_enums_reject_bad_values(field: str, bad_value: str) -> None:
    payload = _valid_payload()
    payload[field] = bad_value

    with pytest.raises(ValidationError):
        PerceptionArtifact.model_validate(payload)


def test_closed_enums_reject_bad_values_via_type_adapter() -> None:
    payload = _valid_payload()
    payload["reading_path"] = "image-dominant-first"

    with pytest.raises(ValidationError):
        TypeAdapter(PerceptionArtifact).validate_python(payload)


def test_reading_path_literal_rejects_out_of_vocab() -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(ReadingPath).validate_python("triptych")


@pytest.mark.parametrize(
    ("adapter", "bad_value"),
    [
        (MacroLayout, "triptych"),
        (ImageRoleTier, "2.5"),
        (ImageRoleFlag, "tier_3_scored"),
        (TextSubstructure, "ordered_list"),
        (NarrationCadence, "fast"),
        (CalloutIntent, "takeaway_imperative"),
        (ReadingPathFlag, "comparison_pair"),
        (ReadingPathSource, "mock"),
    ],
)
def test_tuple_axis_literals_reject_out_of_vocab(
    adapter: object,
    bad_value: str,
) -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(adapter).validate_python(bad_value)


def test_tuple_axis_assignment_revalidates() -> None:
    artifact = PerceptionArtifact.model_validate(_valid_payload())

    with pytest.raises(ValidationError):
        artifact.macro_layout = "triptych"  # type: ignore[assignment]


def test_reading_path_schema_enum_is_public_and_closed(
    emitted_schema: dict[str, object],
) -> None:
    properties = emitted_schema["properties"]
    reading_path = properties["reading_path"]
    enum_branch = next(
        branch for branch in reading_path["anyOf"] if branch.get("type") == "string"
    )

    assert enum_branch["enum"] == [
            "z_pattern",
            "f_pattern",
            "center_out",
            "top_down",
            "multi_column",
            "grid_quadrant",
            "sequence_numbered",
            "split_image_text",
            "two_up_comparison",
            "text_hero_divider",
            "enumerated_process",
            "diagram_driven",
        ]


def test_tuple_axis_schema_enums_are_public_and_closed(
    emitted_schema: dict[str, object],
) -> None:
    properties = emitted_schema["properties"]

    macro = next(
        branch for branch in properties["macro_layout"]["anyOf"] if branch.get("type") == "string"
    )
    image_roles = properties["image_roles"]["anyOf"][0]["items"]["anyOf"]
    image_role_tier = next(
        branch for branch in image_roles if branch.get("type") == "string"
    )
    image_role_null = next(branch for branch in image_roles if branch.get("type") == "null")
    text = next(
        branch
        for branch in properties["text_substructure"]["anyOf"]
        if branch.get("type") == "string"
    )
    cadence = next(
        branch
        for branch in properties["narration_cadence"]["anyOf"]
        if branch.get("type") == "string"
    )
    callout = next(
        branch
        for branch in properties["callout_intent"]["anyOf"]
        if branch.get("type") == "string"
    )
    dominant = next(
        branch
        for branch in properties["dominant_image_role"]["anyOf"]
        if branch.get("type") == "string"
    )
    source = next(
        branch
        for branch in properties["reading_path_source"]["anyOf"]
        if branch.get("type") == "string"
    )

    assert macro["enum"] == [
        "split_image_text",
        "text_hero_divider",
        "multi_column",
        "two_pane",
        "card_grid",
        "center_out",
        "diagram_driven",
        "single_text_block",
    ]
    assert image_role_tier["enum"] == ["1", "2", "2_5", "3", "4"]
    assert image_role_null == {"type": "null"}
    assert dominant["enum"] == ["1", "2", "2_5", "3", "4"]
    assert text["enum"] == [
        "enumerated_process",
        "peer_boxes",
        "comparison_pair",
        "dense_exposition",
        "hero_message",
    ]
    assert cadence["enum"] == ["sparse_slow", "moderate", "dense"]
    assert callout["enum"] == ["invite_response", "challenge_quiz", "directive_cta"]
    assert source["enum"] == ["deterministic", "llm_primary", "safe_default"]


def test_reading_path_flags_schema_enum_is_public_and_closed(
    emitted_schema: dict[str, object],
) -> None:
    properties = emitted_schema["properties"]
    flags = properties["reading_path_flags"]["anyOf"][0]["items"]

    assert flags["const"] == "oppositional_cue"


def test_image_role_flags_schema_enum_is_public_and_closed(
    emitted_schema: dict[str, object],
) -> None:
    properties = emitted_schema["properties"]
    flags = properties["image_role_flags"]["anyOf"][0]["items"]

    assert flags["enum"] == [
        "dropped_invalid_tier",
        "tier_2_5_candidate",
        "tier_3_quarantined",
    ]


def test_p2_1_fixture_still_validates_additively() -> None:
    fixture = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "specialists"
        / "quinn_r"
        / "fidelity"
        / "green-corpus"
        / "green-01.json"
    )
    payload = json.loads(fixture.read_text(encoding="utf-8"))["perception_artifacts"][0]

    artifact = PerceptionArtifact.model_validate(payload)

    assert artifact.coverage == "perceived"
    assert artifact.provenance == "png-grounded"
    assert artifact.reading_path is None
