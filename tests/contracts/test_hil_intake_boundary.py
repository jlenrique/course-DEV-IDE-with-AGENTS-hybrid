"""AST boundary contracts for marcus/orchestrator/hil_intake.py — Story 32-5 AC-T.9.

Asserts:
1. hil_intake.py has no import from marcus.intake.* (Intake boundary — AC-E.1)
2. hil_intake.py has no direct import of LessonPlanLog (AC-E.2 defense-in-depth)
3. MissingIntakeDecisionError message contains no forbidden tokens (AC-E.3)
"""

from __future__ import annotations

import ast
from pathlib import Path

_HIL_INTAKE = Path(__file__).parents[2] / "app" / "marcus" / "orchestrator" / "hil_intake.py"
_FORBIDDEN_TOKENS = frozenset({"intake", "orchestrator", "dispatch"})


def _collect_imports(source: str) -> list[tuple[str, ...]]:
    """Return list of (module_name,) tuples for all imports."""
    tree = ast.parse(source)
    imports: list[tuple[str, ...]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name,))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.module,))
    return imports


def test_hil_intake_no_import_from_marcus_intake() -> None:
    """AC-T.9 / AC-E.1: hil_intake.py must not import from marcus.intake.*"""
    source = _HIL_INTAKE.read_text(encoding="utf-8")
    all_imports = _collect_imports(source)
    violations = [m for (m,) in all_imports if m.startswith("marcus.intake")]
    assert violations == [], (
        f"hil_intake.py imports from marcus.intake (boundary violation): {violations}"
    )


def test_hil_intake_no_direct_lesson_plan_log_import() -> None:
    """AC-T.9 / AC-E.2: hil_intake.py must not import LessonPlanLog directly."""
    source = _HIL_INTAKE.read_text(encoding="utf-8")
    all_imports = _collect_imports(source)
    log_imports = [
        m for (m,) in all_imports
        if "lesson_plan.log" in m or "LessonPlanLog" in m
    ]
    assert log_imports == [], (
        f"hil_intake.py imports LessonPlanLog directly (AC-E.2 violation): {log_imports}"
    )


def test_missing_intake_decision_error_message_no_forbidden_tokens() -> None:
    """AC-T.9 / AC-E.3: MissingIntakeDecisionError has no Voice Register forbidden tokens."""
    from app.marcus.orchestrator.hil_intake import MissingIntakeDecisionError

    err = MissingIntakeDecisionError("u-test")
    message = str(err).lower()
    for token in _FORBIDDEN_TOKENS:
        assert token not in message, (
            f"Forbidden token {token!r} found in error message: {str(err)!r}"
        )
