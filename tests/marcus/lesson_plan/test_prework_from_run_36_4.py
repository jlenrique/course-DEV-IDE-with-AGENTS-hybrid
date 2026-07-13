from pathlib import Path

from app.marcus.lesson_plan.prework_from_run import load_part2_scene_source

ROOT = Path("course-content/courses/tejal-apc-c1-m1-p2-trends")


def test_part2_adapter_selects_real_q5_and_payoff_files() -> None:
    source = load_part2_scene_source(ROOT)
    assert source.raw_candidates[0]["seed_id"] == "part2-q5"
    assert "recurring delay in patient transport" in source.raw_candidates[0]["text"]
    assert source.raw_candidates[0]["text"] == (
        "You are an attending physician managing a complex workflow. "
        "You notice a recurring delay in patient transport."
    )
    assert source.raw_candidates[0]["setup_only"] is True
    assert source.raw_candidates[0]["source_ref"].endswith("chapter-2-knowledge-check.md#Q5")
    assert source.forbidden_resolution_spans == (
        'According to the "Modern Clinician\'s Dilemma," what is the most likely '
        "barrier preventing you from solving this?",
        "The absence of a structured innovation process and the organizational "
        "authority/safety to redesign the workflow.",
    )
    assert source.raw_candidates[0]["forbidden_resolution_spans"] == (
        source.forbidden_resolution_spans
    )
    assert source.setup_span[0] < source.setup_span[1]
    assert all(start < end for start, end in source.forbidden_resolution_source_spans)
    assert source.payoff_slide_keys
    assert source.payoff_slide_keys == ("slides/slide-5-the-leadership-gap.md",)
    assert set(source.payoff_slide_keys) < set(source.payoff_slide_inventory)
    assert all((ROOT / path).is_file() for path in source.payoff_slide_keys)
    assert source.raw_candidates[0]["source_kind"] == "assessment_scenario"
    assert any(row["source_kind"] == "slide_body" for row in source.raw_candidates[1:])
