"""AC-T.1 — FitReport / FitDiagnosis shape-pin (R2 AM-1).

Second of three shape-family pin files. Own snapshot + own changelog entry.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.marcus.lesson_plan.schema import FitDiagnosis, FitReport

FIXTURES = Path(__file__).parent / "fixtures" / "lesson_plan"
CHANGELOG = (
    Path(__file__).parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "SCHEMA_CHANGELOG.md"
)


def _load_snapshot(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _field_names(model_cls) -> set[str]:
    return set(model_cls.model_fields.keys())


SNAPSHOT = _load_snapshot("fit_shape_v1_0.json")


def test_fit_report_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["FitReport"])
    actual = _field_names(FitReport)
    assert actual == expected, (
        f"FitReport schema drift. Missing: {expected - actual}. New: {actual - expected}."
    )


def test_fit_diagnosis_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["FitDiagnosis"])
    actual = _field_names(FitDiagnosis)
    assert actual == expected, (
        f"FitDiagnosis schema drift. Missing: {expected - actual}. New: {actual - expected}."
    )


def test_schema_changelog_pins_fit_report_v1_0() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "Fit Report v1.0" in text, (
        "SCHEMA_CHANGELOG.md does not pin `Fit Report v1.0` — per R2 AM-1 the "
        "fit_report / fit_diagnosis shape family requires its own changelog entry."
    )
