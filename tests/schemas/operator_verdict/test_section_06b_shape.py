from __future__ import annotations

import json
from pathlib import Path

from app.models.operator_verdict_section_06b import (
    SECTION_06B_SURFACE_ID,
    LiteralVisualBuildPayload,
    LiteralVisualEditPayload,
    Section06BOperatorVerdict,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_06b.v1.schema.json")


def test_section_06b_operator_verdict_schema_hash_stable_across_transports() -> None:
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section06BOperatorVerdict,
        surface_id=SECTION_06B_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_06b_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section06BOperatorVerdict.model_json_schema()

    assert SECTION_06B_SURFACE_ID == "section_06b_literal_visual_build"
    assert schema["properties"]["surface_id"]["const"] == (
        "section_06b_literal_visual_build"
    )


def test_section_06b_payload_schemas_are_nested() -> None:
    schema = Section06BOperatorVerdict.model_json_schema()

    assert "LiteralVisualBuildPayload" in schema["$defs"]
    assert "LiteralVisualEditPayload" in schema["$defs"]
    assert schema["$defs"]["LiteralVisualEditPayload"] == (
        LiteralVisualEditPayload.model_json_schema()
    )
    assert "SlideVisualSpecification" in schema["$defs"]
    assert set(LiteralVisualBuildPayload.model_fields).issubset(
        schema["$defs"]["LiteralVisualBuildPayload"]["properties"]
    )


def test_section_06b_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section06BOperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
