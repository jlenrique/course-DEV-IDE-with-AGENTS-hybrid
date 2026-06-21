"""MF3 - Pre-LLM byte-stability of `_assemble_pass_2_prompt`.

P2-3 deliberately repins this prompt-prefix fixture: Pass 2 now receives a
fixed perceived-authority seam before demoted expected visual plans while
preserving the canonical sorted JSON dump signature.
"""

from __future__ import annotations

from app.specialists.irene.graph import _assemble_pass_2_prompt

GROUNDING = {
    "extracted_source": "# Source corpus\n\nMacro trends in healthcare.",
    "slide_roster": [
        {
            "slide_id": "slide-01",
            "visual_description": "Dual-axis chart",
            "visual_authority": (
                "- slide-01: source=vision.perception_artifacts; "
                "coverage=perceived; confidence=HIGH\n"
                "  - perceived_extracted_text: $4.5T annual healthcare spend\n"
                "  - perceived_visual_element: {\"kind\":\"photo\",\"label\":\"building photo\"}"
            ),
            "expected_visual_plan": "gary_visual_description=$5.2T line+bars",
            "reading_path": "top_down",
            "reading_path_order": ["metric", "building"],
        },
        {
            "slide_id": "slide-02",
            "visual_description": "Burnout infographic",
            "visual_authority": (
                "- slide-02: source=vision.perception_artifacts; "
                "coverage=perceived; confidence=HIGH\n"
                "  - perceived_visual_element: "
                "{\"kind\":\"infographic\",\"label\":\"burnout infographic\"}"
            ),
            "expected_visual_plan": "gary_visual_description=Burnout infographic",
            "reading_path": "center_out",
            "reading_path_order": ["burnout"],
        },
    ],
}


def test_prompt_assembly_is_byte_identical_across_5_iterations() -> None:
    payload = {
        "lesson_slug": "c1m1-pres",
        "gary_slide_output": [{"slide_id": "s1", "slide_purpose": "intro"}],
        "perception_artifacts": [
            {
                "slide_id": "s1",
                "confidence": "HIGH",
                "coverage": "perceived",
                "visual_elements": [{"kind": "diagram", "label": "process diagram"}],
            }
        ],
        "narration_profile_controls": {
            "bridge_cadence_minutes": 2,
            "visual_references_per_slide": 2,
        },
    }
    outputs = [_assemble_pass_2_prompt(payload, **GROUNDING) for _ in range(5)]
    first_system, first_user = outputs[0]
    for system, user in outputs[1:]:
        assert system == first_system
        assert user == first_user
    forbidden_substrings = ("uuid:", "UUID(", "random.", "<built-in")
    for substr in forbidden_substrings:
        assert substr not in first_user, f"non-determinism vector: {substr!r}"


def test_prompt_assembly_dict_key_order_independent() -> None:
    payload_a = {"alpha": 1, "beta": 2, "gamma": 3}
    payload_b = {"gamma": 3, "alpha": 1, "beta": 2}
    _, user_a = _assemble_pass_2_prompt(payload_a, **GROUNDING)
    _, user_b = _assemble_pass_2_prompt(payload_b, **GROUNDING)
    assert user_a == user_b


def test_corpus_leads_perceived_authority_then_demoted_expected_plan() -> None:
    _, user = _assemble_pass_2_prompt({"alpha": 1}, **GROUNDING)
    corpus_at = user.index("## Source corpus (the ONLY content basis for narration)")
    authority_at = user.index(
        "## Visual authority - perceived slide evidence (SOLE visual authority)"
    )
    expected_at = user.index(
        "## Expected visual plan - brief/Gary signals "
        "(subordinate; may be stale; defer to perceived)"
    )
    cadence_at = user.index("## Reading path cadence guidance")
    references_at = user.index("## L5 references (fixed order")
    task_at = user.index("## Task")
    assert corpus_at < authority_at < expected_at < cadence_at < references_at < task_at
    assert "Macro trends in healthcare." in user
    assert "perceived_extracted_text: $4.5T annual healthcare spend" in user
    assert "gary_visual_description=$5.2T line+bars" in user
    assert "slide-01: reading_path=top_down" in user
    assert "perceived visual authority block" in user
