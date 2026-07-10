"""Mine 5 — drill spec shape + enrichment projection + markdown render."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.drill_enrichment import project_enrichment_to_drill_inputs
from app.marcus.lesson_plan.drill_producer import (
    DrillProducerError,
    render_drill_markdown,
    write_drill_artifact,
)
from app.marcus.lesson_plan.drill_spec import DrillPracticeItem, DrillSpec

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_ENRICHMENT = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "coverage-reprove-covered-faithful-20260630T193322Z"
    / "g0-enrichment.json"
)


def test_drill_kind_is_closed_deck_companion_drill() -> None:
    spec = DrillSpec(
        items=(
            DrillPracticeItem(
                item_id="drill-001",
                learning_objective_id="lo-001",
                prompt="What is the 70% figure?",
                expected_focus="remember",
            ),
        )
    )
    assert spec.kind == "deck-companion-drill"
    with pytest.raises(ValidationError):
        DrillSpec.model_validate(
            {
                "kind": "deck-companion-workbook",
                "items": [
                    {
                        "item_id": "drill-001",
                        "learning_objective_id": "lo-001",
                        "prompt": "x",
                        "expected_focus": "y",
                    }
                ],
            }
        )


def test_project_enrichment_produces_nonempty_items() -> None:
    card = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    projection = project_enrichment_to_drill_inputs(card)
    assert not projection.empty_source
    assert len(projection.spec.items) >= 1
    first = projection.spec.items[0]
    assert first.prompt.strip()
    assert first.expected_focus.strip()
    assert first.learning_objective_id
    # Honesty: mutate a component label → different prompt
    mutated = json.loads(json.dumps(card))
    for comp in mutated["typed_components"]:
        if comp.get("source_type") in {"slide", "quiz", "narration"}:
            comp["label"] = "MUTATED-LABEL-FOR-HONESTY"
            comp["excerpt"] = "MUTATED-EXCERPT-FOR-HONESTY unique token xyzzy"
            break
    mutated_proj = project_enrichment_to_drill_inputs(mutated)
    assert any(
        "xyzzy" in item.prompt or "MUTATED" in item.prompt
        for item in mutated_proj.spec.items
    )


def test_empty_source_warns_not_silent_success() -> None:
    projection = project_enrichment_to_drill_inputs({"typed_components": [], "provisional_los": []})
    assert projection.empty_source
    assert projection.warnings
    assert projection.spec.items == ()
    with pytest.raises(DrillProducerError, match="empty drill"):
        render_drill_markdown(projection.spec)


def test_render_and_write_nonempty_markdown(tmp_path: Path) -> None:
    card = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    projection = project_enrichment_to_drill_inputs(card)
    body = render_drill_markdown(projection.spec)
    assert "deck-companion-drill" in body
    assert "## " in body
    assert "Learning objective" in body
    out = write_drill_artifact(projection.spec, tmp_path / "artifacts" / "drills" / "drill.md")
    assert out.is_file()
    assert out.stat().st_size > 0
    assert "workbook" not in body.lower() or "Practice drill" in body
