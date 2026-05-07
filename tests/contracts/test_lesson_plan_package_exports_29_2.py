"""AC-C.1 - package exports for Story 29-2."""

from __future__ import annotations

import app.marcus.lesson_plan as pkg
EXPECTED_29_2_EXPORTS = {
    "DEFAULT_BUDGET_FALLBACK_MODE",
    "DuplicateDiagnosisTargetError",
    "PriorDeclinedRationale",
    "UnsupportedGagneEventTypeError",
    "diagnose_lesson_plan",
    "diagnose_plan_unit",
}


def test_marcus_lesson_plan_exports_all_29_2_names() -> None:
    actual = set(pkg.__all__)
    missing = EXPECTED_29_2_EXPORTS - actual
    assert not missing, (
        f"marcus.lesson_plan.__init__.py missing 29-2 exports: {missing}"
    )


def test_marcus_lesson_plan_29_2_exports_are_importable() -> None:
    for name in EXPECTED_29_2_EXPORTS:
        assert hasattr(pkg, name), (
            f"marcus.lesson_plan.{name} is declared in __all__ but not importable"
        )
