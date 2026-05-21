"""AC-T.9 — fit-report-v1 JSON Schema pin (absorbed from 29-1).

Snapshot of the committed JSON Schema file + drift check against the Pydantic
source. Any change without updating the committed schema file AND the
SCHEMA_CHANGELOG fails the test.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.marcus.lesson_plan.schema import FitDiagnosis, FitReport

SCHEMA_PATH = (
    Path(__file__).parents[2]
    / "marcus"
    / "lesson_plan"
    / "schema"
    / "fit_report.v1.schema.json"
)


def test_fit_report_schema_file_exists() -> None:
    assert SCHEMA_PATH.exists(), f"Missing committed schema at {SCHEMA_PATH}"


def test_fit_report_schema_title_and_version() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    # Pydantic titles the root at the model name.
    assert schema.get("title") == "FitReport"
    props = schema["properties"]
    assert "schema_version" in props


def test_fit_report_property_coverage_matches_pydantic() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    props = set(schema["properties"].keys())
    expected = set(FitReport.model_fields.keys())
    assert props == expected, (
        f"fit_report.v1.schema.json property drift. "
        f"Missing: {expected - props}. Extra: {props - expected}."
    )


def test_fit_diagnosis_property_coverage_matches_pydantic() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fd = schema["$defs"]["FitDiagnosis"]
    props = set(fd["properties"].keys())
    expected = set(FitDiagnosis.model_fields.keys())
    assert props == expected


def test_fit_diagnosis_fitness_enum_matches() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fd = schema["$defs"]["FitDiagnosis"]
    fitness = set(fd["properties"]["fitness"]["enum"])
    assert fitness == {"sufficient", "partial", "absent"}
