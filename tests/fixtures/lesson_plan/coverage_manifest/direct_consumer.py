"""Fixture: direct canonical assert_plan_fresh call on the live entry path."""

from app.marcus.lesson_plan.log import assert_plan_fresh


def consume(surface) -> str:
    assert_plan_fresh(surface)
    return "consumed"
