"""AC-T.5 — weather_band enum + no-red validator tests (Sally).

Three-layer rejection:
    (1) direct construction,
    (2) JSON deserialization via model_validate,
    (3) JSON Schema enum path.
Plus positive tests for the four abundance-framed bands.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.schema import PlanUnit, ScopeDecision

SCHEMA_PATH = (
    Path(__file__).parents[1]
    / "marcus"
    / "lesson_plan"
    / "schema"
    / "lesson_plan.v1.schema.json"
)


def _base_unit(band: str) -> PlanUnit:
    sd = ScopeDecision(
        state="proposed",
        scope="in-scope",
        proposed_by="system",
        _internal_proposed_by="marcus",
    )
    return PlanUnit(
        unit_id="gagne-event-1",
        event_type="gagne-event-1",
        source_fitness_diagnosis="ok",
        scope_decision=sd,
        weather_band=band,  # type: ignore[arg-type]
        rationale="",
    )


@pytest.mark.parametrize("band", ["gold", "green", "amber", "gray"])
def test_weather_band_accepts_four_bands(band: str) -> None:
    pu = _base_unit(band)
    assert pu.weather_band == band


def test_weather_band_rejects_red_on_direct_construction() -> None:
    with pytest.raises(ValidationError) as exc:
        _base_unit("red")
    assert "red" in str(exc.value)


def test_weather_band_rejects_red_on_json_deserialization() -> None:
    sd = ScopeDecision(
        state="proposed",
        scope="in-scope",
        proposed_by="system",
        _internal_proposed_by="marcus",
    )
    bad_payload = {
        "unit_id": "gagne-event-1",
        "event_type": "gagne-event-1",
        "source_fitness_diagnosis": "ok",
        "scope_decision": sd.model_dump(),
        "weather_band": "red",
        "rationale": "",
    }
    with pytest.raises(ValidationError):
        PlanUnit.model_validate(bad_payload)


def test_weather_band_rejects_red_via_json_schema_path() -> None:
    """The schema file itself must not list `red` in the weather_band enum."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    pu_def = schema["$defs"]["PlanUnit"]
    enum = pu_def["properties"]["weather_band"]["enum"]
    assert "red" not in enum
    assert set(enum) == {"gold", "green", "amber", "gray"}


def test_weather_band_rejects_red_via_real_jsonschema_validate() -> None:
    """SF-10: a real ``jsonschema.validate`` call rejects ``weather_band="red"``.

    Strengthens the weaker "enum absent from schema text" assertion with a
    live validation call against the Pydantic-emitted JSON Schema.
    """
    import jsonschema

    from app.marcus.lesson_plan.schema import LessonPlan

    schema = LessonPlan.model_json_schema()
    bad_payload = {
        "schema_version": "1.0",
        "learning_model": {"id": "gagne-9", "version": 1},
        "structure": {},
        "plan_units": [
            {
                "unit_id": "gagne-event-1",
                "event_type": "gagne-event-1",
                "source_fitness_diagnosis": "ok",
                "scope_decision": {
                    "state": "proposed",
                    "scope": "in-scope",
                    "proposed_by": "system",
                    "ratified_by": None,
                    "locked_at": None,
                },
                "weather_band": "red",
                "modality_ref": None,
                "rationale": "",
                "gaps": [],
                "dials": None,
            }
        ],
        "revision": 1,
        "updated_at": "2026-04-18T12:00:00+00:00",
        "digest": "",
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad_payload, schema)


def test_recommended_weather_band_on_fit_diagnosis_also_rejects_red() -> None:
    from app.marcus.lesson_plan.schema import FitDiagnosis

    with pytest.raises(ValidationError):
        FitDiagnosis(
            unit_id="gagne-event-1",
            fitness="sufficient",
            commentary="ok",
            recommended_weather_band="red",  # type: ignore[arg-type]
        )


def test_weather_band_rejects_red_via_type_adapter() -> None:
    """G5-Murat: fourth surface — ``TypeAdapter(PlanUnit).validate_python`` rejects red.

    Closes Murat's G5-flagged AC-T.5d fourth rejection surface beyond
    direct construction, JSON deserialization, and JSON Schema path.
    """
    from pydantic import TypeAdapter

    from app.marcus.lesson_plan.schema import PlanUnit, ScopeDecision

    sd = ScopeDecision(
        state="proposed",
        scope="in-scope",
        proposed_by="system",
        _internal_proposed_by="marcus",
    )
    payload = {
        "unit_id": "gagne-event-1",
        "event_type": "gagne-event-1",
        "source_fitness_diagnosis": "ok",
        "scope_decision": sd.model_dump(),
        "weather_band": "red",
        "rationale": "",
    }
    with pytest.raises(ValidationError, match="red"):
        TypeAdapter(PlanUnit).validate_python(payload)
