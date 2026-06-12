"""MF3 — Pre-LLM byte-stability of `_assemble_pass_2_prompt` across 5 in-process iterations.

Murat MF3 binding (party-mode 2026-04-24): 5× in-process invocation of the
prompt assembler with byte-identical inputs MUST produce byte-identical
output. This catches non-deterministic ordering, datetime/UUID injection,
or randomized components. CRLF cross-platform variant lives in a sibling
test file.

dp-v1.1 (party consensus 2026-06-12): goldens deliberately regenerated —
the assembler now REQUIRES grounding kwargs (extracted_source + slide
roster) and leads with the corpus. The prior shape pinned the
confabulation-enabling prompt (cycle-4 sepsis narration).
"""

from __future__ import annotations

from app.specialists.irene.graph import _assemble_pass_2_prompt

GROUNDING = {
    "extracted_source": "# Source corpus\n\nMacro trends in healthcare.",
    "slide_roster": [
        {"slide_id": "slide-01", "visual_description": "Dual-axis chart"},
        {"slide_id": "slide-02", "visual_description": "Burnout infographic"},
    ],
}


def test_prompt_assembly_is_byte_identical_across_5_iterations() -> None:
    payload = {
        "lesson_slug": "c1m1-pres",
        "gary_slide_output": [{"slide_id": "s1", "slide_purpose": "intro"}],
        "perception_artifacts": [
            {"slide_id": "s1", "confidence": "HIGH", "elements": ["title", "diagram"]}
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
    # And no datetime/UUID/random-looking fragments leak into the prompt body.
    forbidden_substrings = (
        "uuid:",
        "UUID(",
        "random.",
        "<built-in",
    )
    for substr in forbidden_substrings:
        assert substr not in first_user, f"non-determinism vector: {substr!r}"


def test_prompt_assembly_dict_key_order_independent() -> None:
    """Two equivalent payloads with different key-insertion orders → same prompt."""
    payload_a = {"alpha": 1, "beta": 2, "gamma": 3}
    payload_b = {"gamma": 3, "alpha": 1, "beta": 2}
    _, user_a = _assemble_pass_2_prompt(payload_a, **GROUNDING)
    _, user_b = _assemble_pass_2_prompt(payload_b, **GROUNDING)
    assert user_a == user_b


def test_corpus_leads_and_references_are_demoted() -> None:
    """dp-v1.1 ordering pin: corpus section FIRST, real roster SECOND, the
    L5 references explicitly format-only — corpus-first cannot silently
    regress (the regression IS the cycle-4 defect)."""
    _, user = _assemble_pass_2_prompt({"alpha": 1}, **GROUNDING)
    corpus_at = user.index("## Source corpus (the ONLY content basis for narration)")
    roster_at = user.index("## Real slide roster (narrate THESE slides and no others)")
    references_at = user.index("## L5 references (fixed order — STRUCTURE AND FORMAT ONLY")
    task_at = user.index("## Task")
    assert corpus_at < roster_at < references_at < task_at
    assert "Macro trends in healthcare." in user
    assert "- slide-01: Dual-axis chart" in user
    assert "grounded EXCLUSIVELY in the source corpus" in user
