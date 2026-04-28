from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jsonschema
import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from app.specialists.irene.authoring.pass_2_template import (
    REQUIRED_PROCEDURAL_RULES,
    GarySlideOutput,
    IrenePass2AuthoringEnvelope,
    PerceptionArtifact,
    SegmentManifest,
    SegmentManifestSegment,
    VisualReference,
)

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "fixtures" / "specialists" / "irene" / "pass_2_template_golden.json"
SCHEMA = ROOT.parent / "schema" / "irene_pass_2_authoring.v1.schema.json"
MARKDOWN = (
    ROOT.parent
    / "skills"
    / "bmad-agent-content-creator"
    / "references"
    / "pass-2-authoring-template.md"
)
VALIDATOR = (
    ROOT.parent
    / "skills"
    / "bmad-agent-marcus"
    / "scripts"
    / "validate-irene-pass2-handoff.py"
)


def _payload() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_strict_model_rejects_unknown_fields_and_naive_datetime() -> None:
    payload = _payload()
    payload["unexpected"] = "red"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        IrenePass2AuthoringEnvelope.model_validate(payload)

    payload = _payload()
    payload["generated_at_utc"] = datetime(2026, 4, 28, 10, 0)
    with pytest.raises(ValidationError, match="timezone-aware"):
        IrenePass2AuthoringEnvelope.model_validate(payload)


def test_strict_mode_rejects_implicit_coercion() -> None:
    payload = _payload()
    payload["run_id"] = 123

    with pytest.raises(ValidationError):
        IrenePass2AuthoringEnvelope.model_validate(payload)


def test_generated_at_utc_rejects_non_utc_aware() -> None:
    payload = _payload()
    payload["generated_at_utc"] = datetime(
        2026,
        4,
        28,
        10,
        0,
        tzinfo=timezone(timedelta(hours=-4)),
    )

    with pytest.raises(ValidationError, match="UTC"):
        IrenePass2AuthoringEnvelope.model_validate(payload)


def test_golden_fixture_and_schema_lockstep() -> None:
    model = IrenePass2AuthoringEnvelope.model_validate_json(
        FIXTURE.read_text(encoding="utf-8")
    )
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert model.schema_version == "irene-pass-2-authoring.v1"
    assert schema == IrenePass2AuthoringEnvelope.model_json_schema()
    assert schema["additionalProperties"] is False


def test_required_fields_bidirectional_schema_parity() -> None:
    schema = IrenePass2AuthoringEnvelope.model_json_schema()
    schema_required = set(schema["required"])
    pydantic_required = {
        name
        for name, field in IrenePass2AuthoringEnvelope.model_fields.items()
        if field.is_required()
    }

    assert schema_required == pydantic_required


@pytest.mark.parametrize(
    ("field_path", "expected_values", "bad_value"),
    [
        (("schema_version",), ["irene-pass-2-authoring.v1"], "v2"),
        (("composition_mode",), ["isolated", "composed"], "parallel"),
        (
            ("segment_manifest", "segments", 0, "visual_detail_load"),
            ["light", "medium", "heavy"],
            "very_high",
        ),
        (
            ("segment_manifest", "segments", 0, "content_density"),
            ["light", "medium", "heavy"],
            "dense",
        ),
        (
            ("segment_manifest", "segments", 0, "bridge_type"),
            ["none", "intro", "outro", "pivot", "both", "cluster_boundary"],
            "handoff",
        ),
        (("segment_manifest", "segments", 0, "cluster_role"), ["head", "interstitial"], "body"),
        (
            ("segment_manifest", "segments", 0, "cluster_position"),
            ["establish", "tension", "develop", "resolve"],
            "wrap",
        ),
        (
            ("procedural_rules", 0),
            list(REQUIRED_PROCEDURAL_RULES),
            "phantom_rule_unknown_value",
        ),
    ],
)
def test_closed_enums_reject_red_three_surfaces(
    field_path: tuple[object, ...],
    expected_values: list[str],
    bad_value: str,
) -> None:
    payload = _payload()
    cursor = payload
    for part in field_path[:-1]:
        cursor = cursor[part]  # type: ignore[index]
    cursor[field_path[-1]] = bad_value  # type: ignore[index]

    with pytest.raises(ValidationError):
        IrenePass2AuthoringEnvelope.model_validate(payload)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, IrenePass2AuthoringEnvelope.model_json_schema())

    schema = IrenePass2AuthoringEnvelope.model_json_schema()
    field_schema = schema
    for part in field_path:
        if isinstance(part, str):
            if "$ref" in field_schema:
                ref = field_schema["$ref"].split("/")[-1]
                field_schema = schema["$defs"][ref]
            field_schema = field_schema["properties"][part]
        elif isinstance(part, int):
            field_schema = field_schema["items"]
            if "$ref" in field_schema:
                ref = field_schema["$ref"].split("/")[-1]
                field_schema = schema["$defs"][ref]
    actual_values = field_schema.get("enum") or [field_schema.get("const")]
    if "anyOf" in field_schema:
        actual_values = next(
            branch["enum"]
            for branch in field_schema["anyOf"]
            if "enum" in branch
        )
    assert actual_values == expected_values
    assert bad_value not in actual_values

    bad_payload = _payload()
    cursor = bad_payload
    for part in field_path[:-1]:
        cursor = cursor[part]  # type: ignore[index]
    cursor[field_path[-1]] = bad_value  # type: ignore[index]
    with pytest.raises(ValidationError):
        TypeAdapter(IrenePass2AuthoringEnvelope).validate_python(bad_payload)


