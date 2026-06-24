"""Pass-2 presenter-persona regression (lost-presenter-voice fix).

Irene's Pass-2 narration system prompt previously cast her as a "senior
Instructional Architect ... authoring Pass 2 narration scripts." Combined with
perception-grounding (which correctly feeds her each slide's contents), she
produced SLIDE-DESCRIPTION ("the fishbone diagram traces how ...", "the journey
diagram lays out the flow ...") instead of PRESENTER speech. This test pins the
recast persona: a senior instructor SPEAKING ALOUD to a live room, with the
slide visible behind her — and embeds a describer-tell tripwire so the
geometry-narration regression cannot silently return.

Scope: voice/persona only. The Pass-2 procedure logic, schemas, and
perception-grounding behavior are out of scope here.
"""

from __future__ import annotations

import re

from app.specialists.irene.graph import PASS_2_SYSTEM_MESSAGE

# --- Describer-tell tripwire ------------------------------------------------

# Banned constructions that signal Irene is describing the slide's geometry
# instead of speaking the idea to a room. Matched case-insensitively.
_DESCRIBER_TELL_PATTERNS: tuple[str, ...] = (
    r"\bthe (?:diagram|chart|timeline|figure|fishbone|graph|infographic|"
    r"journey|slide|image|visual)\b[^.]*\b(?:shows?|traces?|lays? out|"
    r"depicts?|presents?|illustrates?|displays?)\b",
    r"\bon the (?:left|right|top|bottom)\b",
    r"\bthis slide (?:shows?|presents?|depicts?|displays?)\b",
    r"\bas you can see\b",
)


def contains_describer_tells(text: str) -> bool:
    """Flag presenter text that has slipped into describing the slide itself.

    Returns True when the text contains a banned describer construction (the
    grammatical subject is a visual element, or it points at slide geometry,
    or it captions the picture). Returns False for clean presenter speech.
    """
    for pattern in _DESCRIBER_TELL_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def test_tripwire_flags_describer_line() -> None:
    assert contains_describer_tells("The diagram shows how waste compounds.")
    assert contains_describer_tells(
        "the fishbone diagram traces how administrative waste accumulates"
    )
    assert contains_describer_tells("On the left, you have the inputs.")
    assert contains_describer_tells("This slide presents three drivers.")
    assert contains_describer_tells("As you can see, the curve steepens.")


def test_tripwire_passes_presenter_line() -> None:
    assert not contains_describer_tells(
        "Notice how fast knowledge now doubles — seventy-three days."
    )
    assert not contains_describer_tells(
        "You've felt this: every extra approval step is a day a patient waits."
    )
    assert not contains_describer_tells(
        "Think about what doubling every seventy-three days does to a field."
    )


# --- Persona-prompt content pins -------------------------------------------


def test_system_prompt_casts_irene_as_live_room_presenter() -> None:
    prompt = PASS_2_SYSTEM_MESSAGE
    lowered = prompt.lower()
    # Presenter framing: speaking aloud to a live room with the slide behind her.
    assert "speaking" in lowered
    assert "live room" in lowered
    assert "behind you" in lowered


def test_system_prompt_embeds_banned_construction_rule() -> None:
    prompt = PASS_2_SYSTEM_MESSAGE
    lowered = prompt.lower()
    # The banned-construction voice rule must be present verbatim-enough that the
    # describer constructions are explicitly forbidden.
    assert "banned constructions" in lowered
    assert "shows / traces / lays out / depicts" in lowered
    assert "on the left/right/top/bottom" in lowered
    assert "as you can see" in lowered


def test_system_prompt_embeds_caption_self_test() -> None:
    prompt = PASS_2_SYSTEM_MESSAGE
    lowered = prompt.lower()
    # The caption self-test is the load-bearing instruction.
    assert "caption" in lowered
    assert "printed under the image" in lowered
    assert "the thing the picture exists to prove" in lowered


def test_system_prompt_keeps_grounding_for_accuracy() -> None:
    prompt = PASS_2_SYSTEM_MESSAGE
    lowered = prompt.lower()
    # Grounding stays — but reframed as accuracy, not content to report back.
    assert "accuracy" in lowered
    assert "do not report the slide back" in lowered
