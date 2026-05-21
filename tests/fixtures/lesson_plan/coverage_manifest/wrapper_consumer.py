"""Fixture: same-module thin wrapper around the canonical freshness gate."""

from app.marcus.lesson_plan.log import assert_plan_fresh


def _require_fresh(surface) -> None:
    assert_plan_fresh(surface)


def consume(surface) -> str:
    _require_fresh(surface)
    return "consumed"