def test_procedural_rules_partial_rejected() -> None:
    payload = _payload()
    payload["procedural_rules"] = ["behavioral_intent_parity"]

    with pytest.raises(ValidationError, match="at least 6 items"):
        IrenePass2AuthoringEnvelope.model_validate(payload)

    payload = _payload()
    payload["procedural_rules"] = list(reversed(REQUIRED_PROCEDURAL_RULES))
    with pytest.raises(ValidationError, match="validator-enforced rule set"):
        IrenePass2AuthoringEnvelope.model_validate(payload)


def test_json_schema_rejects_remote_png_urls() -> None:
    """6.4-SP2-BH-1: JSON Schema must reject remote .png URLs."""
    schema = IrenePass2AuthoringEnvelope.model_json_schema()
    remote_urls = (
        "https://example.com/slide.png",
        "http://x/y.png",
        "file:///etc/slide.png",
        "ftp://srv/s.png",
    )
    field_paths = (
        ("gary_slide_output", 0, "file_path"),
        ("perception_artifacts", 0, "source_image_path"),
        ("segment_manifest", "segments", 0, "visual_file"),
    )

    for remote_url in remote_urls:
        for field_path in field_paths:
            payload = _payload()
            cursor = payload
            for part in field_path[:-1]:
                cursor = cursor[part]  # type: ignore[index]
            cursor[field_path[-1]] = remote_url  # type: ignore[index]

            with pytest.raises(jsonschema.ValidationError):
                jsonschema.validate(payload, schema)
            with pytest.raises(ValidationError):
                IrenePass2AuthoringEnvelope.model_validate(payload)


def test_cross_artifact_path_and_segment_marker_shape_pins() -> None:
    payload = _payload()
    payload["perception_artifacts"][0]["source_image_path"] = "bundle/other.png"  # type: ignore[index]
    with pytest.raises(ValidationError, match="source_image_path must match"):
        IrenePass2AuthoringEnvelope.model_validate(payload)

    payload = _payload()
    payload["narration_script_markers"] = ["different-seg"]
    with pytest.raises(ValidationError, match="absent from narration_script_markers"):
        IrenePass2AuthoringEnvelope.model_validate(payload)

    payload = _payload()
    payload["segment_manifest"]["segments"][0]["visual_file"] = "bundle/other.png"
    with pytest.raises(ValidationError, match="visual_file must match"):
        IrenePass2AuthoringEnvelope.model_validate(payload)

    payload = _payload()
    payload["segment_manifest"]["segments"][0]["card_number"] = 2
    with pytest.raises(ValidationError, match="card_number must match"):
        IrenePass2AuthoringEnvelope.model_validate(payload)

    payload = _payload()
    del payload["segment_manifest"]["segments"][0]["cluster_role"]
    with pytest.raises(ValidationError, match="cluster_role is required"):
        IrenePass2AuthoringEnvelope.model_validate(payload)


def test_markdown_template_field_names_match_pydantic_model() -> None:
    text = MARKDOWN.read_text(encoding="utf-8")
    referenced = set(re.findall(r"`([a-z_]+)`", text))
    model_field_names: set[str] = set()
    for model in (
        IrenePass2AuthoringEnvelope,
        GarySlideOutput,
        PerceptionArtifact,
        SegmentManifest,
        SegmentManifestSegment,
        VisualReference,
    ):
        assert issubclass(model, BaseModel)
        model_field_names.update(model.model_fields)
    assert referenced
    assert referenced.issubset(model_field_names)


def test_no_intake_orchestrator_leak_pass_2_template() -> None:
    text = MARKDOWN.read_text(encoding="utf-8").lower()

    forbidden_terms = [
        "state/config/schemas/segment-manifest.schema.json",
        "pass_2_emission_lint.py",
        "generated_by",
        "visual_mode",
        "motion_asset",
        "motion_duration_seconds",
        "reading_path",
        "retrieval-intake",
        "retrieval_provenance",
    ]
    assert [term for term in forbidden_terms if term in text] == []


def test_template_and_validator_cross_link_bidirectionally() -> None:
    markdown = MARKDOWN.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")

    assert "validate-irene-pass2-handoff.py" in markdown
    assert "pass-2-authoring-template.md" in validator
