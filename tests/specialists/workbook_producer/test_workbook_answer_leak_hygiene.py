"""Wave 39/40 D2.7 — exercise prompts must never leak the corpus answer.

Live run ``8b275e5b`` rendered two workbook exercise prompts that carried the
quiz answer INLINE ahead of the Answer Key section (``… - **Correct Answer:**
25%``). ``answer_keys`` is the designated answer channel: ``_project_exercises``
must strip the unambiguously-labeled answer segment from the projected PROMPT
and route the answer text into ``answer_keys`` (never overwriting an existing
key; never losing the answer).

Party D3 rule 2 (live-shape fixtures only): every quiz component / annotation /
provisional-LO dict below is lifted VERBATIM from
``runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627/g0-enrichment.json``. The replay
probe additionally projects the FULL real card when the run dir is present.

OFFLINE ONLY: pure deterministic string processing over frozen shapes.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

import pytest

from app.marcus.lesson_plan.workbook_enrichment import (
    _project_exercises,
    _route_answer_key,
    _strip_answer_leak,
    project_enrichment_to_workbook_inputs,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_DIR = REPO_ROOT / "runs" / "8b275e5b-ed8a-4720-8217-8ddaca4c6627"

# Case-insensitive detector encoding the SAME closed-set policy as the
# stripper (a leak is a label the stripper would act on — NOT any prose
# mention): the emphasized "(Correct )Answer:" form anywhere; the plain form
# behind an inline dash/number marker (en/em dashes excluded mid-line — prose
# punctuation); the plain form behind a line-anchored marker (dashes, unicode
# bullets, numbers, blockquote); or the bare plain "correct answer:" at line
# start. Bare mid-prose "correct answer:" mentions (e.g. "Which option is the
# correct answer: A, B, or C?") are ACCEPTED-KEPT and must NOT be flagged.
_DET_EMPH = r"(?:\*{1,3}|_{1,3})"
_DET_LABEL_EMPH = (
    rf"{_DET_EMPH}\s*(?:correct\s+)?answer\s*(?:[:：]\s*{_DET_EMPH}|{_DET_EMPH}\s*[:：])"
)
ANSWER_LABEL_RE = re.compile(
    rf"(?:{_DET_LABEL_EMPH}"
    rf"|(?:^|(?<=\s)|(?<=[?.!,;)]))(?:[-*+]|\d+[.)]|>)\s*(?:correct\s+)?answer\s*[:：]"
    rf"|^\s*(?:[–—•‣▪·])\s*(?:correct\s+)?answer\s*[:：]"
    rf"|^\s*correct\s+answer\s*[:：])",
    re.IGNORECASE | re.MULTILINE,
)

# ---------------------------------------------------------------------------
# Live-shape fixtures — lifted VERBATIM from runs/8b275e5b…/g0-enrichment.json
# ---------------------------------------------------------------------------

# The two components whose excerpts leaked their answers in the live workbook.
LEAKED_QUIZ_C002 = {
    "component_id": "src-001-c002",
    "parent_source_id": "src-001",
    "source_type": "quiz",
    "other_type": None,
    "label": "Q2 Healthcare Economics",
    "locator": "Chapter 2 Knowledge Check > Q2",
    "excerpt": (
        "- **Prompt:** Approximately what percentage of total U.S. healthcare "
        "spending is attributed to administrative costs and waste? "
        "- **Correct Answer:** 25%"
    ),
    "flagged_unconsumed": True,
    "flagged_ungrounded": False,
    "kind": None,
}
LEAKED_QUIZ_C001_SRC002 = {
    "component_id": "src-002-c001",
    "parent_source_id": "src-002",
    "source_type": "quiz",
    "other_type": None,
    "label": "Q1 Knowledge Explosion",
    "locator": "Chapter 3 Knowledge Check > Q1",
    "excerpt": (
        "- **Prompt:** In 1950, medical knowledge doubled every 50 years. "
        "What is the currently projected doubling time? "
        "- **Correct Answer:** 73 days."
    ),
    "flagged_unconsumed": True,
    "flagged_ungrounded": False,
    "kind": None,
}
# A clean component (no answer line) — the byte-identical passthrough control.
CLEAN_QUIZ_C001 = {
    "component_id": "src-001-c001",
    "parent_source_id": "src-001",
    "source_type": "quiz",
    "other_type": None,
    "label": "Q1 Structural Shifts",
    "locator": "Chapter 2 Knowledge Check > Q1",
    "excerpt": (
        "- **Prompt:** Between 2012 and 2022, which major structural shift "
        "occurred regarding physician practice models?"
    ),
    "flagged_unconsumed": True,
    "flagged_ungrounded": False,
    "kind": None,
}

ANNOTATIONS = [
    {
        "component_id": "src-001-c001",
        "lo_refs": ["lo-g0-001"],
        "bloom": "remember",
        "pedagogical_role": "assessment",
        "teaches_after": [],
        "prerequisite_concepts": [
            "US physician employment models",
            "health system consolidation",
        ],
        "assessment_link": None,
        "teachable": True,
        "rationale": (
            "Checks recall of the 2012–2022 shift toward physician employment "
            "in large systems. Recall-level knowledge check aligns with remember "
            "and assesses LO on identifying the structural shift."
        ),
        "transform_model": "marcus",
        "transform_version": "ped-v1",
        "generated_at": "2026-07-15T15:21:57.561995Z",
    },
    {
        "component_id": "src-001-c002",
        "lo_refs": ["lo-g0-005"],
        "bloom": "understand",
        "pedagogical_role": "assessment",
        "teaches_after": ["src-001-c001"],
        "prerequisite_concepts": [
            "healthcare spending figures",
            "employment shift context",
        ],
        "assessment_link": None,
        "teachable": True,
        "rationale": (
            "Assesses understanding of 2024 $5.2T spend and employment shift. "
            "Explaining relationships fits understand; quiz format is assessment "
            "aligned to LO."
        ),
        "transform_model": "marcus",
        "transform_version": "ped-v1",
        "generated_at": "2026-07-15T15:21:57.561995Z",
    },
    {
        "component_id": "src-002-c001",
        "lo_refs": ["lo-g0-008"],
        "bloom": "understand",
        "pedagogical_role": "assessment",
        "teaches_after": [
            "src-001-c001",
            "src-001-c002",
            "src-001-c003",
            "src-001-c004",
            "src-001-c005",
        ],
        "prerequisite_concepts": [
            "Digital Front Door definition",
            "AI triage capability",
        ],
        "assessment_link": None,
        "teachable": True,
        "rationale": (
            "Evaluates understanding of a true Digital Front Door and AI-driven "
            "triage as a key enabler. Concept comprehension matches understand; "
            "quiz is assessment."
        ),
        "transform_model": "marcus",
        "transform_version": "ped-v1",
        "generated_at": "2026-07-15T15:21:57.561995Z",
    },
]

PROVISIONAL_LOS = [
    {
        "objective_id": "lo-g0-001",
        "statement": (
            "Identify the major 2012–2022 structural shift: a decrease in "
            "independent private practice and a surge in physicians employed by "
            "large health systems."
        ),
        "status": "provisional",
        "confidence": "high",
        "bloom_level": None,
        "source_refs": [
            {
                "source_id": "src-001",
                "locator": "Chapter 2 Knowledge Check > Q1",
                "quoted_span": (
                    "A drastic decrease in independent private practice and a "
                    "surge in physicians employed by large health systems."
                ),
            }
        ],
        "adequacy": None,
        "origin": "g0",
        "recommendation": "keep",
    },
    {
        "objective_id": "lo-g0-005",
        "statement": (
            "Explain that U.S. healthcare spending reached $5.2 trillion in 2024 "
            "and that physician employment shifted toward large health systems."
        ),
        "status": "provisional",
        "confidence": "high",
        "bloom_level": None,
        "source_refs": [
            {
                "source_id": "src-006",
                "locator": "Slide 1",
                "quoted_span": "reaching $5.2 trillion in 2024.",
            }
        ],
        "adequacy": None,
        "origin": "g0",
        "recommendation": "keep",
    },
    {
        "objective_id": "lo-g0-008",
        "statement": (
            "Define a true Digital Front Door and cite AI-driven triage as a key "
            "capability enabling a frictionless patient journey."
        ),
        "status": "provisional",
        "confidence": "high",
        "bloom_level": None,
        "source_refs": [
            {
                "source_id": "src-009",
                "locator": "Slide 4",
                "quoted_span": "infrastructure like the 'Digital Front Door.'",
            }
        ],
        "adequacy": None,
        "origin": "g0",
        "recommendation": "keep",
    },
]


def _card(typed_components: list[dict[str, Any]]) -> dict[str, Any]:
    """A minimal card payload over the live shapes (projection-reachable)."""
    return {
        "typed_components": typed_components,
        "provisional_los": PROVISIONAL_LOS,
        "citation_resolutions": [],
        "pedagogy_annotations": ANNOTATIONS,
    }


def _all_exercises(projection: Any) -> list[Any]:
    return [ex for sec in projection.spec.sections for ex in sec.exercises]


# ---------------------------------------------------------------------------
# (a) no-answer-in-prompt pin over the REAL leaked component shapes
# ---------------------------------------------------------------------------


def test_leaked_answer_stripped_from_prompt_and_routed_to_answer_keys() -> None:
    projection = project_enrichment_to_workbook_inputs(
        _card([LEAKED_QUIZ_C002, LEAKED_QUIZ_C001_SRC002])
    )
    exercises = {ex.exercise_id: ex for ex in _all_exercises(projection)}
    assert set(exercises) == {"src-001-c002", "src-002-c001"}

    # The prompt keeps the question and drops the labeled answer segment.
    for ex in exercises.values():
        assert not ANSWER_LABEL_RE.search(ex.prompt_intent), ex.prompt_intent
    assert "administrative costs and waste?" in exercises["src-001-c002"].prompt_intent
    assert "25%" not in exercises["src-001-c002"].prompt_intent
    assert "73 days" not in exercises["src-002-c001"].prompt_intent

    # The stripped answers land VERBATIM-leading in the answer_keys channel.
    assert projection.answer_keys["src-001-c002"].startswith("25%")
    assert projection.answer_keys["src-002-c001"].startswith("73 days.")


# ---------------------------------------------------------------------------
# (b) answer routing — lands when absent; existing key NEVER overwritten
# ---------------------------------------------------------------------------


def test_route_answer_key_fills_empty_slot_only() -> None:
    keys: dict[str, str] = {}
    _route_answer_key(keys, "src-001-c002", "25%")
    assert keys == {"src-001-c002": "25%"}


def test_route_answer_key_never_overwrites_existing_key() -> None:
    keys = {"src-001-c002": "PRE-EXISTING WORKED ANSWER"}
    _route_answer_key(keys, "src-001-c002", "25%")
    assert keys == {"src-001-c002": "PRE-EXISTING WORKED ANSWER"}


def test_projection_answer_key_present_for_clean_prompt_too() -> None:
    """A clean quiz (nothing stripped) still gets the grounding-note key."""
    projection = project_enrichment_to_workbook_inputs(_card([CLEAN_QUIZ_C001]))
    worked = projection.answer_keys["src-001-c001"]
    assert "source_ref `lo-g0-001`" in worked
    assert "25%" not in worked


# ---------------------------------------------------------------------------
# (c) prompts WITHOUT answer lines pass through byte-identical
# ---------------------------------------------------------------------------


def test_clean_prompt_passes_through_byte_identical() -> None:
    projection = project_enrichment_to_workbook_inputs(_card([CLEAN_QUIZ_C001]))
    (exercise,) = _all_exercises(projection)
    assert exercise.prompt_intent == CLEAN_QUIZ_C001["excerpt"]


@pytest.mark.parametrize(
    "prompt",
    [
        # Prose mentioning the words without the label-colon form.
        "Discuss why the correct answer depends on the clinical context.",
        # A question ABOUT a correct answer (bare mid-sentence colon is
        # ambiguous prose, not the labeled form).
        "Which option is the correct answer: A, B, or C?",
        # TRAILING label with NO answer text and no following line — ambiguous;
        # never strip a label while orphaning the answer elsewhere.
        "- **Prompt:** What is the doubling time?\n- **Correct Answer:**",
        # Emphasis that is not the answer label.
        "The *primary* driver of burnout is administrative burden.",
        # P5: mid-line en/em dash reads as prose punctuation, not a marker.
        "Burnout is high — correct answer: varies by state.",
        "Burnout is high – correct answer: varies by state.",
        # P4d: the bare un-marked, un-emphasized "Answer:" synonym stays put.
        "Answer: 25%",
        "The team should answer: does the model generalize?",
        # P7: a blank-marker "answer" is a fill-in-the-blank PROMPT, not a leak.
        "- **Correct Answer:** ____ (fill in the blank)",
        "- **Correct Answer:** _____",
    ],
)
def test_ambiguous_near_miss_lines_are_not_stripped(prompt: str) -> None:
    cleaned, answer = _strip_answer_leak(prompt)
    assert cleaned == prompt  # byte-identical
    assert answer is None


@pytest.mark.parametrize(
    ("prompt", "expected_clean", "expected_answer"),
    [
        # The live 8b275e5b inline leak shape.
        (
            "- **Prompt:** What is the doubling time? - **Correct Answer:** 73 days.",
            "- **Prompt:** What is the doubling time?",
            "73 days.",
        ),
        # Full answer LINE forms: plain / bold / list-markered.
        ("Correct Answer: 25%", "", "25%"),
        ("**Correct Answer:** 25%", "", "25%"),
        ("- **Correct Answer:** 25%", "", "25%"),
        (
            "What percentage is attributed to waste?\n- **Correct Answer:** 25%",
            "What percentage is attributed to waste?",
            "25%",
        ),
        # Colon outside the emphasis wrapper.
        ("**Correct Answer**: 25%", "", "25%"),
        # Case-insensitive.
        ("- correct answer: 25%", "", "25%"),
        # P4a: glued list marker (no whitespace after the dash).
        ("-**Correct Answer:** 25%", "", "25%"),
        # P4b: unicode bullets are line-anchored markers.
        ("• **Correct Answer:** 25%", "", "25%"),
        ("‣ correct answer: 25%", "", "25%"),
        # P4c: bold-italic (triple) emphasis.
        ("***Correct Answer:*** 25%", "", "25%"),
        # P4d: the "Answer" synonym — emphasized form.
        ("**Answer:** 25%", "", "25%"),
        # P4d: the "Answer" synonym — line-anchored dash-marked plain form.
        ("- Answer: 25%", "", "25%"),
        # P4e: fullwidth colon, emphasized and bare-plain forms.
        ("**Correct Answer：** 25%", "", "25%"),
        ("Correct Answer： 25%", "", "25%"),
        # P6: inline label glued directly after sentence punctuation.
        (
            "What time?**Correct Answer:** 25%",
            "What time?",
            "25%",
        ),
        # P1: a label line with an EMPTY answer group consumes the following
        # non-empty line as the answer (both removed from the prompt).
        (
            "- **Prompt:** What is the doubling time?\n- **Correct Answer:**\n73 days.",
            "- **Prompt:** What is the doubling time?",
            "73 days.",
        ),
        # P1: intervening blank lines are consumed with the answer block.
        (
            "What percentage is waste?\n- **Correct Answer:**\n\n25%",
            "What percentage is waste?",
            "25%",
        ),
        # P1 + P2 seam: an answer-only wrapped pair strips to the empty prompt
        # (the caller's fallback chain supplies the prompt).
        ("- **Correct Answer:**\n25%", "", "25%"),
        # P10: multiple stripped answers join with "; " (no embedded newlines).
        (
            "Name both figures.\n- **Correct Answer:** 25%\n- **Answer:** 73 days.",
            "Name both figures.",
            "25%; 73 days.",
        ),
    ],
)
def test_labeled_answer_forms_are_stripped(
    prompt: str, expected_clean: str, expected_answer: str
) -> None:
    cleaned, answer = _strip_answer_leak(prompt)
    assert cleaned == expected_clean
    assert answer == expected_answer
    assert answer is None or "\n" not in answer


# ---------------------------------------------------------------------------
# (d) P3 ambiguity guard — keep + warn; never destroy the question,
#     never lose an answer silently
# ---------------------------------------------------------------------------


def test_answer_first_ordering_is_kept_with_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Answer-BEFORE-prompt ordering must not destroy the question."""
    prompt = "- **Correct Answer:** 25% - **Prompt:** Which structural shift occurred?"
    with caplog.at_level(logging.WARNING):
        cleaned, answer = _strip_answer_leak(prompt)
    assert cleaned == prompt  # byte-identical — the question survives
    assert answer is None
    assert "ambiguous" in caplog.text


