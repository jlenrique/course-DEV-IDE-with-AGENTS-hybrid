"""Story 37.4 closing-reflection contract and anti-forgery tests."""

from __future__ import annotations

import ast
import asyncio
import gc
import inspect
import json
import logging
import threading
import warnings
import weakref
from pathlib import Path
from types import MethodType

import pytest
from markdown_it import MarkdownIt
from pydantic import BaseModel, ValidationError

from app.marcus.lesson_plan.prework_projection import (
    FRICTION_SCALE,
    PreWorkBrief,
    PreWorkProvenance,
    PromiseProjection,
    PromiseVow,
    SceneBrief,
)
from app.marcus.lesson_plan.promise_projection import PromiseGateReceipt, PromiseProjectionResult
from app.marcus.lesson_plan.reflection_projection import (
    CALLBACK_CLAUSE,
    CAPABILITY_CLAUSE,
    MOVE_CLAUSE,
    NO_CANDIDATE_DIGEST,
    NO_PREWORK_DIGEST,
    REFLECTION_DEGRADED_MARKER,
    REFLECTION_UNAVAILABLE_MARKER,
    ReflectionAbilityCue,
    ReflectionAbilityFocus,
    ReflectionGateReceipt,
    ReflectionRequest,
    ReflectionResult,
    ReflectionWriterCandidate,
    ShiftedQuestionClauses,
    ShiftedQuestionPrompt,
    compose_closing_reflection,
    offline_closing_reflection_writer,
    prework_callback_digest,
    reflection_authority_digest,
    reflection_candidate_digest,
)

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "tests" / "fixtures" / "reflection_37_4"
MODULE = ROOT / "app" / "marcus" / "lesson_plan" / "reflection_projection.py"


def _promise(status: str = "authored", *, suffix: str = "") -> PromiseProjectionResult:
    if status == "authored":
        vows = (
            PromiseVow(objective_id="ability-a", text=f"Name the 3 recurring causes{suffix}"),
            PromiseVow(objective_id="ability-b", text="See the score pattern without re-rating it"),
        )
        return PromiseProjectionResult(
            projection=PromiseProjection(
                status="authored", vows=vows, known_losses=(), marker=None
            ),
            gate_receipt=PromiseGateReceipt(),
            authority_refs=("ratified#0", "ratified#1"),
        )
    loss = f"promise_{status}"
    return PromiseProjectionResult(
        projection=PromiseProjection(
            status=status,
            vows=(),
            known_losses=(loss,),
            marker="promise_semantics_not_authored",
        ),
        gate_receipt=PromiseGateReceipt(failures=(loss,)),
    )


def _prework(promise: PromiseProjectionResult | None = None) -> PreWorkBrief:
    promise = promise or _promise()
    scene = SceneBrief(
        status="authored",
        text="A grounded scene.",
        source_refs=("lesson:slide-2",),
        known_losses=(),
        marker=None,
    )
    return PreWorkBrief(
        scene=scene,
        friction_scale=FRICTION_SCALE,
        promise=promise.projection,
        provenance=PreWorkProvenance(source_refs=scene.source_refs, known_losses=()),
    )


def _request(*, status: str = "authored", prework: bool = True) -> ReflectionRequest:
    promise = _promise(status)
    return ReflectionRequest(
        lesson_ref="part-2",
        promise=promise,
        prework=_prework(promise) if prework else None,
    )


def _candidate(order: tuple[str, ...] = ("ability-a", "ability-b")) -> ReflectionWriterCandidate:
    lenses = {"ability-a": "name", "ability-b": "see"}
    return ReflectionWriterCandidate(
        status="authored",
        ability_focuses=tuple(
            ReflectionAbilityFocus(ability_ref=ref, capability_lens=lenses[ref]) for ref in order
        ),
        known_losses=(),
        marker=None,
    )


def test_red_module_and_closed_authored_composition() -> None:
    calls = 0

    def writer(request: ReflectionRequest) -> ReflectionWriterCandidate:
        nonlocal calls
        calls += 1
        assert request.promise.projection.vows[0].objective_id == "ability-a"
        return _candidate()

    result = compose_closing_reflection(_request(), writer)
    assert calls == 1
    assert result.status == "authored"
    assert result.prompt is not None
    assert tuple(cue.ability_ref for cue in result.prompt.ability_cues) == (
        "ability-a",
        "ability-b",
    )
    assert result.prompt.ability_cues[0].vow_text == "Name the 3 recurring causes"
    assert result.prompt.clauses.model_dump() == {
        "callback": CALLBACK_CLAUSE,
        "capability": CAPABILITY_CLAUSE,
        "move": MOVE_CLAUSE,
    }
    assert result.gate.status == "pass"
    assert result.known_losses == () and result.marker is None


@pytest.mark.parametrize("status", ["unavailable", "degraded"])
def test_non_authored_promise_pre_gates_with_zero_calls(status: str) -> None:
    calls = 0

    def writer(_: ReflectionRequest) -> ReflectionWriterCandidate:
        nonlocal calls
        calls += 1
        return _candidate()

    result = compose_closing_reflection(_request(status=status, prework=False), writer)
    assert calls == 0
    assert result.status == status
    assert result.candidate_snapshot is None
    assert result.prompt is None
    assert result.known_losses == (f"reflection_promise_authority_{status}",)


def test_absent_prework_is_unavailable_and_writer_is_not_called() -> None:
    result = compose_closing_reflection(_request(prework=False), lambda _: pytest.fail())
    assert result.status == "unavailable"
    assert result.known_losses == ("reflection_prework_callback_unavailable",)
    assert result.marker == REFLECTION_UNAVAILABLE_MARKER
    assert result.candidate_snapshot is None


def test_prework_promise_mismatch_pre_gates_before_writer() -> None:
    request = ReflectionRequest(
        lesson_ref="part-2", promise=_promise(), prework=_prework(_promise(suffix=" changed"))
    )
    result = compose_closing_reflection(request, lambda _: pytest.fail())
    assert result.status == "degraded"
    assert result.known_losses == ("reflection_prework_callback_mismatch",)


def test_binding_must_be_complete_unique_and_in_promise_order() -> None:
    for order in (("ability-b", "ability-a"), ("ability-a",)):
        candidate = ReflectionWriterCandidate(
            status="authored",
            ability_focuses=tuple(
                ReflectionAbilityFocus(ability_ref=ref, capability_lens="do") for ref in order
            ),
            known_losses=(),
            marker=None,
        )
        result = compose_closing_reflection(_request(), lambda _, candidate=candidate: candidate)
        assert result.status == "degraded"
        assert result.prompt is None
        assert result.known_losses == ("reflection_ability_binding_failed",)
    with pytest.raises(ValidationError):
        ReflectionWriterCandidate(
            status="authored",
            ability_focuses=(
                ReflectionAbilityFocus(ability_ref="ability-a", capability_lens="name"),
                ReflectionAbilityFocus(ability_ref="ability-a", capability_lens="do"),
            ),
            known_losses=(),
            marker=None,
        )


def test_unknown_lens_and_arbitrary_writer_prose_are_rejected() -> None:
    raw = _candidate().model_dump(mode="python")
    raw["ability_focuses"][0]["capability_lens"] = "fix"
    with pytest.raises(ValidationError):
        ReflectionWriterCandidate.model_validate(raw, strict=True)
    raw = _candidate().model_dump(mode="python") | {"prompt": "Rate again"}
    with pytest.raises(ValidationError):
        ReflectionWriterCandidate.model_validate(raw, strict=True)


@pytest.mark.parametrize(
    "unsafe",
    [
        "<b>unsafe</b>",
        "# heading",
        "#heading",
        "- list",
        "• list",
        "> quote",
        "[link](https://x)",
        "![image](https://x)",
        "```code",
        " padded ",
        "a\nline",
    ],
)
def test_unsafe_authoritative_vow_display_fails_closed(unsafe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = unsafe
    with pytest.raises(ValidationError):
        promise = PromiseProjectionResult.model_validate(raw, strict=True)
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "unsafe",
    [
        "Read [the guide][guide-ref]",
        "Read [the guide][]",
        "Read [the guide]",
        "![diagram][diagram-ref]",
        "![diagram][]",
        "![diagram]",
        "[guide-ref]: https://example.invalid/guide",
    ],
)
def test_reference_style_markdown_link_and_image_injection_is_rejected(unsafe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = unsafe
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "unsafe",
    [
        "Read [x]",
        "Read [12]",
        "Read [Δ]",
        "Compare [A] and [B]",
        "Read [x][ref]",
        "Read [x][]",
        "Read [x](https://example.invalid)",
        "Read [outer [inner]](https://example.invalid)",
        r"Read [escaped\] closing](https://example.invalid)",
        r"Read [escaped\]]",
        "![x]",
        "![x][ref]",
        "![x][]",
        "![x](https://example.invalid)",
        "![outer [inner]][ref]",
        r"![escaped\] closing][ref]",
        "[référence]: https://example.invalid",
    ],
)
def test_every_bracketed_markdown_reference_form_fails_closed(unsafe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = unsafe
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "safe",
    [
        "Compare A and B before choosing",
        "Use item 12 in the ordinary sequence",
        "Explain Δ without adding markup",
        "Name a cause (then choose a move)",
        "Join words with an em dash — safely",
    ],
)
def test_ordinary_non_markup_text_remains_safe(safe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = safe
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    assert ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "unsafe",
    [
        "---",
        "----",
        "***",
        "*****",
        "___",
        "_____",
        "- - -",
        "* * *",
        "_ _ _",
        "-\t-\t-",
        "* \t*\t *",
        "_\t _ \t_",
        "- - - - -",
        "*\t*\t*\t*",
        "_ _ _ _",
    ],
)
def test_full_request_rejects_commonmark_thematic_breaks(unsafe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = unsafe
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "safe",
    [
        "**",
        "__",
        "cause---effect remains ordinary prose",
        "Use A_B as an ordinary identifier",
        "Multiply 2*3 before choosing",
        "The marker families are -, *, and _ in prose",
        "Mixed compact markers *-_ are not a thematic break",
    ],
)
def test_thematic_break_boundary_controls_remain_safe(safe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = safe
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    assert ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "unsafe",
    ["=", "==", "===", "=====", "-", "--", "---", "-----", " =", "== ", "  ===  "],
)
def test_full_request_rejects_commonmark_setext_underlines(unsafe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = unsafe
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "underline,heading", [("=", "h1"), ("===", "h1"), ("-", "h2"), ("---", "h2")]
)
def test_contextual_commonmark_repro_proves_setext_heading_activation(
    underline: str, heading: str
) -> None:
    rendered = MarkdownIt("commonmark").render(f"Adjacent ability cue\n{underline}\n")
    assert rendered == f"<{heading}>Adjacent ability cue</{heading}>\n"


