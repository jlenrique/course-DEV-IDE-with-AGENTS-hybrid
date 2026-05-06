from __future__ import annotations

import json
from pathlib import Path

from app.models.operator_verdict_section_07c import (
    SECTION_07C_SURFACE_ID,
    Section07COperatorVerdict,
    StoryboardBuildPayload,
    StoryboardEditPayload,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_07c.v1.schema.json")


def test_section_07c_operator_verdict_schema_hash_stable_across_transports() -> None:
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section07COperatorVerdict,
        surface_id=SECTION_07C_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_07c_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section07COperatorVerdict.model_json_schema()

    assert SECTION_07C_SURFACE_ID == "section_07c_storyboard_build"
    assert schema["properties"]["surface_id"]["const"] == (
        "section_07c_storyboard_build"
    )


def test_section_07c_payload_schemas_are_nested() -> None:
    schema = Section07COperatorVerdict.model_json_schema()

    assert "StoryboardBuildPayload" in schema["$defs"]
    assert "StoryboardEditPayload" in schema["$defs"]
    assert schema["$defs"]["StoryboardBuildPayload"] == (
        StoryboardBuildPayload.model_json_schema()
    )
    assert schema["$defs"]["StoryboardEditPayload"] == (
        StoryboardEditPayload.model_json_schema()
    )


def test_section_07c_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section07COperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
