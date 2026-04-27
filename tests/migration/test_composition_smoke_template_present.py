from __future__ import annotations

from pathlib import Path


def test_composition_smoke_present_in_create_story_template() -> None:
    body = Path(".agents/skills/bmad-create-story/template.md").read_text(
        encoding="utf-8"
    )

    assert "## Composition Smoke" in body
    assert "PASS or FAIL as vote-evidence" in body
    assert "re-scope the slab" in body
    assert "defer until the missing substrate exists" in body
    assert "composition-shape vote with the substrate gap named" in body
