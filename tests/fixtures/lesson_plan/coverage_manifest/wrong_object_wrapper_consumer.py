"""Fixture: wrapper calls canonical gate on the wrong object."""

from app.marcus.lesson_plan.log import assert_plan_fresh


def _require_fresh(surface) -> None:
    wrong_surface = object()
    assert_plan_fresh(wrong_surface)


def consume(surface) -> str:
    _require_fresh(surface)
    return "consumed"
