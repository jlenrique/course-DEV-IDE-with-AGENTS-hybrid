from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from app.models.perception.perception_artifact import PerceptionArtifact, ReadingPath

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
