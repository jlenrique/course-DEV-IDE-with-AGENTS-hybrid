"""29-2 contract pin: diagnostician code must not import the emitter surface."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "app" / "marcus" / "lesson_plan" / "gagne_diagnostician.py"


def test_gagne_diagnostician_does_not_import_emit_fit_report() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8")
    assert "from marcus.lesson_plan.fit_report import emit_fit_report" not in text
    assert " emit_fit_report," not in text
    assert " emit_fit_report\n" not in text, (
        "29-2 must construct and validate FitReport instances only; "
        "Marcus-Orchestrator remains the canonical emitter."
    )
