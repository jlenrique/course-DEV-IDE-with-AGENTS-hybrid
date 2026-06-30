"""FORK C — project_ambiguous_narration_ordinals (the :335 0/>1 role-seed drop).

The narration role-seed matcher keeps EXACTLY-one-eligible per slide and silently
drops the >1 (ambiguous-collision) ordinals (``enrichment_consumption.py:336-340``).
This accessor surfaces those dropped ordinals so the coverage receipt can log the
narration surface as ``missing`` (AnchorResolution.narration_ambiguous) rather than
trust an ambiguous join. It SHARES the candidate-collection block with
``project_role_derived_voice_by_slide`` (one extracted helper — no duplication).
"""

from __future__ import annotations

from app.marcus.orchestrator.enrichment_consumption import (
    project_ambiguous_narration_ordinals,
    project_role_derived_voice_by_slide,
)


def _card(*components: dict) -> dict:
    annotations = [
        {"component_id": c["component_id"], "teachable": True, "pedagogical_role": "synthesis"}
        for c in components
    ]
    return {"typed_components": list(components), "pedagogy_annotations": annotations}


def _narr(component_id: str, slide_n: int) -> dict:
    return {
        "component_id": component_id,
        "source_type": "narration",
        "locator": f"Course 1 > Slide {slide_n}",
    }


def test_single_eligible_is_not_ambiguous() -> None:
    card = _card(_narr("c1", 1))
    assert project_ambiguous_narration_ordinals(card) == set()
    # and the role-seed projector keeps it (len == 1)
    assert "1" in project_role_derived_voice_by_slide(card)


def test_two_eligible_for_one_slide_is_ambiguous() -> None:
    card = _card(_narr("c1", 2), _narr("c2", 2))  # collision on Slide 2
    assert project_ambiguous_narration_ordinals(card) == {"2"}
    # the role-seed projector DROPS the collision (len > 1) — the two must agree
    assert "2" not in project_role_derived_voice_by_slide(card)


def test_empty_or_malformed_card() -> None:
    assert project_ambiguous_narration_ordinals(None) == set()
    assert project_ambiguous_narration_ordinals({}) == set()
    assert project_ambiguous_narration_ordinals({"typed_components": "x"}) == set()
