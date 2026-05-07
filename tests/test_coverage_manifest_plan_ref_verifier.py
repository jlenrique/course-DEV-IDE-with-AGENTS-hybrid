"""AC-T.4 + AC-T.5 — top-level and nested plan-ref verification."""

from __future__ import annotations

from types import SimpleNamespace

from app.marcus.lesson_plan.coverage_manifest import verify_plan_ref_fields
from app.marcus.lesson_plan.schema import PlanRef


def test_verify_plan_ref_fields_top_level_matrix() -> None:
    assert verify_plan_ref_fields(
        SimpleNamespace(lesson_plan_revision=7, lesson_plan_digest="abc"),
        "top-level-fields",
    ) == (True, True)
    assert verify_plan_ref_fields(
        SimpleNamespace(lesson_plan_revision=7),
        "top-level-fields",
    ) == (True, False)
    assert verify_plan_ref_fields(
        {"lesson_plan_digest": "abc"},
        "top-level-fields",
    ) == (False, True)


def test_verify_plan_ref_fields_nested_matrix() -> None:
    assert verify_plan_ref_fields(
        SimpleNamespace(plan_ref=PlanRef(lesson_plan_revision=3, lesson_plan_digest="xyz")),
        "nested-plan-ref",
    ) == (True, True)
    assert verify_plan_ref_fields(
        {"plan_ref": {"lesson_plan_revision": 3}},
        "nested-plan-ref",
    ) == (True, False)
    assert verify_plan_ref_fields(
        SimpleNamespace(plan_ref=None),
        "nested-plan-ref",
    ) == (False, False)