def test_internal_space_equals_is_not_a_commonmark_setext_underline() -> None:
    value = "= = remains ordinary comparison prose"
    assert MarkdownIt("commonmark").render(f"Adjacent ability cue\n{value}\n").startswith("<p>")
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = value
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    assert ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "visually_blank",
    ["\u200c", "\u200d", "\u200c\u200d", "\u200d\u200c\u200d"],
)
def test_joiner_only_vow_text_is_rejected_as_visually_blank(visually_blank: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = visually_blank
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "visually_blank",
    [
        "\ufe0f",
        "\ufe0e",
        "\u034f",
        "\u180b",
        "\U000e0100",
        "\u0301",
        "\ufe0f\u034f\u180b",
        "\u200c\ufe0f\u200d",
        "\u034f\u200d\U000e0100\u200c",
    ],
)
def test_default_ignorable_and_combining_mark_only_vows_are_rejected(
    visually_blank: str,
) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = visually_blank
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "visible",
    [
        "A\ufe0f",
        "e\u0301",
        "数\u034f",
        "7\U000e0100",
        "→\ufe0f",
        "©\ufe0f",
        "?",
        "¿",
        "न\u200dम",
        "ن\u200dم",
        "한\u200c글",
    ],
)
def test_marks_selectors_and_joiners_are_valid_with_a_visible_base(visible: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = visible
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    request = ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)
    assert request.promise.projection.vows[0].text == visible


UNICODE_VISUAL_FILLERS = (
    "\u115f",
    "\u1160",
    "\u2800",
    "\u303f",
    "\u3164",
    "\uffa0",
    "\U00013441",
    "\U00013442",
    "\U0001da7f",
    "\U0001da80",
)


@pytest.mark.parametrize(
    "visually_blank",
    UNICODE_VISUAL_FILLERS
    + (
        "\u115f\u1160",
        "\u3164\uffa0\u2800",
        "\u303f\U00013441\U0001da7f",
        "\u200d\u115f\ufe0f\u2800\U00013442\U0001da80",
    ),
)
def test_unicode_filler_and_blank_symbol_only_vows_are_rejected(
    visually_blank: str,
) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = visually_blank
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "visible",
    tuple(f"A{filler}" for filler in UNICODE_VISUAL_FILLERS)
    + ("한\u115f글", "数\u3164", "→\u2800", "7\uffa0"),
)
def test_unicode_fillers_may_accompany_actual_visible_content(visible: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = visible
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    request = ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)
    assert request.promise.projection.vows[0].text == visible


@pytest.mark.parametrize(
    "visible",
    [
        "A\u303f",
        "A\U00013441B\U00013442C",
        "A\U0001da7fB\U0001da80C",
        "\u2420",
        "Use \u2420 to name a space",
        "\uac00",
        "\u6570",
        "\u0646",
        "A\u115e\u1161",
    ],
)
def test_semantic_blanks_need_visible_content_but_visible_neighbors_remain_valid(
    visible: str,
) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = visible
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    request = ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)
    assert request.promise.projection.vows[0].text == visible


BLACK_FLAG = "\U0001f3f4"
CANCEL_TAG = "\U000e007f"


def _tag_spec(text: str) -> str:
    return "".join(chr(0xE0000 + ord(character)) for character in text)


@pytest.mark.parametrize("subdivision", ["gbeng", "gbsct", "gbwls"])
def test_known_subdivision_flag_tag_sequences_are_structurally_valid(
    subdivision: str,
) -> None:
    flag = BLACK_FLAG + _tag_spec(subdivision) + CANCEL_TAG
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = f"Recognize {flag} as a subdivision flag"
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    request = ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)
    assert flag in request.promise.projection.vows[0].text


@pytest.mark.parametrize(
    "malformed",
    [
        _tag_spec("g"),
        CANCEL_TAG,
        _tag_spec("g") + CANCEL_TAG,
        BLACK_FLAG + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("gbeng"),
        BLACK_FLAG + _tag_spec("g") + "\u200d" + _tag_spec("b") + CANCEL_TAG,
        BLACK_FLAG + CANCEL_TAG + _tag_spec("g"),
        BLACK_FLAG + _tag_spec("g") + CANCEL_TAG + _tag_spec("b"),
        BLACK_FLAG + _tag_spec("g") + CANCEL_TAG + CANCEL_TAG,
        _tag_spec("g") + BLACK_FLAG + CANCEL_TAG,
        BLACK_FLAG + "\U000e0001" + CANCEL_TAG,
    ],
)
def test_isolated_malformed_unterminated_and_reordered_tag_sequences_fail(
    malformed: str,
) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = f"Visible base {malformed} remains malformed"
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


def test_valid_tag_sequence_boundary_allows_multiple_sequences_and_visible_text() -> None:
    england = BLACK_FLAG + _tag_spec("gbeng") + CANCEL_TAG
    wales = BLACK_FLAG + _tag_spec("gbwls") + CANCEL_TAG
    text = f"Compare {england} with {wales} without assuming glyph support"
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = text
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    request = ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)
    assert request.promise.projection.vows[0].text == text


@pytest.mark.parametrize(
    "payload",
    ["rateagain", "javascript", "a", "z", "0", "9", "gb1", "a0z9", "gbengx"],
)
def test_non_rgi_hidden_alphanumeric_subdivision_payloads_are_rejected(
    payload: str,
) -> None:
    flag = BLACK_FLAG + _tag_spec(payload) + CANCEL_TAG
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = f"Visible base {flag} hidden payload"
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "malformed",
    [
        BLACK_FLAG + _tag_spec(" ") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("!") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("-") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("A") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("Z") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("g b") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("g-b") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("gB") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("g") + "x" + _tag_spec("b") + CANCEL_TAG,
        BLACK_FLAG + _tag_spec("g") + CANCEL_TAG + _tag_spec("b") + CANCEL_TAG,
    ],
)
def test_subdivision_flag_rejects_non_alphanumeric_tag_payload_boundaries(
    malformed: str,
) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = f"Visible base {malformed} remains malformed"
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


COMMONMARK_TYPE_1_TAGS = ("script", "pre", "style", "textarea")
COMMONMARK_TYPE_6_TAGS = (
    "address",
    "article",
    "aside",
    "base",
    "basefont",
    "blockquote",
    "body",
    "caption",
    "center",
    "col",
    "colgroup",
    "dd",
    "details",
    "dialog",
    "dir",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "frame",
    "frameset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hgroup",
    "hr",
    "html",
    "iframe",
    "legend",
    "li",
    "link",
    "main",
    "menu",
    "menuitem",
    "nav",
    "noframes",
    "ol",
    "optgroup",
    "option",
    "p",
    "param",
    "search",
    "section",
    "summary",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "title",
    "tr",
    "track",
    "ul",
)


