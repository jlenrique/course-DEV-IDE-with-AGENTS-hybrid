"""JSON-Schema parity + no-leak propagation for CollateralSpec (Braid S1, AC-7).

Bidirectional required-vs-optional parity (checklist §9) + additionalProperties
propagation (checklist §14). RED-first: written before the schema is emitted.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic_core import PydanticUndefined

from app.marcus.lesson_plan.collateral_spec import (
    SCHEMA_VERSION,
    CollateralSpec,
    DepthDeltaContract,
    Exercise,
    ResearchEnrichmentGoal,
    WorkbookSection,
    WorkbookSpec,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "marcus"
    / "lesson_plan"
    / "schema"
    / "collateral_spec.v1.schema.json"
)

_FAMILY = {
    "CollateralSpec": CollateralSpec,
    "WorkbookSpec": WorkbookSpec,
    "WorkbookSection": WorkbookSection,
    "DepthDeltaContract": DepthDeltaContract,
    "Exercise": Exercise,
    "ResearchEnrichmentGoal": ResearchEnrichmentGoal,
}


def _schema_def(schema: dict, model_name: str) -> dict:
    if schema.get("title") == model_name:
        return schema
    return schema["$defs"][model_name]


def _pydantic_required(model_cls) -> set[str]:
    return {
        name
        for name, field in model_cls.model_fields.items()
        if field.default is PydanticUndefined and field.default_factory is None
    }


def test_emitted_schema_exists() -> None:
    assert SCHEMA_PATH.exists(), f"Expected schema file missing: {SCHEMA_PATH}"


def test_emitted_schema_matches_live_for_every_family_member() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for model_name, model_cls in _FAMILY.items():
        schema_def = _schema_def(schema, model_name)
        assert set(schema_def["properties"].keys()) == set(
            model_cls.model_fields.keys()
        ), model_name


def test_required_field_parity_bidirectional() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for model_name, model_cls in _FAMILY.items():
        schema_def = _schema_def(schema, model_name)
        json_required = set(schema_def.get("required", []))
        pyd_required = _pydantic_required(model_cls)
        # Pydantic -> JSON
        assert not (pyd_required - json_required), f"{model_name}: pyd>json"
        # JSON -> Pydantic
        assert not (json_required - pyd_required), f"{model_name}: json>pyd"


def test_additional_properties_false_propagates_everywhere() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for model_name in _FAMILY:
        schema_def = _schema_def(schema, model_name)
        assert schema_def.get("additionalProperties") is False, model_name


def test_emitted_schema_has_version_field() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    top = _schema_def(schema, "CollateralSpec")
    assert "schema_version" in top["properties"]


def test_bloom_enum_present_in_emitted_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    blob = json.dumps(schema)
    for level in (
        "remember",
        "understand",
        "apply",
        "analyze",
        "evaluate",
        "create",
    ):
        assert level in blob


def test_emitted_schema_is_byte_current_vs_live() -> None:
    # The committed witness must equal the live model_json_schema() output so a
    # silent schema drift fails CI (regen discipline).
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    live = CollateralSpec.model_json_schema()
    assert schema == live


def test_schema_version_major_matches_file_name() -> None:
    # Sibling convention (lesson_plan.v1.schema.json, coverage_manifest.v1...):
    # the filename carries the MAJOR version; SCHEMA_VERSION carries major.minor.
    major = SCHEMA_VERSION.split(".", 1)[0]
    assert f".v{major}." in SCHEMA_PATH.name
