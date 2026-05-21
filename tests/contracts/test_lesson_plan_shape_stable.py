"""AC-T.1 — LessonPlan / PlanUnit / Dials / IdentifiedGap shape-pin (R2 AM-1).

Snapshot + allowlist + SCHEMA_CHANGELOG.md gate pattern (inherited from 27-0).
Any change to these shapes without a matching snapshot update here AND a
matching `Lesson Plan v1.0` or later entry in the changelog fails the test.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.marcus.lesson_plan.schema import Dials, IdentifiedGap, LessonPlan, PlanUnit

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


SNAPSHOT = _load_snapshot("lesson_plan_v1_0.json")


def test_lesson_plan_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["LessonPlan"])
    actual = _field_names(LessonPlan)
    missing = expected - actual
    extra = actual - expected
    assert not missing, f"LessonPlan missing fields per snapshot: {missing}"
    assert not extra, (
        f"LessonPlan has NEW fields not in snapshot: {extra}. "
        f"Update fixtures/lesson_plan/lesson_plan_v1_0.json AND add a "
        f"SCHEMA_CHANGELOG.md entry explaining the bump."
    )


def test_plan_unit_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["PlanUnit"])
    actual = _field_names(PlanUnit)
    assert actual == expected, (
        f"PlanUnit schema drift. Missing: {expected - actual}. New: {actual - expected}."
    )


def test_dials_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["Dials"])
    actual = _field_names(Dials)
    assert actual == expected


def test_identified_gap_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["IdentifiedGap"])
    actual = _field_names(IdentifiedGap)
    assert actual == expected


def test_schema_changelog_pins_lesson_plan_v1_0() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "Lesson Plan v1.0" in text, (
        "SCHEMA_CHANGELOG.md does not pin `Lesson Plan v1.0` — per R2 AM-1 the "
        "lesson_plan / plan_unit / dials / identified_gap shape family requires "
        "its own changelog entry."
    )
    assert "Story 31-1" in text, "Changelog entry must attribute to Story 31-1"
