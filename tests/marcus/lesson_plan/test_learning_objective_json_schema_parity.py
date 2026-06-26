"""JSON-Schema parity + enum-surface for LearningObjective (Story G0-S1 AC-S1-4).

Bidirectional required-vs-optional parity (checklist 9), additionalProperties
propagation (checklist 14), emitted JSON-Schema enum array (checklist 4 surface 2),
and witness-vs-live byte currency (regen discipline). RED-first.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic_core import PydanticUndefined

from app.marcus.lesson_plan.learning_objective import (
    SCHEMA_VERSION,
    LearningObjective,
    SourceAdequacy,
    SourceRef,
    learning_objective_json_schema,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "marcus"
    / "lesson_plan"
    / "schema"
    / "learning_objective.v1.schema.json"
)

_FAMILY = {
    "LearningObjective": LearningObjective,
    "SourceRef": SourceRef,
    "SourceAdequacy": SourceAdequacy,
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
    assert SCHEMA_PATH.exists(), f"Expected schema witness missing: {SCHEMA_PATH}"


def test_emitted_schema_is_byte_current_vs_live() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema == learning_objective_json_schema()


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
        assert not (pyd_required - json_required), f"{model_name}: pyd>json"
        assert not (json_required - pyd_required), f"{model_name}: json>pyd"


def test_additional_properties_false_propagates_everywhere() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for model_name in _FAMILY:
        schema_def = _schema_def(schema, model_name)
        assert schema_def.get("additionalProperties") is False, model_name


def _collect_enum_arrays(node: object) -> list[frozenset[str]]:
    """Every ``enum`` array in the schema, as frozensets (structural, not substring)."""
    found: list[frozenset[str]] = []
    if isinstance(node, dict):
        enum = node.get("enum")
        if isinstance(enum, list):
            found.append(frozenset(enum))
        for value in node.values():
            found.extend(_collect_enum_arrays(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_collect_enum_arrays(item))
    return found


def test_closed_enums_present_in_emitted_schema() -> None:
    # Structural: each closed enum must appear as a COMPLETE `enum` array, not as
    # a substring of the JSON blob. (A substring check is tautological -- e.g.
    # "low" is inside "suggested_followups" and "gap" inside "gaps" -- so it would
    # pass even if the Confidence/AdequacyVerdict enum were deleted.)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    enum_sets = _collect_enum_arrays(schema)
    expected = [
        frozenset({"remember", "understand", "apply", "analyze", "evaluate", "create"}),
        frozenset({"provisional", "refined", "ratified"}),
        frozenset({"high", "medium", "low"}),
        frozenset({"adequate", "thin", "gap"}),
        frozenset({"research-run", "external-content-expected", "special-artifact-guidance"}),
    ]
    for exp in expected:
        assert exp in enum_sets, sorted(exp)


def test_schema_version_major_matches_file_name() -> None:
    major = SCHEMA_VERSION.split(".", 1)[0]
    assert f".v{major}." in SCHEMA_PATH.name
