from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from app.specialists.irene.authoring.pass_2_template import (
    IrenePass2AuthoringEnvelope,
    SegmentManifestSegment,
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


def test_visual_detail_load_closed_enum_rejects_red_three_surfaces() -> None:
    payload = _payload()
    segment = payload["segment_manifest"]["segments"][0]  # type: ignore[index]
    segment["visual_detail_load"] = "overwhelming"  # type: ignore[index]
    with pytest.raises(ValidationError):
        IrenePass2AuthoringEnvelope.model_validate(payload)

    valid_segment = _payload()["segment_manifest"]["segments"][0]  # type: ignore[index]
    model = SegmentManifestSegment.model_validate(valid_segment)
    with pytest.raises(ValidationError):
        model.visual_detail_load = "overwhelming"  # type: ignore[assignment]

    schema = SegmentManifestSegment.model_json_schema()
    enum_values = schema["properties"]["visual_detail_load"]["enum"]
    assert enum_values == ["low", "medium", "high"]
    adapter = TypeAdapter(SegmentManifestSegment)
    with pytest.raises(ValidationError):
        bad = dict(valid_segment)
        bad["visual_detail_load"] = "overwhelming"
        adapter.validate_python(bad)


def test_cross_artifact_path_and_segment_marker_shape_pins() -> None:
    payload = _payload()
    payload["perception_artifacts"][0]["source_image_path"] = "bundle/other.png"  # type: ignore[index]
    with pytest.raises(ValidationError, match="source_image_path must match"):
        IrenePass2AuthoringEnvelope.model_validate(payload)

    payload = _payload()
    payload["narration_script_markers"] = ["different-seg"]
    with pytest.raises(ValidationError, match="absent from narration_script_markers"):
        IrenePass2AuthoringEnvelope.model_validate(payload)


def test_markdown_template_field_names_match_pydantic_model() -> None:
    text = MARKDOWN.read_text(encoding="utf-8")
    match = re.search(
        r"<!-- irene-pass2-pydantic-fields:start -->(.*?)<!-- irene-pass2-pydantic-fields:end -->",
        text,
        flags=re.S,
    )
    assert match is not None
    referenced = set(re.findall(r"`([a-z_]+)`", match.group(1)))

    assert referenced
    assert referenced.issubset(set(IrenePass2AuthoringEnvelope.model_fields))


def test_template_and_validator_cross_link_bidirectionally() -> None:
    markdown = MARKDOWN.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")

    assert "validate-irene-pass2-handoff.py" in markdown
    assert "pass-2-authoring-template.md" in validator