def test_overlong_midline_capture_is_kept_with_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A >120-char capture smells like a truncated prompt — keep + warn."""
    tail = ("weighing administrative burden against clinical outcomes " * 3).strip()
    assert len(tail) > 120
    prompt = f"Summarize the drivers of burnout. **Correct Answer:** {tail}"
    with caplog.at_level(logging.WARNING):
        cleaned, answer = _strip_answer_leak(prompt)
    assert cleaned == prompt  # byte-identical
    assert answer is None
    assert "ambiguous" in caplog.text


def test_clean_short_answer_still_strips_even_when_prompt_empties() -> None:
    """The P3 guard only bites on ambiguous shapes — a clean empty-prompt
    strip (no second label token, short answer) proceeds."""
    cleaned, answer = _strip_answer_leak("- **Correct Answer:** 25%")
    assert cleaned == ""
    assert answer == "25%"


def test_project_exercises_never_emits_empty_prompt() -> None:
    """An excerpt that is ONLY an answer line falls back to the label."""
    comp = dict(LEAKED_QUIZ_C002, excerpt="- **Correct Answer:** 25%")
    by_section, answer_keys = _project_exercises(
        [comp],
        {a["component_id"]: a for a in ANNOTATIONS},
        ["lo-g0-005"],
    )
    (exercise,) = [ex for exs in by_section.values() for ex in exs]
    assert exercise.prompt_intent == "Q2 Healthcare Economics"
    assert answer_keys["src-001-c002"].startswith("25%")


# ---------------------------------------------------------------------------
# (e) P2 — the empty-prompt fallback re-strips the label (no verbatim re-leak)
# ---------------------------------------------------------------------------


def test_empty_prompt_fallback_restrips_answer_bearing_label() -> None:
    """A label like "Correct Answer: 25%" must not re-leak verbatim as the
    fallback prompt; it re-strips, then cid takes over."""
    comp = dict(
        LEAKED_QUIZ_C002,
        excerpt="- **Correct Answer:** 25%",
        label="Correct Answer: 25%",
    )
    by_section, answer_keys = _project_exercises(
        [comp],
        {a["component_id"]: a for a in ANNOTATIONS},
        ["lo-g0-005"],
    )
    (exercise,) = [ex for exs in by_section.values() for ex in exs]
    assert exercise.prompt_intent == "src-001-c002"
    assert not ANSWER_LABEL_RE.search(exercise.prompt_intent)
    # Identical excerpt- and label-borne answers dedupe into one routed key.
    assert answer_keys["src-001-c002"].startswith("25% (source-provided")


def test_empty_prompt_fallback_routes_label_only_answer() -> None:
    """The answer-only-label shape: no excerpt, the LABEL carries the leak."""
    comp = dict(LEAKED_QUIZ_C002, excerpt="", label="Correct Answer: 25%")
    by_section, answer_keys = _project_exercises(
        [comp],
        {a["component_id"]: a for a in ANNOTATIONS},
        ["lo-g0-005"],
    )
    (exercise,) = [ex for exs in by_section.values() for ex in exs]
    assert exercise.prompt_intent == "src-001-c002"
    assert answer_keys["src-001-c002"].startswith("25%")


def test_empty_prompt_fallback_cid_leg_when_label_is_empty() -> None:
    """Empty label + answer-only excerpt -> the cid leg of the fallback chain.

    The LITERAL leg ("(exercise prompt unavailable)") stays in the production
    chain as the defensive last resort, but it is not black-box reachable:
    the :class:`Exercise` model rejects an empty ``exercise_id`` at
    construction, so an empty-cid component can never project an exercise.
    """
    comp = dict(LEAKED_QUIZ_C002, label="", excerpt="- **Correct Answer:** 25%")
    by_section, answer_keys = _project_exercises(
        [comp],
        {a["component_id"]: a for a in ANNOTATIONS},
        ["lo-g0-005"],
    )
    (exercise,) = [ex for exs in by_section.values() for ex in exs]
    assert exercise.prompt_intent == "src-001-c002"
    assert answer_keys["src-001-c002"].startswith("25%")


# ---------------------------------------------------------------------------
# (f) P8/P9/P10 — routing observability, truthiness gate, multi-answer join
# ---------------------------------------------------------------------------


def test_route_answer_key_fills_empty_string_slot() -> None:
    """P9: an empty-string slot counts as empty (truthiness, not membership)."""
    keys = {"src-001-c002": ""}
    _route_answer_key(keys, "src-001-c002", "25%")
    assert keys == {"src-001-c002": "25%"}


def test_duplicate_component_id_leak_warns_when_slot_claimed(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """P8: a second leaked answer for the SAME component_id cannot land —
    warn (with the exercise id), never overwrite, never silent."""
    comp_a = dict(LEAKED_QUIZ_C002)
    comp_b = dict(
        LEAKED_QUIZ_C002,
        excerpt="- **Prompt:** A different question? - **Correct Answer:** 30%",
    )
    with caplog.at_level(logging.WARNING):
        _, answer_keys = _project_exercises(
            [comp_a, comp_b],
            {a["component_id"]: a for a in ANNOTATIONS},
            ["lo-g0-005"],
        )
    assert answer_keys["src-001-c002"].startswith("25%")  # first claim wins
    assert "could not be routed" in caplog.text
    assert "src-001-c002" in caplog.text


def test_zero_surfaced_los_leak_warns_unrendered_section(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """P8: with zero provisional LOs the answer routes to a section that will
    never render — warn, but still route (never lose the answer)."""
    with caplog.at_level(logging.WARNING):
        _, answer_keys = _project_exercises(
            [dict(LEAKED_QUIZ_C002)],
            {a["component_id"]: a for a in ANNOTATIONS},
            [],
        )
    assert answer_keys["src-001-c002"].startswith("25%")
    assert "unrendered" in caplog.text


def test_multi_answer_key_gets_single_grounding_suffix() -> None:
    """P10: joined answers carry the grounding suffix exactly once."""
    comp = dict(
        LEAKED_QUIZ_C002,
        excerpt=(
            "Name both figures.\n"
            "- **Correct Answer:** 25%\n"
            "- **Answer:** 73 days."
        ),
    )
    _, answer_keys = _project_exercises(
        [comp],
        {a["component_id"]: a for a in ANNOTATIONS},
        ["lo-g0-005"],
    )
    worked = answer_keys["src-001-c002"]
    assert worked.startswith("25%; 73 days. (source-provided")
    assert worked.count("(source-provided correct answer;") == 1
    assert "\n" not in worked


# ---------------------------------------------------------------------------
# (3) real-run replay probe — the FULL 8b275e5b card projects zero leaks
# ---------------------------------------------------------------------------


def test_replay_full_8b275e5b_card_projects_zero_answer_leaks() -> None:
    card_path = RUN_DIR / "g0-enrichment.json"
    if not card_path.is_file():
        pytest.skip("run 8b275e5b artifacts unavailable")
    card = json.loads(card_path.read_text(encoding="utf-8"))

    projection = project_enrichment_to_workbook_inputs(card)
    exercises = _all_exercises(projection)
    assert exercises, "the real card must project at least one exercise"

    leaked = [
        ex.exercise_id for ex in exercises if ANSWER_LABEL_RE.search(ex.prompt_intent)
    ]
    assert leaked == [], f"answer label leaked into prompts: {leaked}"

    # The two live-observed answers are preserved in the Answer Key channel.
    assert projection.answer_keys["src-001-c002"].startswith("25%")
    assert projection.answer_keys["src-002-c001"].startswith("73 days.")
