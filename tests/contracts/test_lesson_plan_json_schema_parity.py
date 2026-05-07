"""AC-T.2 + AC-T.2.d — JSON-Schema / Pydantic parity (R2 rider AM-2).

Validates the committed JSON Schema files stay in sync with the Pydantic
source of truth on:
    (a) field presence,
    (b) enum membership parity,
    (c) model_dump round-trip fidelity (via jsonschema, opportunistically),
    (d) required-vs-optional bidirectional parity (R2 AM-2 / AC-T.2.d).

The internal audit fields (``internal_proposed_by`` / ``internal_actor``) are
intentionally EXCLUDED from the JSON Schema via ``SkipJsonSchema`` per R2
rider S-4. Parity assertions filter them out on the Pydantic side.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan.schema import (
    BlueprintSignoff,
    Dials,
    FitDiagnosis,
    FitReport,
    IdentifiedGap,
    LearningModel,
    LessonPlan,
    PlanUnit,
    ScopeDecision,
)

SCHEMAS_DIR = Path(__file__).parents[2] / "app" / "marcus" / "lesson_plan" / "schema"

# Fields intentionally hidden from the published JSON Schema (R2 S-4).
_SKIP_JSON_SCHEMA_FIELDS: dict[type, set[str]] = {
    ScopeDecision: {"internal_proposed_by"},
}


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def _pydantic_fields_visible_to_json_schema(model_cls) -> set[str]:
    skip = _SKIP_JSON_SCHEMA_FIELDS.get(model_cls, set())
    return set(model_cls.model_fields.keys()) - skip


def _pydantic_required_fields(model_cls) -> set[str]:
    """Pydantic fields declared without a default (i.e. PydanticUndefined)."""
    from pydantic_core import PydanticUndefined

    skip = _SKIP_JSON_SCHEMA_FIELDS.get(model_cls, set())
    required: set[str] = set()
    for name, field in model_cls.model_fields.items():
        if name in skip:
            continue
        if field.default is PydanticUndefined and field.default_factory is None:
            required.add(name)
    return required


def _json_schema_required_for(schema: dict, model_name: str) -> set[str]:
    """Find the `required` array for ``model_name`` inside a Pydantic-emitted schema.

    SF-8: raises AssertionError with an explicit message if ``model_name`` is
    not found in ``$defs`` or at the root — silent fallback-to-empty-set hid
    drift when a def was renamed or removed. A def that IS present but has no
    ``required`` array (all fields optional) returns ``set()`` — legitimate.
    """
    if schema.get("title") == model_name:
        return set(schema.get("required", []))
    defs = schema.get("$defs") or {}
    if model_name in defs:
        return set(defs[model_name].get("required", []))
    raise AssertionError(
        f"{model_name} not found in schema $defs; "
        f"available defs: {sorted(defs.keys())}"
    )


# ---------------------------------------------------------------------------
# AC-T.2 (a) field presence
# ---------------------------------------------------------------------------


def test_lesson_plan_root_fields_present_in_schema() -> None:
    schema = _load_schema("lesson_plan.v1.schema.json")
    root_props = set(schema["properties"].keys())
    pydantic_fields = _pydantic_fields_visible_to_json_schema(LessonPlan)
    assert root_props == pydantic_fields, (
        f"LessonPlan JSON Schema / Pydantic field drift: "
        f"missing in schema={pydantic_fields - root_props}, "
        f"missing in model={root_props - pydantic_fields}"
    )


def test_fit_report_root_fields_present_in_schema() -> None:
    schema = _load_schema("fit_report.v1.schema.json")
    root_props = set(schema["properties"].keys())
    pydantic_fields = _pydantic_fields_visible_to_json_schema(FitReport)
    assert root_props == pydantic_fields


def test_scope_decision_def_hides_internal_field() -> None:
    """R2 S-4: ``internal_proposed_by`` MUST NOT appear in the JSON Schema."""
    schema = _load_schema("lesson_plan.v1.schema.json")
    sd_def = (schema.get("$defs") or {}).get("ScopeDecision", {})
    assert "internal_proposed_by" not in sd_def.get("properties", {}), (
        "ScopeDecision.internal_proposed_by leaked into the published JSON Schema. "
        "Use SkipJsonSchema on the Literal type."
    )


# ---------------------------------------------------------------------------
# AC-T.2 (b) enum parity
# ---------------------------------------------------------------------------


def test_scope_decision_scope_enum_parity() -> None:
    schema = _load_schema("lesson_plan.v1.schema.json")
    sd_def = schema["$defs"]["ScopeDecision"]
    scope_enum = set(sd_def["properties"]["scope"]["enum"])
    assert scope_enum == {"in-scope", "out-of-scope", "delegated", "blueprint"}


def test_plan_unit_weather_band_enum_parity() -> None:
    schema = _load_schema("lesson_plan.v1.schema.json")
    pu_def = schema["$defs"]["PlanUnit"]
    wb = set(pu_def["properties"]["weather_band"]["enum"])
    assert wb == {"gold", "green", "amber", "gray"}, (
        "weather_band enum drift — red MUST NOT appear. AC-B.7 / R2 S-1."
    )
    assert "red" not in wb


def test_plan_unit_blueprint_signoff_field_is_optional_and_present() -> None:
    schema = _load_schema("lesson_plan.v1.schema.json")
    pu_def = schema["$defs"]["PlanUnit"]
    assert "blueprint_signoff" in pu_def["properties"]
    assert "blueprint_signoff" not in pu_def.get("required", [])


# ---------------------------------------------------------------------------
# AC-T.2 (c) model_dump round-trip
# ---------------------------------------------------------------------------


def test_lesson_plan_model_dump_roundtrip() -> None:
    sd = ScopeDecision(
        state="proposed",
        scope="in-scope",
        proposed_by="system",
        _internal_proposed_by="marcus",
    )
    pu = PlanUnit(
        unit_id="gagne-event-1",
        event_type="gagne-event-1",
        source_fitness_diagnosis="ok",
        scope_decision=sd,
        weather_band="gold",
        rationale="test",
    )
    lp = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[pu],
        revision=1,
        updated_at=datetime.now(tz=UTC),
    )
    dumped = lp.model_dump(mode="json")
    # Round-trip back through model_validate.
    restored = LessonPlan.model_validate(dumped)
    assert restored.revision == 1
    assert restored.plan_units[0].weather_band == "gold"


# ---------------------------------------------------------------------------
# AC-T.2.d — required-vs-optional bidirectional parity (R2 AM-2)
# ---------------------------------------------------------------------------


def test_required_optional_parity_lesson_plan() -> None:
    schema = _load_schema("lesson_plan.v1.schema.json")
    expected_required = _pydantic_required_fields(LessonPlan)
    actual_required = _json_schema_required_for(schema, "LessonPlan")
    missing = expected_required - actual_required
    extra = actual_required - expected_required
    assert not missing, (
        f"LessonPlan: field(s) required in Pydantic but missing from JSON "
        f"Schema `required` array: {missing}"
    )
    assert not extra, (
        f"LessonPlan: field(s) in JSON Schema `required` array that are "
        f"optional in Pydantic: {extra}"
    )


def test_required_optional_parity_plan_unit() -> None:
    schema = _load_schema("lesson_plan.v1.schema.json")
    expected_required = _pydantic_required_fields(PlanUnit)
    actual_required = _json_schema_required_for(schema, "PlanUnit")
    missing = expected_required - actual_required
    extra = actual_required - expected_required
    assert not missing, (
        f"PlanUnit: required-in-Pydantic not required-in-JSON: {missing}"
    )
    assert not extra, (
        f"PlanUnit: required-in-JSON not required-in-Pydantic: {extra}"
    )


def test_required_optional_parity_scope_decision() -> None:
    schema = _load_schema("lesson_plan.v1.schema.json")
    expected_required = _pydantic_required_fields(ScopeDecision)
    actual_required = _json_schema_required_for(schema, "ScopeDecision")
    missing = expected_required - actual_required
    extra = actual_required - expected_required
    assert not missing, f"ScopeDecision: required drift: missing={missing}"
    assert not extra, f"ScopeDecision: required drift: extra={extra}"


def test_required_optional_parity_fit_report() -> None:
    schema = _load_schema("fit_report.v1.schema.json")
    expected_required = _pydantic_required_fields(FitReport)
    actual_required = _json_schema_required_for(schema, "FitReport")
    assert actual_required == expected_required, (
        f"FitReport required-optional parity drift: "
        f"missing={expected_required - actual_required} "
        f"extra={actual_required - expected_required}"
    )


# ---------------------------------------------------------------------------
# SF-11 — extend AM-2 parity to additional shape definitions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model_cls,model_name,schema_file",
    [
        (FitDiagnosis, "FitDiagnosis", "fit_report.v1.schema.json"),
        (BlueprintSignoff, "BlueprintSignoff", "lesson_plan.v1.schema.json"),
        (Dials, "Dials", "lesson_plan.v1.schema.json"),
        (IdentifiedGap, "IdentifiedGap", "lesson_plan.v1.schema.json"),
    ],
)
def test_required_optional_parity_extended_shapes(
    model_cls: type, model_name: str, schema_file: str
) -> None:
    """AM-2 parity for ``FitDiagnosis`` + ``Dials`` + ``IdentifiedGap`` (SF-11).

    Uses the SF-8-hardened ``_json_schema_required_for`` helper — an explicit
    ``AssertionError`` is raised if the def is not found in ``$defs``.
    """
    schema = _load_schema(schema_file)
    expected_required = _pydantic_required_fields(model_cls)
    actual_required = _json_schema_required_for(schema, model_name)
    missing = expected_required - actual_required
    extra = actual_required - expected_required
    assert not missing, f"{model_name}: required-in-Pydantic not required-in-JSON: {missing}"
    assert not extra, f"{model_name}: required-in-JSON not required-in-Pydantic: {extra}"
