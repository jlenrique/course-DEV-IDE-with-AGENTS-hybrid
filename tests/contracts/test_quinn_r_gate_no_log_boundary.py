"""Contract tests for Story 31-5 log-boundary discipline."""

from __future__ import annotations

from pathlib import Path


def test_quinn_r_gate_does_not_call_lesson_plan_log_write_surface() -> None:
    # Path repinned marcus/ -> app/marcus/ (s2-marcus-collapse) and anchored
    # to the repo root instead of CWD; forbidden import token updated to the
    # current app.marcus namespace so it keeps teeth.
    # See contracts-triage-ledger-2026-07-02 row 16.
    module_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "marcus"
        / "lesson_plan"
        / "quinn_r_gate.py"
    )
    module_text = module_path.read_text(encoding="utf-8")
    forbidden_tokens = [
        "LessonPlanLog",
        "append_event(",
        "write_event(",
        "emit_fit_report(",
        "from app.marcus.lesson_plan.log import",
    ]
    for token in forbidden_tokens:
        assert token not in module_text

