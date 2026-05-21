"""Fixture: wrapper exists but is not on the live consumer path."""

from app.marcus.lesson_plan.log import assert_plan_fresh


def _require_fresh(surface) -> None:
    assert_plan_fresh(surface)


def _downstream_process(surface) -> str:
    return f"processed:{surface}"


def consume(surface) -> str:
    return _downstream_process(surface)
