"""29-3 contract pin: blueprint co-authoring must not emit to log surfaces."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "app" / "marcus" / "lesson_plan" / "blueprint_coauthor.py"


def test_blueprint_coauthor_does_not_import_emit_fit_report_or_log_writer() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8")
    assert "emit_fit_report" not in text
    assert "LessonPlanLog" not in text
    assert ".append_event(" not in text, (
        "29-3 must prepare a typed blueprint sign-off pointer only; "
        "log emission stays outside this story."
    )
