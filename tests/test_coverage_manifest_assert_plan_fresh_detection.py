"""AC-T.6 — AST/import-path-aware assert_plan_fresh detection."""

from __future__ import annotations

from pathlib import Path

from app.marcus.lesson_plan.coverage_manifest import verify_assert_plan_fresh_usage

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "lesson_plan" / "coverage_manifest"


def test_verify_assert_plan_fresh_usage_accepts_and_rejects_expected_fixtures() -> None:
    expectations = {
        "direct_consumer.py": True,
        "wrapper_consumer.py": True,
        "dead_wrapper_consumer.py": False,
        "counterfeit_helper_consumer.py": False,
        "wrong_object_wrapper_consumer.py": False,
    }
    for filename, expected in expectations.items():
        assert (
            verify_assert_plan_fresh_usage(FIXTURES / filename, entrypoint_name="consume")
            is expected
        ), filename
