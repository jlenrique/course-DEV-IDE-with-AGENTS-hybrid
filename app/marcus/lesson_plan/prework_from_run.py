"""Explicit-root adapters for the presentation-support pre-work authoring node."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.marcus.lesson_plan.prework_artifact import validate_source_child


class Part2SceneSource(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    raw_candidates: tuple[dict[str, object], ...]
    payoff_slide_inventory: tuple[str, ...]
    payoff_slide_keys: tuple[str, ...]
    forbidden_resolution_spans: tuple[str, ...]
    setup_span: tuple[int, int]
    forbidden_resolution_source_spans: tuple[tuple[int, int], ...]


_Q5 = re.compile(
    r"\*\*Q5:[^\n]*\*\*\s*\n"
    r"- \*\*Prompt:\*\*\s*(?P<prompt>[^\n]+)\s*\n"
    r"- \*\*Correct Answer:\*\*\s*(?P<answer>[^\n]+)",
    re.MULTILINE,
)


def load_part2_scene_source(course_source_root: Path) -> Part2SceneSource:
    root = Path(course_source_root).resolve(strict=True)
    assessment = validate_source_child(root, root / "assessments" / "chapter-2-knowledge-check.md")
    text = assessment.read_text(encoding="utf-8")
    match = _Q5.search(text)
    if match is None:
        raise ValueError("Part-2 Chapter-2 Q5 source anchor is unavailable")
    rel = assessment.relative_to(root).as_posix()
    ref = f"{rel}#Q5"
    prompt = match.group("prompt").strip()
    setup, separator, question_tail = prompt.partition(
        ' According to the "Modern Clinician\'s Dilemma,"'
    )
    if not separator or not setup.endswith(".") or not question_tail.strip():
        raise ValueError("Part-2 Q5 setup/forbidden-resolution boundary is unavailable")
    forbidden_question = (separator.strip() + " " + question_tail.strip()).strip()
    answer = match.group("answer").strip()
    setup_start = match.start("prompt")
    question_start = setup_start + len(setup) + 1
    slide_paths = tuple(
        validate_source_child(root, path)
        for path in sorted((root / "slides").glob("slide-*.md"))
        if path.is_file()
    )
    slides = tuple(path.relative_to(root).as_posix() for path in slide_paths)
    if not slides:
        raise ValueError("Part-2 payoff slide authority is unavailable")
    relevant = "slides/slide-5-the-leadership-gap.md"
    if relevant not in slides:
        raise ValueError("Part-2 relevant payoff slide is unavailable")
    fallback = tuple(
        {
            "seed_id": f"part2-slide-{index}",
            "text": path.read_text(encoding="utf-8"),
            "source_ref": f"{path.relative_to(root).as_posix()}#body",
            "source_kind": "slide_body",
            "slide_key": path.relative_to(root).as_posix(),
            "sme_scenario": False,
        }
        for index, path in enumerate(slide_paths, start=1)
    )
    return Part2SceneSource(
        raw_candidates=(
            {
                "seed_id": "part2-q5",
                "text": setup,
                "source_ref": ref,
                "source_kind": "assessment_scenario",
                "slide_key": None,
                "sme_scenario": True,
                "setup_only": True,
                "forbidden_resolution_spans": (forbidden_question, answer),
            },
            *fallback,
        ),
        payoff_slide_inventory=slides,
        payoff_slide_keys=(relevant,),
        forbidden_resolution_spans=(forbidden_question, answer),
        setup_span=(setup_start, setup_start + len(setup)),
        forbidden_resolution_source_spans=(
            (question_start, match.end("prompt")),
            (match.start("answer"), match.end("answer")),
        ),
    )


__all__ = ["Part2SceneSource", "load_part2_scene_source"]