@pytest.mark.parametrize(
    "unsafe",
    tuple(f"<{tag}" for tag in COMMONMARK_TYPE_1_TAGS + COMMONMARK_TYPE_6_TAGS)
    + tuple(f"</{tag}" for tag in COMMONMARK_TYPE_6_TAGS)
    + ("<SCRIPT", "<DIV", "</TABLE", "<script type", "<div class", "</table data"),
)
def test_full_request_rejects_incomplete_commonmark_raw_block_openers(unsafe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = unsafe
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize("opener", ["<script", "<pre", "<style", "<textarea", "<div", "</div"])
def test_contextual_commonmark_repro_proves_incomplete_raw_block_activation(opener: str) -> None:
    rendered = MarkdownIt("commonmark").render(f"{opener}\nadjacent cue\n")
    assert rendered == f"{opener}\nadjacent cue\n"


@pytest.mark.parametrize(
    "safe",
    [
        "Compare 2 < 3 before choosing",
        "Use <custom as ordinary comparison prose",
        "Name scripture rather than <scripture",
        "Use prevention rather than <prevent",
        "Choose a division rather than <division",
        "Use textarea concepts without <textareax activation",
    ],
)
def test_incomplete_raw_block_safe_boundaries_remain_valid(safe: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = safe
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    assert ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize("joiner", ["\u200c", "\u200d"])
def test_safe_zwnj_and_zwj_are_permitted_in_vow_text(joiner: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = f"Join{joiner}this ability safely"
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    assert ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


@pytest.mark.parametrize(
    "unsafe_format",
    [
        "\u200e",
        "\u200f",
        "\u202a",
        "\u202b",
        "\u202c",
        "\u202d",
        "\u202e",
        "\u2066",
        "\u2067",
        "\u2068",
        "\u2069",
    ],
)
def test_bidi_formatting_is_still_rejected(unsafe_format: str) -> None:
    raw = _promise().model_dump(mode="python")
    raw["projection"]["vows"][0]["text"] = f"Unsafe{unsafe_format}direction"
    promise = PromiseProjectionResult.model_validate(raw, strict=True)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)


def test_changed_vow_text_changes_visible_cue_and_authority_digest() -> None:
    first = _request()
    changed_promise = _promise(suffix=" — précis")
    second = ReflectionRequest(
        lesson_ref="part-2", promise=changed_promise, prework=_prework(changed_promise)
    )
    first_result = compose_closing_reflection(first, lambda _: _candidate())
    second_result = compose_closing_reflection(second, lambda _: _candidate())
    assert first_result.prompt != second_result.prompt
    assert reflection_authority_digest(first) != reflection_authority_digest(second)


def test_lens_choice_changes_only_the_typed_visible_cue() -> None:
    first = compose_closing_reflection(_request(), lambda _: _candidate())
    changed = ReflectionWriterCandidate(
        status="authored",
        ability_focuses=(
            ReflectionAbilityFocus(ability_ref="ability-a", capability_lens="do"),
            ReflectionAbilityFocus(ability_ref="ability-b", capability_lens="see"),
        ),
        known_losses=(),
        marker=None,
    )
    second = compose_closing_reflection(_request(), lambda _: changed)
    assert first.prompt is not None and second.prompt is not None
    assert first.prompt.clauses == second.prompt.clauses
    assert first.prompt.ability_cues[0].capability_lens == "name"
    assert second.prompt.ability_cues[0].capability_lens == "do"


def test_standalone_shifted_question_rejects_duplicate_cue_refs() -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    assert result.prompt is not None
    raw = result.prompt.model_dump(mode="python")
    raw["ability_cues"][1]["ability_ref"] = "ability-a"
    with pytest.raises(ValidationError):
        ShiftedQuestionPrompt.model_validate(raw, strict=True)


def test_offline_stub_is_honestly_unavailable() -> None:
    candidate = offline_closing_reflection_writer(_request())
    assert candidate.status == "unavailable"
    result = compose_closing_reflection(_request(), offline_closing_reflection_writer)
    assert result.status == "unavailable"
    assert result.known_losses == ("reflection_writer_unavailable",)


def test_writer_exception_propagates_unchanged() -> None:
    sentinel = RuntimeError("writer failed")

    def writer(_: ReflectionRequest) -> ReflectionWriterCandidate:
        raise sentinel

    with pytest.raises(RuntimeError) as captured:
        compose_closing_reflection(_request(), writer)
    assert captured.value is sentinel


def test_eligible_noncallable_writer_degrades_without_an_invocation_attempt() -> None:
    class NonCallableWriter:
        def __init__(self) -> None:
            self.call_count = 0

    writer = NonCallableWriter()
    result = compose_closing_reflection(_request(), writer)  # type: ignore[arg-type]

    assert writer.call_count == 0
    assert result.status == "degraded"
    assert result.prompt is None
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert result.marker == REFLECTION_DEGRADED_MARKER
    assert result.candidate_snapshot == ReflectionWriterCandidate(
        status="degraded",
        ability_focuses=(),
        known_losses=("reflection_writer_contract_invalid",),
        marker=REFLECTION_DEGRADED_MARKER,
    )
    assert result.gate.failures == ("writer_contract_invalid",)


@pytest.mark.parametrize("writer", [object(), {"writer": "not callable"}, 42])
def test_plain_noncallable_writer_objects_share_the_contract_invalid_result(
    writer: object,
) -> None:
    result = compose_closing_reflection(_request(), writer)  # type: ignore[arg-type]
    assert result.status == "degraded"
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert result.gate.failures == ("writer_contract_invalid",)


def test_wrong_or_constructed_writer_return_degrades_to_contract_loss() -> None:
    wrong = compose_closing_reflection(_request(), lambda _: {"status": "authored"})  # type: ignore[arg-type]
    assert wrong.known_losses == ("reflection_writer_contract_invalid",)
    forged = ReflectionWriterCandidate.model_construct(
        status="authored", ability_focuses=(), known_losses=(), marker=None
    )
    result = compose_closing_reflection(_request(), lambda _: forged)
    assert result.known_losses == ("reflection_writer_contract_invalid",)


def test_constructed_candidate_nested_type_mismatch_degrades_without_warning() -> None:
    forged = ReflectionWriterCandidate.model_construct(
        status="authored",
        ability_focuses=("not-a-focus-model",),
        known_losses=(),
        marker=None,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("error", UserWarning)
        result = compose_closing_reflection(_request(), lambda _: forged)

    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert result.gate.failures == ("writer_contract_invalid",)
    assert not [warning for warning in caught if issubclass(warning.category, UserWarning)]


def test_schema_shaped_foreign_focus_cannot_be_coerced_into_authored_candidate() -> None:
    class ForeignFocus(BaseModel):
        ability_ref: str
        capability_lens: str

    forged = ReflectionWriterCandidate.model_construct(
        status="authored",
        ability_focuses=(
            ForeignFocus(ability_ref="ability-a", capability_lens="name"),
            ReflectionAbilityFocus(ability_ref="ability-b", capability_lens="see"),
        ),
        known_losses=(),
        marker=None,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("error", UserWarning)
        result = compose_closing_reflection(_request(), lambda _: forged)

    assert result.status == "degraded"
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert result.candidate_snapshot == ReflectionWriterCandidate(
        status="degraded",
        ability_focuses=(),
        known_losses=("reflection_writer_contract_invalid",),
        marker=REFLECTION_DEGRADED_MARKER,
    )
    assert not [warning for warning in caught if issubclass(warning.category, UserWarning)]


@pytest.mark.parametrize("foreign_field", ["cue", "clauses"])
def test_result_rejects_schema_shaped_foreign_prompt_children(
    foreign_field: str,
) -> None:
    class ForeignCue(BaseModel):
        ability_ref: str
        vow_text: str
        capability_lens: str

    class ForeignClauses(BaseModel):
        callback: str
        capability: str
        move: str

    result = compose_closing_reflection(_request(), lambda _: _candidate())
    prompt = result.prompt
    assert prompt is not None
    cues: tuple[object, ...] = prompt.ability_cues
    clauses: object = prompt.clauses
    if foreign_field == "cue":
        cue = prompt.ability_cues[0]
        cues = (
            ForeignCue(
                ability_ref=cue.ability_ref,
                vow_text=cue.vow_text,
                capability_lens=cue.capability_lens,
            ),
            *prompt.ability_cues[1:],
        )
    else:
        clauses = ForeignClauses(
            callback=prompt.clauses.callback,
            capability=prompt.clauses.capability,
            move=prompt.clauses.move,
        )
    forged_prompt = ShiftedQuestionPrompt.model_construct(ability_cues=cues, clauses=clauses)
    raw = result.model_dump(mode="python")
    raw["prompt"] = forged_prompt
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("error", UserWarning)
        with pytest.raises(ValidationError):
            ReflectionResult.model_validate(raw, strict=True)
    assert not [warning for warning in caught if issubclass(warning.category, UserWarning)]


@pytest.mark.parametrize("foreign_field", ["promise", "prework"])
def test_request_preflight_rejects_schema_shaped_foreign_authority_children(
    foreign_field: str,
) -> None:
    class ForeignPromise(BaseModel):
        projection: object
        gate_receipt: object
        authority_refs: tuple[str, ...]
        operator_warnings: tuple[str, ...]

    class ForeignPrework(BaseModel):
        scene: object
        friction_scale: object
        promise: object
        provenance: object
        beat_order: tuple[str, ...]

    promise = _promise()
    prework = _prework()
    request = ReflectionRequest.model_construct(
        lesson_ref="part-2",
        promise=(
            ForeignPromise(
                projection=promise.projection,
                gate_receipt=promise.gate_receipt,
                authority_refs=promise.authority_refs,
                operator_warnings=promise.operator_warnings,
            )
            if foreign_field == "promise"
            else promise
        ),
        prework=(
            ForeignPrework(
                scene=prework.scene,
                friction_scale=prework.friction_scale,
                promise=prework.promise,
                provenance=prework.provenance,
                beat_order=prework.beat_order,
            )
            if foreign_field == "prework"
            else prework
        ),
    )
    writer_calls = 0

    def writer(_: ReflectionRequest) -> ReflectionWriterCandidate:
        nonlocal writer_calls
        writer_calls += 1
        return _candidate()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("error", UserWarning)
        with pytest.raises((ValidationError, ValueError)):
            compose_closing_reflection(request, writer)
    assert writer_calls == 0
    assert not [warning for warning in caught if issubclass(warning.category, UserWarning)]


def test_writer_candidate_subclass_is_not_an_exact_protocol_return() -> None:
    class CandidateSubclass(ReflectionWriterCandidate):
        pass

    subclass = CandidateSubclass.model_validate(_candidate().model_dump(mode="python"))
    result = compose_closing_reflection(_request(), lambda _: subclass)
    assert result.status == "degraded"
    assert result.known_losses == ("reflection_writer_contract_invalid",)


def test_native_coroutine_writer_return_is_closed_before_contract_degradation() -> None:
    async def candidate_coroutine() -> ReflectionWriterCandidate:
        return _candidate()

    class CoroutineWriter:
        def __init__(self) -> None:
            self.call_count = 0

        def __call__(self, _: ReflectionRequest) -> object:
            self.call_count += 1
            return candidate_coroutine()

    writer = CoroutineWriter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = compose_closing_reflection(_request(), writer)  # type: ignore[arg-type]
        gc.collect()

    assert writer.call_count == 1
    assert result.status == "degraded"
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]


def test_non_native_awaitable_without_cleanup_degrades_as_wrong_return_type() -> None:
    class AwaitableOnly:
        def __await__(self):  # type: ignore[no-untyped-def]
            if False:
                yield None
            return _candidate()

    calls = 0

    def writer(_: ReflectionRequest) -> object:
        nonlocal calls
        calls += 1
        return AwaitableOnly()

    result = compose_closing_reflection(_request(), writer)  # type: ignore[arg-type]
    assert calls == 1
    assert result.known_losses == ("reflection_writer_contract_invalid",)


def test_recursive_request_and_result_revalidation_defeats_constructed_bypass() -> None:
    forged = ReflectionRequest.model_construct(
        lesson_ref=" ", promise=_promise(), prework=_prework()
    )
    with pytest.raises(ValidationError):
        compose_closing_reflection(forged, lambda _: _candidate())
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    raw = result.model_dump(mode="python")
    raw["prompt"]["clauses"]["move"] = "Rate the pain again."
    with pytest.raises(ValidationError):
        ReflectionResult.model_validate(raw, strict=True)


def test_result_rejects_hostile_gate_and_prompt_subclasses_before_equality() -> None:
    class EvilGate(ReflectionGateReceipt):
        def __eq__(self, other: object) -> bool:
            return True

        def __ne__(self, other: object) -> bool:
            return False

    class EvilPrompt(ShiftedQuestionPrompt):
        def __eq__(self, other: object) -> bool:
            return True

        def __ne__(self, other: object) -> bool:
            return False

    result = compose_closing_reflection(_request(), lambda _: _candidate())
    for field, hostile in (
        ("gate", EvilGate.model_validate(result.gate.model_dump(mode="python"))),
        ("prompt", EvilPrompt.model_validate(result.prompt.model_dump(mode="python"))),
    ):
        raw = result.model_dump(mode="python")
        raw[field] = hostile
        with pytest.raises(ValidationError):
            ReflectionResult.model_validate(raw, strict=True)


def test_result_rejects_hostile_authority_and_candidate_before_model_dump() -> None:
    class EvilAuthority(ReflectionRequest):
        def model_dump(self, *args: object, **kwargs: object) -> dict[str, object]:
            raise AssertionError("hostile authority model_dump must not run")

    class EvilCandidate(ReflectionWriterCandidate):
        def model_dump(self, *args: object, **kwargs: object) -> dict[str, object]:
            raise AssertionError("hostile candidate model_dump must not run")

    result = compose_closing_reflection(_request(), lambda _: _candidate())
    authority = EvilAuthority.model_validate(result.authority.model_dump(mode="python"))
    candidate = EvilCandidate.model_validate(result.candidate_snapshot.model_dump(mode="python"))
    for field, hostile in (("authority", authority), ("candidate_snapshot", candidate)):
        raw = result.model_dump(mode="python")
        raw[field] = hostile
        with pytest.raises(ValidationError):
            ReflectionResult.model_validate(raw, strict=True)

    with pytest.raises(TypeError):
        compose_closing_reflection(authority, lambda _: _candidate())


@pytest.mark.parametrize("field", ["authority", "candidate_snapshot", "gate", "prompt"])
def test_result_rejects_exact_base_constructed_nested_models_with_invalid_internals(
    field: str,
) -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    raw = result.model_dump(mode="python")
    if field == "authority":
        nested = ReflectionRequest.model_construct(
            lesson_ref=" ", promise=result.authority.promise, prework=result.authority.prework
        )
    elif field == "candidate_snapshot":
        nested = ReflectionWriterCandidate.model_construct(
            status="authored", ability_focuses=(), known_losses=(), marker=None
        )
    elif field == "gate":
        gate_raw = result.gate.model_dump(mode="python")
        gate_raw["authority_digest"] = "not-a-digest"
        nested = ReflectionGateReceipt.model_construct(**gate_raw)
    else:
        prompt_raw = result.prompt.model_dump(mode="python")
        prompt_raw["ability_cues"] = ()
        nested = ShiftedQuestionPrompt.model_construct(**prompt_raw)
    raw[field] = nested
    with pytest.raises(ValidationError):
        ReflectionResult.model_validate(raw, strict=True)


def test_result_valid_python_and_json_round_trips_preserve_exact_nested_types() -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    python_round_trip = ReflectionResult.model_validate(
        result.model_dump(mode="python"), strict=True
    )
    json_round_trip = ReflectionResult.model_validate_json(result.model_dump_json())
    for restored in (python_round_trip, json_round_trip):
        assert type(restored.authority) is ReflectionRequest
        assert type(restored.candidate_snapshot) is ReflectionWriterCandidate
        assert type(restored.gate) is ReflectionGateReceipt
        assert type(restored.prompt) is ShiftedQuestionPrompt
        assert restored == result


@pytest.mark.parametrize("field", ["authority", "candidate_snapshot", "gate", "prompt"])
def test_result_uses_trusted_dump_and_stores_normalized_nested_copies(field: str) -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    raw = result.model_dump(mode="python")
    nested = getattr(result, field)
    assert nested is not None
    calls = 0

    def hostile_dump(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal calls
        calls += 1
        raise AssertionError("instance serializer shadow must not run")

    object.__setattr__(nested, "model_dump", hostile_dump)
    raw[field] = nested
    restored = ReflectionResult.model_validate(raw, strict=True)
    normalized = getattr(restored, field)
    assert calls == 0
    assert normalized is not nested
    assert "model_dump" not in normalized.__dict__


def test_result_rejects_forged_exact_gate_despite_valid_serializer_shadow() -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    valid_gate_dump = result.gate.model_dump(mode="python")
    forged_dump = dict(valid_gate_dump)
    forged_dump["authority_digest"] = "forged"
    forged = ReflectionGateReceipt.model_construct(**forged_dump)
    calls = 0

    def spoof_dump(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return valid_gate_dump

    object.__setattr__(forged, "model_dump", spoof_dump)
    raw = result.model_dump(mode="python")
    raw["gate"] = forged
    with pytest.raises(ValidationError):
        ReflectionResult.model_validate(raw, strict=True)
    assert calls == 0


def test_request_rejects_forged_exact_promise_without_using_shadow_serializer() -> None:
    valid = _promise()
    forged = PromiseProjectionResult.model_construct(
        projection=valid.projection,
        gate_receipt=valid.gate_receipt,
        authority_refs=(),
    )
    calls = 0

    def spoof_dump(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return valid.model_dump(mode="python")

    object.__setattr__(forged, "model_dump", spoof_dump)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=forged, prework=None)
    assert calls == 0


def test_request_rejects_hostile_upstream_nested_subclass_without_hook_dispatch() -> None:
    serializer_calls = 0

    class EvilProjection(PromiseProjection):
        def model_dump(self, *args: object, **kwargs: object) -> dict[str, object]:
            nonlocal serializer_calls
            serializer_calls += 1
            return super().model_dump(*args, **kwargs)

    valid = _promise()
    projection = EvilProjection.model_validate(valid.projection.model_dump(mode="python"))
    promise = PromiseProjectionResult.model_construct(
        projection=projection,
        gate_receipt=valid.gate_receipt,
        authority_refs=valid.authority_refs,
    )
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)
    assert serializer_calls == 0


def test_request_rejects_owned_snapshot_subclasses_before_serializer_dispatch() -> None:
    class EvilPromise(PromiseProjectionResult):
        def model_dump(self, *args: object, **kwargs: object) -> dict[str, object]:
            raise AssertionError("promise serializer must not run")

    class EvilPrework(PreWorkBrief):
        def model_dump(self, *args: object, **kwargs: object) -> dict[str, object]:
            raise AssertionError("prework serializer must not run")

    promise = EvilPromise.model_validate(_promise().model_dump(mode="python"))
    prework = EvilPrework.model_validate(_prework().model_dump(mode="python"))
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None)
    with pytest.raises(ValidationError):
        ReflectionRequest(lesson_ref="part-2", promise=_promise(), prework=prework)


def test_candidate_and_prompt_reject_forged_children_despite_serializer_shadows() -> None:
    valid_focus = ReflectionAbilityFocus(ability_ref="ability-a", capability_lens="name")
    forged_focus = ReflectionAbilityFocus.model_construct(ability_ref=" ", capability_lens="name")
    focus_calls = 0

    def focus_spoof(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal focus_calls
        focus_calls += 1
        return valid_focus.model_dump(mode="python")

    object.__setattr__(forged_focus, "model_dump", focus_spoof)
    with pytest.raises(ValidationError):
        ReflectionWriterCandidate(
            status="authored", ability_focuses=(forged_focus,), known_losses=(), marker=None
        )
    assert focus_calls == 0

    valid_result = compose_closing_reflection(_request(), lambda _: _candidate())
    valid_cue = valid_result.prompt.ability_cues[0]
    forged_cue = ReflectionAbilityCue.model_construct(
        ability_ref=" ", vow_text=valid_cue.vow_text, capability_lens=valid_cue.capability_lens
    )
    cue_calls = 0

    def cue_spoof(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal cue_calls
        cue_calls += 1
        return valid_cue.model_dump(mode="python")

    object.__setattr__(forged_cue, "model_dump", cue_spoof)
    with pytest.raises(ValidationError):
        ShiftedQuestionPrompt(ability_cues=(forged_cue,))
    assert cue_calls == 0

    valid_clauses = valid_result.prompt.clauses
    forged_clauses = ShiftedQuestionClauses.model_construct(callback="forged")
    clause_calls = 0

    def clause_spoof(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal clause_calls
        clause_calls += 1
        return valid_clauses.model_dump(mode="python")

    object.__setattr__(forged_clauses, "model_dump", clause_spoof)
    with pytest.raises(ValidationError):
        ShiftedQuestionPrompt(ability_cues=(valid_cue,), clauses=forged_clauses)
    assert clause_calls == 0


def test_candidate_and_prompt_store_normalized_child_copies() -> None:
    focus = ReflectionAbilityFocus(ability_ref="ability-a", capability_lens="name")
    cue = ReflectionAbilityCue(
        ability_ref="ability-a", vow_text="Name the pattern", capability_lens="name"
    )
    clauses = ShiftedQuestionClauses()
    for child in (focus, cue, clauses):
        object.__setattr__(
            child,
            "model_dump",
            lambda *args, **kwargs: pytest.fail("instance serializer shadow executed"),
        )
    candidate = ReflectionWriterCandidate(
        status="authored", ability_focuses=(focus,), known_losses=(), marker=None
    )
    prompt = ShiftedQuestionPrompt(ability_cues=(cue,), clauses=clauses)
    assert candidate.ability_focuses[0] is not focus
    assert prompt.ability_cues[0] is not cue
    assert prompt.clauses is not clauses
    assert all("model_dump" not in child.__dict__ for child in candidate.ability_focuses)
    assert "model_dump" not in prompt.ability_cues[0].__dict__
    assert "model_dump" not in prompt.clauses.__dict__


@pytest.mark.asyncio
async def test_task_and_future_writer_returns_are_cancelled_before_degradation() -> None:
    loop = asyncio.get_running_loop()
    calls = 0

    async def pending() -> None:
        await asyncio.Event().wait()

    task = loop.create_task(pending())
    future = loop.create_future()
    for returned in (task, future):

        def writer(_: ReflectionRequest, value: object = returned) -> object:
            nonlocal calls
            calls += 1
            return value

        result = compose_closing_reflection(_request(), writer)  # type: ignore[arg-type]
        assert result.known_losses == ("reflection_writer_contract_invalid",)
        assert returned.cancelled() or returned.cancelling()
    await asyncio.gather(task, return_exceptions=True)
    assert task.cancelled() and future.cancelled()
    assert calls == 2


def test_generic_awaitable_cleanup_hook_is_not_executed() -> None:
    class HostileAwaitable:
        def __init__(self) -> None:
            self.close_calls = 0

        def __await__(self):  # type: ignore[no-untyped-def]
            if False:
                yield None
            return None

        def close(self) -> None:
            self.close_calls += 1
            raise AssertionError("arbitrary cleanup hook must not execute")

    returned = HostileAwaitable()
    result = compose_closing_reflection(_request(), lambda _: returned)  # type: ignore[arg-type]
    assert returned.close_calls == 0
    assert result.known_losses == ("reflection_writer_contract_invalid",)


@pytest.mark.parametrize("field", ["authority", "candidate_snapshot", "gate", "prompt"])
def test_expected_class_serializer_ignores_forged_instance_serializer_state(
    field: str,
) -> None:
    class SpoofSerializer:
        def __init__(self, clean: dict[str, object]) -> None:
            self.clean = clean
            self.calls = 0

        def to_python(self, *args: object, **kwargs: object) -> dict[str, object]:
            self.calls += 1
            return self.clean

    result = compose_closing_reflection(_request(), lambda _: _candidate())
    clean = getattr(result, field).model_dump(mode="python")
    if field == "authority":
        forged = ReflectionRequest.model_construct(
            lesson_ref=" ", promise=result.authority.promise, prework=result.authority.prework
        )
    elif field == "candidate_snapshot":
        forged = ReflectionWriterCandidate.model_construct(
            status="authored", ability_focuses=(), known_losses=(), marker=None
        )
    elif field == "gate":
        forged_dump = dict(clean)
        forged_dump["authority_digest"] = "forged"
        forged = ReflectionGateReceipt.model_construct(**forged_dump)
    else:
        forged = ShiftedQuestionPrompt.model_construct(
            ability_cues=(), clauses=result.prompt.clauses
        )
    serializer = SpoofSerializer(clean)
    object.__setattr__(forged, "__pydantic_serializer__", serializer)
    raw = result.model_dump(mode="python")
    raw[field] = forged
    with pytest.raises(ValidationError):
        ReflectionResult.model_validate(raw, strict=True)
    assert serializer.calls == 0


@pytest.mark.parametrize("field", ["authority", "candidate_snapshot", "gate", "prompt"])
def test_instance_serializer_shadow_is_stripped_from_returned_canonical_graph(
    field: str,
) -> None:
    class RaisingSerializer:
        calls = 0

        def to_python(self, *args: object, **kwargs: object) -> dict[str, object]:
            self.calls += 1
            raise AssertionError("instance Pydantic serializer must not run")

    result = compose_closing_reflection(_request(), lambda _: _candidate())
    raw = result.model_dump(mode="python")
    nested = getattr(result, field)
    serializer = RaisingSerializer()
    object.__setattr__(nested, "__pydantic_serializer__", serializer)
    raw[field] = nested
    restored = ReflectionResult.model_validate(raw, strict=True)
    normalized = getattr(restored, field)
    assert serializer.calls == 0
    assert normalized is not nested
    assert "__pydantic_serializer__" not in normalized.__dict__


def test_future_cancel_override_is_bypassed_by_trusted_unbound_cleanup() -> None:
    class EvilFuture(asyncio.Future[object]):
        cancel_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            raise AssertionError("Future.cancel override must not run")

    loop = asyncio.new_event_loop()
    future = EvilFuture(loop=loop)
    try:
        result = compose_closing_reflection(_request(), lambda _: future)  # type: ignore[arg-type]
        assert future.cancel_calls == 0
        assert future.cancelled()
        assert result.known_losses == ("reflection_writer_contract_invalid",)
    finally:
        if not future.done():
            asyncio.Future.cancel(future)
        loop.close()


@pytest.mark.asyncio
async def test_task_cancel_override_is_bypassed_without_pending_work() -> None:
    class EvilTask(asyncio.Task[None]):
        cancel_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            raise AssertionError("Task.cancel override must not run")

    loop = asyncio.get_running_loop()

    async def pending() -> None:
        await asyncio.Event().wait()

    task = EvilTask(pending(), loop=loop)
    result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
    assert task.cancel_calls == 0
    assert task.cancelling()
    await asyncio.gather(task, return_exceptions=True)
    assert task.cancelled()
    assert result.known_losses == ("reflection_writer_contract_invalid",)


def test_closed_loop_rejected_task_is_disposed_without_destruction_diagnostics(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class EvilTask(asyncio.Task[None]):
        cancel_calls = 0
        get_coro_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            raise AssertionError("Task.cancel override must not run")

        def get_coro(self):  # type: ignore[no-untyped-def]
            self.get_coro_calls += 1
            raise AssertionError("Task.get_coro override must not run")

    loop = asyncio.new_event_loop()

    async def pending() -> None:
        await asyncio.Event().wait()

    task = EvilTask(pending(), loop=loop)
    task_ref = weakref.ref(task)
    loop.close()

    def writer(_: ReflectionRequest, returned: object = task) -> object:
        return returned

    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), writer)  # type: ignore[arg-type]
        assert result.known_losses == ("reflection_writer_contract_invalid",)
        assert task.cancel_calls == 0
        assert task.get_coro_calls == 0
        del writer
        del task
        gc.collect()

    assert task_ref() is None
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [
        record
        for record in caplog.records
        if "Task was destroyed but it is pending" in record.message
    ]


def test_open_idle_loop_owns_cancellation_and_finalizes_on_later_turn(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class EvilTask(asyncio.Task[None]):
        cancel_calls = 0
        get_coro_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            raise AssertionError("Task.cancel override must not run")

        def get_coro(self):  # type: ignore[no-untyped-def]
            self.get_coro_calls += 1
            raise AssertionError("Task.get_coro override must not run")

    loop = asyncio.new_event_loop()
    body_runs = 0

    async def pending() -> None:
        nonlocal body_runs
        body_runs += 1
        await asyncio.Event().wait()

    task = EvilTask(pending(), loop=loop)
    task_ref = weakref.ref(task)

    def writer(_: ReflectionRequest, returned: object = task) -> object:
        return returned

    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), writer)  # type: ignore[arg-type]
        pre_turn_state = inspect.getcoroutinestate(asyncio.Task.get_coro(task))
        assert result.known_losses == ("reflection_writer_contract_invalid",)
        assert task.cancel_calls == 0
        assert task.get_coro_calls == 0
        outcomes = loop.run_until_complete(asyncio.gather(task, return_exceptions=True))
        assert task.cancelled()
        assert isinstance(outcomes[0], asyncio.CancelledError)
        assert body_runs == 0
        post_turn_state = inspect.getcoroutinestate(asyncio.Task.get_coro(task))
        del writer
        del task
        gc.collect()

    loop.close()
    assert pre_turn_state == inspect.CORO_CREATED
    assert post_turn_state == inspect.CORO_CLOSED
    assert task_ref() is None
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [
        record
        for record in caplog.records
        if any(
            marker in record.message
            for marker in (
                "Task was destroyed but it is pending",
                "Task exception was never retrieved",
                "InvalidStateError",
                "RuntimeError",
            )
        )
    ]


@pytest.mark.parametrize("raises", [True, False])
def test_future_waiter_cancel_override_is_bypassed_and_outer_task_cancels(
    raises: bool,
    caplog: pytest.LogCaptureFixture,
) -> None:
    class EvilFuture(asyncio.Future[None]):
        cancel_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            if raises:
                raise AssertionError("Future waiter cancel override must not run")
            return False

    loop = asyncio.new_event_loop()
    waiter = EvilFuture(loop=loop)
    continuations = 0

    async def outer_body() -> None:
        nonlocal continuations
        await waiter
        continuations += 1

    outer = loop.create_task(outer_body())
    loop.run_until_complete(asyncio.sleep(0))
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: outer)  # type: ignore[arg-type]
        override_calls = waiter.cancel_calls
        if not waiter.done():
            asyncio.Future.cancel(waiter)
        outcomes = loop.run_until_complete(asyncio.gather(outer, return_exceptions=True))
        assert result.known_losses == ("reflection_writer_contract_invalid",)
        assert outer.cancelled()
        assert isinstance(outcomes[0], asyncio.CancelledError)
        assert continuations == 0

    loop.close()
    assert override_calls == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_nested_task_waiter_chain_uses_trusted_recursive_cancellation(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class EvilInnerTask(asyncio.Task[None]):
        cancel_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            raise AssertionError("nested Task cancel override must not run")

    loop = asyncio.new_event_loop()
    leaf = loop.create_future()
    continuations = 0

    async def inner_body() -> None:
        nonlocal continuations
        await leaf
        continuations += 1

    inner = EvilInnerTask(inner_body(), loop=loop)

    async def outer_body() -> None:
        nonlocal continuations
        await inner
        continuations += 1

    outer = loop.create_task(outer_body())
    loop.run_until_complete(asyncio.sleep(0))
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: outer)  # type: ignore[arg-type]
        override_calls = inner.cancel_calls
        if not inner.done():
            asyncio.Task.cancel(inner)
        outcomes = loop.run_until_complete(asyncio.gather(outer, inner, return_exceptions=True))
        assert result.known_losses == ("reflection_writer_contract_invalid",)
        assert outer.cancelled() and inner.cancelled()
        assert all(isinstance(outcome, asyncio.CancelledError) for outcome in outcomes)
        assert continuations == 0

    loop.close()
    assert override_calls == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_completed_waiter_requests_owner_cancellation_before_queued_wakeup(
    caplog: pytest.LogCaptureFixture,
) -> None:
    loop = asyncio.new_event_loop()
    waiter = loop.create_future()
    continuations = 0

    async def body() -> None:
        nonlocal continuations
        await waiter
        continuations += 1

    task = loop.create_task(body())
    loop.run_until_complete(asyncio.sleep(0))
    waiter.set_result(None)
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
        cancelling_before_turn = task.cancelling()
        for _ in range(4):
            loop.run_until_complete(asyncio.sleep(0))
        terminal_before_cleanup = task.cancelled()
        if not task.done():
            asyncio.Task.cancel(task)
        outcomes = loop.run_until_complete(asyncio.gather(task, return_exceptions=True))

    loop.close()
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert cancelling_before_turn > 0
    assert terminal_before_cleanup
    assert isinstance(outcomes[0], asyncio.CancelledError)
    assert continuations == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_hostile_completed_waiter_is_retried_after_next_safe_suspension(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class EvilFuture(asyncio.Future[None]):
        cancel_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            raise AssertionError("hostile completed waiter hook must not run")

    loop = asyncio.new_event_loop()
    waiter = EvilFuture(loop=loop)
    second_waiter = loop.create_future()
    resumptions = 0
    side_effects = 0

    async def body() -> None:
        nonlocal resumptions, side_effects
        await waiter
        resumptions += 1
        await second_waiter
        side_effects += 1

    task = loop.create_task(body())
    loop.run_until_complete(asyncio.sleep(0))
    waiter.set_result(None)
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
        for _ in range(4):
            loop.run_until_complete(asyncio.sleep(0))
        terminal_before_cleanup = task.cancelled()
        override_calls = waiter.cancel_calls
        if not task.done():
            asyncio.Task.cancel(task)
        outcomes = loop.run_until_complete(asyncio.gather(task, return_exceptions=True))

    loop.close()
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert terminal_before_cleanup
    assert override_calls == 0
    assert isinstance(outcomes[0], asyncio.CancelledError)
    # The completed waiter's wakeup was already queued before adapter entry. Public
    # asyncio offers no way to preempt it without invoking the hostile hook or editing
    # the foreign loop queue, so the trusted retry cancels at the next suspension.
    assert resumptions == 1
    assert side_effects == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_owner_cancellation_is_repeated_after_coroutine_catches_first_request(
    caplog: pytest.LogCaptureFixture,
) -> None:
    loop = asyncio.new_event_loop()
    first_waiter = loop.create_future()
    second_waiter = loop.create_future()
    caught_cancellations = 0
    side_effects = 0

    async def body() -> None:
        nonlocal caught_cancellations, side_effects
        try:
            await first_waiter
        except asyncio.CancelledError:
            caught_cancellations += 1
        await second_waiter
        side_effects += 1

    task = loop.create_task(body())
    loop.run_until_complete(asyncio.sleep(0))
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
        cancelling_before_turn = task.cancelling()
        for _ in range(4):
            loop.run_until_complete(asyncio.sleep(0))
        terminal_before_cleanup = task.cancelled()
        if not task.done():
            asyncio.Task.cancel(task)
        outcomes = loop.run_until_complete(asyncio.gather(task, return_exceptions=True))

    loop.close()
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert cancelling_before_turn > 0
    assert terminal_before_cleanup
    assert isinstance(outcomes[0], asyncio.CancelledError)
    assert caught_cancellations == 1
    assert side_effects == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_nested_task_chain_repeats_cancellation_after_inner_catches_once(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class EvilInnerTask(asyncio.Task[None]):
        cancel_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            raise AssertionError("nested Task cancel override must not run")

    loop = asyncio.new_event_loop()
    first_leaf = loop.create_future()
    second_leaf = loop.create_future()
    caught_cancellations = 0
    side_effects = 0

    async def inner_body() -> None:
        nonlocal caught_cancellations, side_effects
        try:
            await first_leaf
        except asyncio.CancelledError:
            caught_cancellations += 1
        await second_leaf
        side_effects += 1

    inner = EvilInnerTask(inner_body(), loop=loop)

    async def outer_body() -> None:
        nonlocal side_effects
        await inner
        side_effects += 1

    outer = loop.create_task(outer_body())
    loop.run_until_complete(asyncio.sleep(0))
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: outer)  # type: ignore[arg-type]
        for _ in range(6):
            loop.run_until_complete(asyncio.sleep(0))
        terminal_before_cleanup = outer.cancelled() and inner.cancelled()
        override_calls = inner.cancel_calls
        if not inner.done():
            asyncio.Task.cancel(inner)
        outcomes = loop.run_until_complete(asyncio.gather(outer, inner, return_exceptions=True))

    loop.close()
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert terminal_before_cleanup
    assert override_calls == 0
    assert all(isinstance(outcome, asyncio.CancelledError) for outcome in outcomes)
    assert caught_cancellations == 1
    assert side_effects == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_inherited_future_cancel_instance_shadow_is_never_dispatched(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class InheritedFuture(asyncio.Future[None]):
        pass

    loop = asyncio.new_event_loop()
    waiter = InheritedFuture(loop=loop)
    override_calls = 0

    def hostile_cancel(self: InheritedFuture, *args: object, **kwargs: object) -> bool:
        nonlocal override_calls
        override_calls += 1
        raise AssertionError("instance cancel shadow must not run")

    waiter.cancel = MethodType(hostile_cancel, waiter)  # type: ignore[method-assign]

    async def body() -> None:
        await waiter

    task = loop.create_task(body())
    loop.run_until_complete(asyncio.sleep(0))
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
        outcomes = loop.run_until_complete(asyncio.gather(task, return_exceptions=True))

    loop.close()
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert override_calls == 0
    assert task.cancelled()
    assert isinstance(outcomes[0], asyncio.CancelledError)
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_bounded_retries_cancel_after_four_caught_requests(
    caplog: pytest.LogCaptureFixture,
) -> None:
    loop = asyncio.new_event_loop()
    waiters = [loop.create_future() for _ in range(5)]
    caught_indices: list[int] = []
    side_effects = 0

    async def body() -> None:
        nonlocal side_effects
        for index, waiter in enumerate(waiters[:4]):
            try:
                await waiter
            except asyncio.CancelledError:
                caught_indices.append(index)
        await waiters[4]
        side_effects += 1

    task = loop.create_task(body())
    loop.run_until_complete(asyncio.sleep(0))
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
        for _ in range(14):
            loop.run_until_complete(asyncio.sleep(0))
        terminal_before_cleanup = task.cancelled()
        cancellation_count = task.cancelling()
        for _ in range(8):
            if task.done():
                break
            asyncio.Task.cancel(task)
            loop.run_until_complete(asyncio.sleep(0))
        outcomes = loop.run_until_complete(asyncio.gather(task, return_exceptions=True))

    loop.close()
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert terminal_before_cleanup
    assert cancellation_count == 5
    assert caught_indices == [0, 1, 2, 3]
    assert isinstance(outcomes[0], asyncio.CancelledError)
    assert side_effects == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_bounded_retry_exhaustion_is_finite_for_cancellation_resistant_coroutine(
    caplog: pytest.LogCaptureFixture,
) -> None:
    loop = asyncio.new_event_loop()
    waiters = [loop.create_future() for _ in range(5)]
    survivor = loop.create_future()
    caught_indices: list[int] = []
    exhaustion_reached = False
    side_effects = 0

    async def body() -> None:
        nonlocal exhaustion_reached, side_effects
        for index, waiter in enumerate(waiters):
            try:
                await waiter
            except asyncio.CancelledError:
                caught_indices.append(index)
        exhaustion_reached = True
        await survivor
        side_effects += 1

    task = loop.create_task(body())
    loop.run_until_complete(asyncio.sleep(0))
    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
        for _ in range(14):
            loop.run_until_complete(asyncio.sleep(0))
        pending_at_exhaustion = not task.done()
        cancellation_count = task.cancelling()
        for _ in range(8):
            if task.done():
                break
            asyncio.Task.cancel(task)
            loop.run_until_complete(asyncio.sleep(0))
        outcomes = loop.run_until_complete(asyncio.gather(task, return_exceptions=True))

    loop.close()
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert pending_at_exhaustion
    assert cancellation_count == 5
    assert caught_indices == [0, 1, 2, 3, 4]
    assert exhaustion_reached
    assert isinstance(outcomes[0], asyncio.CancelledError)
    assert side_effects == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_debug_loop_in_foreign_thread_runs_full_threadsafe_retry_sequence(
    caplog: pytest.LogCaptureFixture,
) -> None:
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    loop_started = threading.Event()
    blocker_entered = threading.Event()
    release_blocker = threading.Event()
    task_terminal = threading.Event()
    caught_indices: list[int] = []
    side_effects = 0

    def run_loop() -> None:
        asyncio.set_event_loop(loop)
        loop_started.set()
        loop.run_forever()
        asyncio.set_event_loop(None)

    thread = threading.Thread(target=run_loop, name="reflection-37-4-loop")
    thread.start()
    assert loop_started.wait(timeout=2)

    async def setup_task() -> asyncio.Task[None]:
        async def body() -> None:
            nonlocal side_effects
            for index in range(4):
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    caught_indices.append(index)
            await asyncio.Event().wait()
            side_effects += 1

        task = asyncio.create_task(body())
        task.add_done_callback(lambda _: task_terminal.set())
        await asyncio.sleep(0)
        return task

    task = asyncio.run_coroutine_threadsafe(setup_task(), loop).result(timeout=2)

    def block_loop() -> None:
        blocker_entered.set()
        release_blocker.wait(timeout=3)

    asyncio.BaseEventLoop.call_soon_threadsafe(loop, block_loop)
    assert blocker_entered.wait(timeout=2)

    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
        release_blocker.set()
        terminal_before_cleanup = task_terminal.wait(timeout=2)
        cancellation_count = asyncio.Task.cancelling(task)

        asyncio.BaseEventLoop.call_soon_threadsafe(loop, asyncio.BaseEventLoop.stop, loop)
        thread.join(timeout=2)
        if not asyncio.Future.done(task):
            loop.close()
            coroutine = asyncio.Task.get_coro(task)
            coroutine.close()
            asyncio.Task._log_destroy_pending.__set__(task, False)
        else:
            loop.close()
        gc.collect()

    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert terminal_before_cleanup
    assert not thread.is_alive()
    assert asyncio.Future.cancelled(task)
    assert cancellation_count == 5
    assert caught_indices == [0, 1, 2, 3]
    assert side_effects == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_same_thread_running_loop_retains_bounded_retry_behavior(
    caplog: pytest.LogCaptureFixture,
) -> None:
    loop = asyncio.new_event_loop()
    caught_cancellations = 0
    side_effects = 0

    async def scenario() -> tuple[ReflectionResult, list[object], int]:
        nonlocal caught_cancellations, side_effects
        first_waiter = loop.create_future()
        second_waiter = loop.create_future()

        async def body() -> None:
            nonlocal caught_cancellations, side_effects
            try:
                await first_waiter
            except asyncio.CancelledError:
                caught_cancellations += 1
            await second_waiter
            side_effects += 1

        task = loop.create_task(body())
        await asyncio.sleep(0)
        result = compose_closing_reflection(_request(), lambda _: task)  # type: ignore[arg-type]
        outcomes = await asyncio.gather(task, return_exceptions=True)
        return result, outcomes, task.cancelling()

    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result, outcomes, cancellation_count = loop.run_until_complete(scenario())

    loop.close()
    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert isinstance(outcomes[0], asyncio.CancelledError)
    assert cancellation_count == 2
    assert caught_cancellations == 1
    assert side_effects == 0
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_standalone_future_on_foreign_debug_loop_cancels_on_owner_thread(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class EvilFuture(asyncio.Future[None]):
        cancel_calls = 0

        def cancel(self, *args: object, **kwargs: object) -> bool:
            self.cancel_calls += 1
            raise AssertionError("standalone Future cancel override must not run")

    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    loop_started = threading.Event()
    blocker_entered = threading.Event()
    release_blocker = threading.Event()
    task_terminal = threading.Event()
    side_effects = 0

    def run_loop() -> None:
        asyncio.set_event_loop(loop)
        loop_started.set()
        loop.run_forever()
        asyncio.set_event_loop(None)

    thread = threading.Thread(target=run_loop, name="reflection-37-4-future-loop")
    thread.start()
    assert loop_started.wait(timeout=2)

    async def setup_waiter() -> tuple[EvilFuture, asyncio.Task[None]]:
        nonlocal side_effects
        future = EvilFuture(loop=asyncio.get_running_loop())

        async def body() -> None:
            nonlocal side_effects
            await future
            side_effects += 1

        task = asyncio.create_task(body())
        task.add_done_callback(lambda _: task_terminal.set())
        await asyncio.sleep(0)
        return future, task

    future, task = asyncio.run_coroutine_threadsafe(setup_waiter(), loop).result(timeout=2)

    def block_loop() -> None:
        blocker_entered.set()
        release_blocker.wait(timeout=3)

    asyncio.BaseEventLoop.call_soon_threadsafe(loop, block_loop)
    assert blocker_entered.wait(timeout=2)

    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        warnings.simplefilter("error", UserWarning)
        result = compose_closing_reflection(_request(), lambda _: future)  # type: ignore[arg-type]
        release_blocker.set()
        terminal_before_cleanup = task_terminal.wait(timeout=2)
        override_calls = future.cancel_calls

        asyncio.BaseEventLoop.call_soon_threadsafe(loop, asyncio.BaseEventLoop.stop, loop)
        thread.join(timeout=2)
        if not asyncio.Future.done(task):
            loop.close()
            coroutine = asyncio.Task.get_coro(task)
            coroutine.close()
            asyncio.Task._log_destroy_pending.__set__(task, False)
        else:
            loop.close()
        gc.collect()

    assert result.known_losses == ("reflection_writer_contract_invalid",)
    assert terminal_before_cleanup
    assert not thread.is_alive()
    assert asyncio.Future.cancelled(future)
    assert asyncio.Future.cancelled(task)
    assert override_calls == 0
    assert side_effects == 0
    assert not [warning for warning in caught if issubclass(warning.category, UserWarning)]
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_generator_exit_resistant_task_keeps_pending_diagnostic(
    caplog: pytest.LogCaptureFixture,
) -> None:
    loop = asyncio.new_event_loop()

    async def resistant() -> None:
        try:
            await asyncio.Event().wait()
        except GeneratorExit:
            await asyncio.sleep(0)

    task = loop.create_task(resistant())
    loop.run_until_complete(asyncio.sleep(0))
    assert inspect.getcoroutinestate(asyncio.Task.get_coro(task)) == inspect.CORO_SUSPENDED
    loop.close()

    def writer(_: ReflectionRequest, returned: object = task) -> object:
        return returned

    with (
        caplog.at_level(logging.ERROR, logger="asyncio"),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("error", RuntimeWarning)
        result = compose_closing_reflection(_request(), writer)  # type: ignore[arg-type]
        coroutine = asyncio.Task.get_coro(task)
        coroutine_state = inspect.getcoroutinestate(coroutine)
        assert result.known_losses == ("reflection_writer_contract_invalid",)
        assert coroutine_state != inspect.CORO_CLOSED
        # Observe the diagnostic that production intentionally preserved, then
        # perform explicit test-only teardown without asking production to retry.
        asyncio.Task.__del__(task)
        coroutine.close()
        asyncio.Task._log_destroy_pending.__set__(task, False)
        del writer
        del task
        gc.collect()

    assert coroutine_state != inspect.CORO_CLOSED
    assert inspect.getcoroutinestate(coroutine) == inspect.CORO_CLOSED
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert [
        record
        for record in caplog.records
        if "Task was destroyed but it is pending" in record.message
    ]


@pytest.mark.parametrize(
    "field,value",
    [("rating", 5), ("location", "desk"), ("honest_line", "hard"), ("delta", 2), ("abilities", [])],
)
def test_no_learner_value_or_parallel_ability_surface(field: str, value: object) -> None:
    raw = _request().model_dump(mode="python") | {field: value}
    with pytest.raises(ValidationError):
        ReflectionRequest.model_validate(raw, strict=True)


def test_digests_json_round_trip_and_aggregate_anti_forgery() -> None:
    request = _request()
    result = compose_closing_reflection(request, lambda _: _candidate())
    assert result.authority_digest == reflection_authority_digest(request)
    assert result.candidate_digest == reflection_candidate_digest(_candidate())
    assert result.prework_digest == prework_callback_digest(request.prework)
    assert ReflectionResult.model_validate_json(result.model_dump_json()) == result
    raw = result.model_dump(mode="python")
    raw["authority_digest"] = "sha256:" + "0" * 64
    with pytest.raises(ValidationError):
        ReflectionResult.model_validate(raw, strict=True)


@pytest.mark.parametrize("location", ["result", "gate", "both"])
def test_prework_digest_mutation_is_rejected(location: str) -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    raw = result.model_dump(mode="python")
    forged = "sha256:" + "1" * 64
    if location in {"result", "both"}:
        raw["prework_digest"] = forged
    if location in {"gate", "both"}:
        raw["gate"]["prework_digest"] = forged
    with pytest.raises(ValidationError):
        ReflectionResult.model_validate(raw, strict=True)


@pytest.mark.parametrize("mutation", ["remove", "reorder", "text_drift"])
def test_visible_cue_removal_reorder_and_text_drift_are_rejected(mutation: str) -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    raw = result.model_dump(mode="python")
    cues = list(raw["prompt"]["ability_cues"])
    if mutation == "remove":
        cues.pop()
    elif mutation == "reorder":
        cues.reverse()
    else:
        cues[0]["vow_text"] = "Forged ability copy"
    raw["prompt"]["ability_cues"] = tuple(cues)
    with pytest.raises(ValidationError):
        ReflectionResult.model_validate(raw, strict=True)


def test_unknown_writer_ability_ref_degrades_without_exposing_prompt() -> None:
    candidate = ReflectionWriterCandidate(
        status="authored",
        ability_focuses=(
            ReflectionAbilityFocus(ability_ref="ability-a", capability_lens="name"),
            ReflectionAbilityFocus(ability_ref="unknown-ability", capability_lens="see"),
        ),
        known_losses=(),
        marker=None,
    )
    result = compose_closing_reflection(_request(), lambda _: candidate)
    assert result.status == "degraded"
    assert result.prompt is None
    assert result.known_losses == ("reflection_ability_binding_failed",)


@pytest.mark.parametrize(
    "updates",
    [
        {"declared_ability_refs": ()},
        {"declared_ability_refs": ("ability-a", "ability-a")},
        {"bound_ability_refs": ("ability-a", "ability-a")},
        {"candidate_digest": NO_CANDIDATE_DIGEST},
        {"failures": ("prework_callback_unavailable",)},
        {"failures": ("writer_unavailable",), "bound_ability_refs": ("ability-a",)},
        {"failures": ("ability_binding_failed",), "bound_ability_refs": ()},
        {
            "failures": ("ability_binding_failed",),
            "bound_ability_refs": ("ability-a", "ability-b"),
        },
        {"failures": ("reflection_gate_failed",)},
    ],
)
def test_standalone_gate_receipt_rejects_impossible_eligible_shapes(
    updates: dict[str, object],
) -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    raw = result.gate.model_dump(mode="python")
    raw.update({"status": "fail", **updates})
    with pytest.raises(ValidationError):
        ReflectionGateReceipt.model_validate(raw, strict=True)


@pytest.mark.parametrize(
    "updates",
    [
        {"candidate_digest": "sha256:" + "2" * 64},
        {"bound_ability_refs": ("ability-a",)},
        {"failures": ("writer_unavailable",)},
        {"status": "pass"},
    ],
)
def test_standalone_gate_receipt_rejects_impossible_pregate_shapes(
    updates: dict[str, object],
) -> None:
    result = compose_closing_reflection(
        _request(prework=False), lambda _: pytest.fail("writer must not run")
    )
    raw = result.gate.model_dump(mode="python")
    raw.update(updates)
    with pytest.raises(ValidationError):
        ReflectionGateReceipt.model_validate(raw, strict=True)


@pytest.mark.parametrize("status", ["unavailable", "degraded"])
def test_promise_failure_receipt_requires_empty_declared_refs(status: str) -> None:
    result = compose_closing_reflection(
        _request(status=status, prework=False), lambda _: pytest.fail("writer must not run")
    )
    raw = result.gate.model_dump(mode="python")
    assert raw["declared_ability_refs"] == ()
    raw["declared_ability_refs"] = ("forged-ability",)
    with pytest.raises(ValidationError):
        ReflectionGateReceipt.model_validate(raw, strict=True)


def test_promise_failure_receipt_preserves_either_prework_digest_shape() -> None:
    promise = _promise("unavailable")
    without = compose_closing_reflection(
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=None),
        lambda _: pytest.fail("writer must not run"),
    )
    with_authority = compose_closing_reflection(
        ReflectionRequest(lesson_ref="part-2", promise=promise, prework=_prework()),
        lambda _: pytest.fail("writer must not run"),
    )
    assert without.gate.prework_digest == NO_PREWORK_DIGEST
    assert with_authority.gate.prework_digest != NO_PREWORK_DIGEST
    assert ReflectionGateReceipt.model_validate(without.gate.model_dump(mode="python"), strict=True)
    assert ReflectionGateReceipt.model_validate(
        with_authority.gate.model_dump(mode="python"), strict=True
    )


@pytest.mark.parametrize("disposition", ["prework_absent", "prework_mismatch"])
def test_prework_failure_receipt_requires_nonempty_declared_refs(disposition: str) -> None:
    if disposition == "prework_absent":
        result = compose_closing_reflection(
            _request(prework=False), lambda _: pytest.fail("writer must not run")
        )
    else:
        request = ReflectionRequest(
            lesson_ref="part-2",
            promise=_promise(),
            prework=_prework(_promise(suffix=" changed")),
        )
        result = compose_closing_reflection(request, lambda _: pytest.fail("writer must not run"))
    assert result.gate.pre_gate_disposition == disposition
    raw = result.gate.model_dump(mode="python")
    raw["declared_ability_refs"] = ()
    with pytest.raises(ValidationError):
        ReflectionGateReceipt.model_validate(raw, strict=True)


def test_prework_absent_receipt_requires_exact_null_prework_digest() -> None:
    result = compose_closing_reflection(
        _request(prework=False), lambda _: pytest.fail("writer must not run")
    )
    assert result.gate.prework_digest == NO_PREWORK_DIGEST
    raw = result.gate.model_dump(mode="python")
    raw["prework_digest"] = "sha256:" + "5" * 64
    with pytest.raises(ValidationError):
        ReflectionGateReceipt.model_validate(raw, strict=True)


@pytest.mark.parametrize("disposition", ["prework_mismatch", "eligible"])
def test_present_prework_receipt_rejects_null_prework_digest(disposition: str) -> None:
    if disposition == "eligible":
        result = compose_closing_reflection(_request(), lambda _: _candidate())
    else:
        request = ReflectionRequest(
            lesson_ref="part-2",
            promise=_promise(),
            prework=_prework(_promise(suffix=" changed")),
        )
        result = compose_closing_reflection(request, lambda _: pytest.fail("writer must not run"))
    assert result.gate.pre_gate_disposition == disposition
    raw = result.gate.model_dump(mode="python")
    raw["prework_digest"] = NO_PREWORK_DIGEST
    with pytest.raises(ValidationError):
        ReflectionGateReceipt.model_validate(raw, strict=True)


@pytest.mark.parametrize(
    "field,value",
    [
        ("authority_digest", "sha256:" + "3" * 64),
        ("candidate_digest", "sha256:" + "4" * 64),
        ("pre_gate_disposition", "prework_absent"),
        ("bound_ability_refs", ("ability-b", "ability-a")),
        ("failures", ("writer_unavailable",)),
    ],
)
def test_forged_aggregate_receipt_fields_are_rejected(field: str, value: object) -> None:
    result = compose_closing_reflection(_request(), lambda _: _candidate())
    raw = result.model_dump(mode="python")
    raw["gate"][field] = value
    with pytest.raises(ValidationError):
        ReflectionResult.model_validate(raw, strict=True)


def test_strict_schemas_frozen_models_and_public_boundary_types() -> None:
    for model in (
        ReflectionRequest,
        ReflectionAbilityFocus,
        ReflectionWriterCandidate,
        ShiftedQuestionPrompt,
        ReflectionResult,
    ):
        schema = model.model_json_schema()
        assert schema["additionalProperties"] is False
        assert all(
            definition.get("type") != "object" or definition.get("additionalProperties") is False
            for definition in schema.get("$defs", {}).values()
        )
    request = _request()
    with pytest.raises(ValidationError):
        request.lesson_ref = "changed"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ReflectionRequest.model_validate(
            request.model_dump(mode="python") | {"lesson_ref": 7}, strict=True
        )
    with pytest.raises(TypeError):
        compose_closing_reflection(request.model_dump(), lambda _: _candidate())  # type: ignore[arg-type]


def test_upstream_authority_ref_defects_are_rejected_recursively() -> None:
    for mutate in (
        lambda raw: raw["promise"].__setitem__("authority_refs", ("ratified#0",)),
        lambda raw: raw["promise"].__setitem__("authority_refs", ("ratified#0", "ratified#0")),
        lambda raw: raw["promise"]["gate_receipt"].__setitem__("failures", ("forged",)),
    ):
        raw = _request().model_dump(mode="python")
        mutate(raw)
        with pytest.raises(ValidationError):
            ReflectionRequest.model_validate(raw, strict=True)


def test_fixture_shapes_are_exact_and_repeatable() -> None:
    request = _request()
    candidate = _candidate()
    result = compose_closing_reflection(request, lambda _: candidate)
    expected = {
        "request.json": request.model_dump(mode="json"),
        "writer_candidate.json": candidate.model_dump(mode="json"),
        "semantic_manifest.json": result.model_dump(mode="json"),
    }
    for name, payload in expected.items():
        assert json.loads((FIXTURES / name).read_text(encoding="utf-8")) == payload


def test_m3_import_and_ownership_fences() -> None:
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports |= {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not imports & {"os", "pathlib", "openai", "litellm", "requests"}
    source = MODULE.read_text(encoding="utf-8").lower()
    assert "filesystem" not in source
    assert "orchestrator" not in source
    assert "researchpacket" not in source
