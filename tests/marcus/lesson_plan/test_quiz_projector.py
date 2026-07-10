"""Mine-next N3 — quiz projector (deck-companion-quiz) shape + render."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.quiz_enrichment import project_enrichment_to_quiz_inputs
from app.marcus.lesson_plan.quiz_producer import (
    QuizProducerError,
    render_quiz_markdown,
    write_quiz_artifact,
)
from app.marcus.lesson_plan.quiz_spec import QuizItem, QuizSpec

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_ENRICHMENT = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "coverage-reprove-covered-faithful-20260630T193322Z"
    / "g0-enrichment.json"
)


def test_quiz_kind_is_closed_deck_companion_quiz() -> None:
    spec = QuizSpec(
        items=(
            QuizItem(
                item_id="quiz-001",
                learning_objective_id="lo-001",
                prompt="Which action applies the bridge framing?",
                expected_answer_focus="apply",
            ),
        )
    )
    assert spec.kind == "deck-companion-quiz"
    with pytest.raises(ValidationError):
        QuizSpec.model_validate(
            {
                "kind": "deck-companion-workbook",
                "items": [
                    {
                        "item_id": "quiz-001",
                        "learning_objective_id": "lo-001",
                        "prompt": "x",
                        "expected_answer_focus": "y",
                    }
                ],
            }
        )


def test_project_enrichment_produces_nonempty_quiz_items() -> None:
    card = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    projection = project_enrichment_to_quiz_inputs(card)
    assert not projection.empty_source
    assert len(projection.spec.items) >= 1
    first = projection.spec.items[0]
    assert first.prompt.strip()
    assert first.expected_answer_focus.strip()
    assert first.learning_objective_id
    mutated = json.loads(json.dumps(card))
    for comp in mutated["typed_components"]:
        if comp.get("source_type") in {"quiz", "slide", "assignment_instructions"}:
            comp["label"] = "MUTATED-QUIZ-LABEL"
            comp["excerpt"] = "MUTATED-QUIZ-EXCERPT unique token plugh"
            break
    mutated_proj = project_enrichment_to_quiz_inputs(mutated)
    assert any(
        "plugh" in item.prompt or "MUTATED" in item.prompt
        for item in mutated_proj.spec.items
    )


def test_empty_source_warns_not_silent_success() -> None:
    projection = project_enrichment_to_quiz_inputs(
        {"typed_components": [], "provisional_los": []}
    )
    assert projection.empty_source
    assert projection.warnings
    assert projection.spec.items == ()
    with pytest.raises(QuizProducerError, match="empty quiz"):
        render_quiz_markdown(projection.spec)


def test_render_and_write_nonempty_markdown(tmp_path: Path) -> None:
    card = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    projection = project_enrichment_to_quiz_inputs(card)
    body = render_quiz_markdown(projection.spec)
    assert "deck-companion-quiz" in body
    assert "## " in body
    assert "Learning objective" in body
    assert "Expected answer focus" in body
    out = write_quiz_artifact(
        projection.spec, tmp_path / "artifacts" / "quizzes" / "quiz.md"
    )
    assert out.is_file()
    assert out.stat().st_size > 0
    assert "drill" not in body.lower()
