"""Pure Promise-bound closing-reflection projection for Story 37.4."""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import re
import unicodedata
from collections.abc import Callable
from contextlib import suppress
from types import CoroutineType
from typing import Annotated, Literal, Protocol

from pydantic import AfterValidator, BaseModel, ConfigDict, ValidationError, model_validator

from app.marcus.lesson_plan.prework_projection import (
    FRICTION_SCALE,
    FrictionScaleSpec,
    PreWorkBrief,
    PreWorkProvenance,
    PromiseProjection,
    PromiseVow,
    SceneBrief,
)
from app.marcus.lesson_plan.promise_projection import (
    PromiseGateReceipt as PromiseAuthorityGateReceipt,
)
from app.marcus.lesson_plan.promise_projection import PromiseProjectionResult

ReflectionStatus = Literal["authored", "degraded", "unavailable"]
CapabilityLens = Literal["name", "see", "do"]
PreGateDisposition = Literal[
    "eligible",
    "promise_unavailable",
    "promise_degraded",
    "prework_absent",
    "prework_mismatch",
]
GateFailure = Literal[
    "promise_authority_unavailable",
    "promise_authority_degraded",
    "prework_callback_unavailable",
    "prework_callback_mismatch",
    "writer_unavailable",
    "writer_contract_invalid",
    "ability_binding_failed",
    "reflection_gate_failed",
]
WriterLoss = Literal["reflection_writer_unavailable", "reflection_writer_contract_invalid"]
ResultLoss = Literal[
    "reflection_promise_authority_unavailable",
    "reflection_promise_authority_degraded",
    "reflection_prework_callback_unavailable",
    "reflection_prework_callback_mismatch",
    "reflection_writer_unavailable",
    "reflection_writer_contract_invalid",
    "reflection_ability_binding_failed",
    "reflection_gate_failed",
]

CALLBACK_CLAUSE = (
    "Return to the friction mark, location, and honest line you wrote before the presentation."
)
CAPABILITY_CLAUSE = (
    "With the lesson abilities above in mind, what can you now name, see, or do "
    "about that friction?"
)
MOVE_CLAUSE = "Write one concrete move you will make this week."
REFLECTION_UNAVAILABLE_MARKER = "closing_reflection_unavailable"
REFLECTION_DEGRADED_MARKER = "closing_reflection_degraded"
OPERATOR_SEMANTIC_WARNING = "reflection_lens_mapping_requires_operator_spot_check"


def _non_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("value must contain non-whitespace text")
    return value


def _stable_ref(value: str) -> str:
    _non_blank(value)
    if value != value.strip():
        raise ValueError("stable references cannot have surrounding whitespace")
    if any(unicodedata.category(char).startswith("C") for char in value):
        raise ValueError("stable references cannot contain control characters")
    return value


_RAW_HTML = re.compile(r"</?[A-Za-z][^<>]*>|<!--|<![A-Za-z\[]|<\?")
_MARKDOWN_BLOCK = re.compile(
    r"^\s*(?:#{1,6}|(?:[-+*\u2022\u2023\u2043\u25e6\u2219\u25aa\u25ab\u25cf\u25cb]"
    r"|\d+[.)])\s|>\s?|```|~~~)"
)


def _has_markdown_reference_surface(value: str) -> bool:
    """Fail closed on the delimiters shared by every Markdown reference form.

    The downstream cue is rendered as Markdown.  A bracket can therefore become a
    shortcut reference through a definition outside this single vow, so no bracketed
    sub-grammar is safe at this boundary.  Scanning the two delimiters also covers
    nested labels and backslash-escaped closing brackets without parser heuristics.
    """
    return any(character in "[]" for character in value)


def _is_commonmark_thematic_break(value: str) -> bool:
    """Recognize marker-only CommonMark breaks without rejecting marker prose."""
    markers = value.replace(" ", "").replace("\t", "")
    return (
        len(markers) >= 3
        and markers[0] in "-*_"
        and all(character == markers[0] for character in markers)
    )


def _is_commonmark_setext_underline(value: str) -> bool:
    """Recognize marker-only H1/H2 underlines in their valid local grammar."""
    candidate = value.strip(" \t")
    return (
        bool(candidate)
        and candidate[0] in "=-"
        and all(character == candidate[0] for character in candidate)
    )


_COMMONMARK_RAW_TYPE_1_TAGS = frozenset({"script", "pre", "style", "textarea"})
_COMMONMARK_RAW_TYPE_6_TAGS = frozenset(
    {
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
    }
)


def _starts_commonmark_raw_html_block(value: str) -> bool:
    """Recognize type-1/type-6 starts, including end-of-line tag openers."""
    if not value.startswith("<"):
        return False
    position = 1
    closing = position < len(value) and value[position] == "/"
    if closing:
        position += 1
    name_start = position
    while position < len(value) and value[position].isascii() and value[position].isalnum():
        position += 1
    tag_name = value[name_start:position].lower()
    if not tag_name:
        return False
    allowed = _COMMONMARK_RAW_TYPE_6_TAGS
    if not closing:
        allowed = allowed | _COMMONMARK_RAW_TYPE_1_TAGS
    if tag_name not in allowed:
        return False
    remainder = value[position:]
    return not remainder or remainder[0] in " \t>" or remainder.startswith("/>")


_SEMANTIC_BLANK_RANGES = (
    # Closed policy for Python's runtime Unicode database: these named characters
    # encode blank/filler/space semantics without visible ink. This intentionally
    # excludes visible depictions of whitespace such as U+2420 SYMBOL FOR SPACE.
    (0x115F, 0x1160),  # Hangul choseong and jungseong fillers
    (0x2800, 0x2800),  # Braille pattern blank
    (0x303F, 0x303F),  # Ideographic half fill space
    (0x3164, 0x3164),  # Hangul compatibility filler
    (0xFFA0, 0xFFA0),  # Halfwidth Hangul filler
    (0x13441, 0x13442),  # Egyptian hieroglyph full and half blanks
    (0x1DA7F, 0x1DA80),  # SignWriting wall/floor-plane spaces
)
_BLACK_FLAG = "\U0001f3f4"
_TAG_SPEC_START = 0xE0020
_TAG_SPEC_END = 0xE007E
_TAG_DIGIT_START = 0xE0030
_TAG_DIGIT_END = 0xE0039
_TAG_LOWERCASE_START = 0xE0061
_TAG_LOWERCASE_END = 0xE007A
_CANCEL_TAG = "\U000e007f"


def _tag_encode_ascii(value: str) -> str:
    return "".join(chr(0xE0000 + ord(character)) for character in value)


# Pinned closed registry of RGI subdivision flags supported by Unicode emoji data.
# No arbitrary tag-encoded text is admitted merely because it uses the tag alphabet.
_RGI_SUBDIVISION_FLAG_TAG_PAYLOADS = frozenset(
    _tag_encode_ascii(payload) for payload in ("gbeng", "gbsct", "gbwls")
)


def _is_semantic_blank(character: str) -> bool:
    codepoint = ord(character)
    return any(start <= codepoint <= end for start, end in _SEMANTIC_BLANK_RANGES)


def _is_subdivision_tag_payload(codepoint: int) -> bool:
    return (
        _TAG_DIGIT_START <= codepoint <= _TAG_DIGIT_END
        or _TAG_LOWERCASE_START <= codepoint <= _TAG_LOWERCASE_END
    )


def _tag_sequences_are_structurally_valid(value: str) -> bool:
    """Allow only lowercase-letter/digit tags in complete subdivision flags."""
    position = 0
    while position < len(value):
        codepoint = ord(value[position])
        if value[position] == _BLACK_FLAG and position + 1 < len(value):
            cursor = position + 1
            while cursor < len(value) and _is_subdivision_tag_payload(ord(value[cursor])):
                cursor += 1
            if cursor > position + 1:
                payload = value[position + 1 : cursor]
                if (
                    payload not in _RGI_SUBDIVISION_FLAG_TAG_PAYLOADS
                    or cursor >= len(value)
                    or value[cursor] != _CANCEL_TAG
                ):
                    return False
                position = cursor + 1
                continue
        if _TAG_SPEC_START <= codepoint <= _TAG_SPEC_END or value[position] == _CANCEL_TAG:
            return False
        position += 1
    return True


def _has_visible_vow_character(value: str) -> bool:
    return any(
        not character.isspace()
        and not _is_semantic_blank(character)
        and unicodedata.category(character)[0] not in {"C", "M"}
        for character in value
    )


def _safe_vow_text(value: str) -> str:
    _non_blank(value)
    if not _has_visible_vow_character(value):
        raise ValueError("ability display text requires a visible character")
    if not _tag_sequences_are_structurally_valid(value):
        raise ValueError("Unicode tag characters require a complete subdivision flag sequence")
    if value != value.strip():
        raise ValueError("ability display text cannot have surrounding whitespace")
    if any(
        char in "\r\n\u2028\u2029"
        or (
            unicodedata.category(char).startswith("C")
            and char not in {"\u200c", "\u200d", _CANCEL_TAG}
            and not _is_subdivision_tag_payload(ord(char))
        )
        for char in value
    ):
        raise ValueError("ability display text must be a safe single line")
    if (
        _RAW_HTML.search(value)
        or _MARKDOWN_BLOCK.search(value)
        or _has_markdown_reference_surface(value)
        or _is_commonmark_thematic_break(value)
        or _is_commonmark_setext_underline(value)
        or _starts_commonmark_raw_html_block(value)
    ):
        raise ValueError("ability display text cannot inject markup")
    return value


def _sha256(value: str) -> str:
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError("value must be a canonical sha256 digest")
    return value


NonBlankStr = Annotated[str, AfterValidator(_non_blank)]
StableRef = Annotated[str, AfterValidator(_stable_ref)]
SafeVowText = Annotated[str, AfterValidator(_safe_vow_text)]
Sha256Digest = Annotated[str, AfterValidator(_sha256)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        validate_default=True,
    )


def _unique(values: tuple[str, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")


def _canonical_json_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _owned_model_field(model: BaseModel, field: str) -> object:
    """Read an owned model field without consulting instance overrides."""
    try:
        return object.__getattribute__(model, field)
    except BaseException as exc:
        raise ValueError(f"owned model is missing {field}") from exc


def _require_exact_model(value: object, expected_type: type[BaseModel], label: str) -> None:
    if type(value) is not expected_type:
        raise ValueError(f"{label} must be an exact {expected_type.__name__}")


def _require_exact_model_tuple(
    value: object, expected_type: type[BaseModel], label: str
) -> tuple[BaseModel, ...]:
    if type(value) is not tuple or any(type(item) is not expected_type for item in value):
        raise ValueError(f"{label} must contain exact {expected_type.__name__} models")
    return value


def _preflight_owned_graph(model: BaseModel, expected_type: type[BaseModel]) -> None:
    """Reject foreign nested models before schema-directed serialization can coerce them."""
    if expected_type is ReflectionWriterCandidate:
        _require_exact_model_tuple(
            _owned_model_field(model, "ability_focuses"),
            ReflectionAbilityFocus,
            "candidate focuses",
        )
    elif expected_type is ShiftedQuestionPrompt:
        _require_exact_model_tuple(
            _owned_model_field(model, "ability_cues"),
            ReflectionAbilityCue,
            "prompt cues",
        )
        _require_exact_model(
            _owned_model_field(model, "clauses"),
            ShiftedQuestionClauses,
            "prompt clauses",
        )
    elif expected_type is PromiseProjectionResult:
        projection = _owned_model_field(model, "projection")
        _require_exact_model(projection, PromiseProjection, "Promise projection")
        _require_exact_model(
            _owned_model_field(model, "gate_receipt"),
            PromiseAuthorityGateReceipt,
            "Promise gate receipt",
        )
        _require_exact_model_tuple(
            _owned_model_field(projection, "vows"), PromiseVow, "Promise vows"
        )
    elif expected_type is PreWorkBrief:
        _require_exact_model(_owned_model_field(model, "scene"), SceneBrief, "pre-work scene")
        _require_exact_model(
            _owned_model_field(model, "friction_scale"),
            FrictionScaleSpec,
            "pre-work Friction Scale",
        )
        promise = _owned_model_field(model, "promise")
        _require_exact_model(promise, PromiseProjection, "pre-work Promise")
        _require_exact_model_tuple(
            _owned_model_field(promise, "vows"), PromiseVow, "pre-work Promise vows"
        )
        _require_exact_model(
            _owned_model_field(model, "provenance"),
            PreWorkProvenance,
            "pre-work provenance",
        )
    elif expected_type is ReflectionRequest:
        promise = _owned_model_field(model, "promise")
        _require_exact_model(promise, PromiseProjectionResult, "request Promise")
        _preflight_owned_graph(promise, PromiseProjectionResult)
        prework = _owned_model_field(model, "prework")
        if prework is not None:
            _require_exact_model(prework, PreWorkBrief, "request pre-work")
            _preflight_owned_graph(prework, PreWorkBrief)
    elif expected_type is ReflectionResult:
        authority = _owned_model_field(model, "authority")
        _require_exact_model(authority, ReflectionRequest, "result authority")
        _preflight_owned_graph(authority, ReflectionRequest)
        candidate = _owned_model_field(model, "candidate_snapshot")
        if candidate is not None:
            _require_exact_model(candidate, ReflectionWriterCandidate, "result candidate")
            _preflight_owned_graph(candidate, ReflectionWriterCandidate)
        _require_exact_model(
            _owned_model_field(model, "gate"), ReflectionGateReceipt, "result gate"
        )
        prompt = _owned_model_field(model, "prompt")
        if prompt is not None:
            _require_exact_model(prompt, ShiftedQuestionPrompt, "result prompt")
            _preflight_owned_graph(prompt, ShiftedQuestionPrompt)


def _trusted_model_dump(
    model: BaseModel,
    expected_type: type[BaseModel],
    *,
    mode: Literal["python", "json"] = "python",
) -> dict[str, object]:
    """Serialize with the expected class-owned schema, bypassing instance state."""
    if type(model) is not expected_type:
        raise ValueError(f"model must be an exact {expected_type.__name__}")
    _preflight_owned_graph(model, expected_type)
    return expected_type.__pydantic_serializer__.to_python(model, mode=mode, warnings="none")


def _validate_promise(promise: PromiseProjectionResult) -> PromiseProjectionResult:
    if type(promise) is not PromiseProjectionResult:
        raise ValueError("Promise snapshot must be an exact PromiseProjectionResult")
    promise = PromiseProjectionResult.model_validate(
        _trusted_model_dump(promise, PromiseProjectionResult), strict=True
    )
    projection = promise.projection
    if projection.status == "authored":
        ids = tuple(vow.objective_id for vow in projection.vows)
        refs = promise.authority_refs
        if not ids or projection.known_losses or projection.marker is not None:
            raise ValueError("authored Promise authority requires complete vows")
        if promise.gate_receipt.failures:
            raise ValueError("authored Promise authority requires a passing gate")
        if len(refs) != len(ids):
            raise ValueError("Promise authority refs must align 1:1 with vows")
        _unique(ids, "Promise ability refs")
        _unique(refs, "Promise authority refs")
        for ref in ids + refs:
            _stable_ref(ref)
        for vow in projection.vows:
            _safe_vow_text(vow.text)
    else:
        if projection.vows or promise.authority_refs:
            raise ValueError("non-authored Promise cannot expose authority")
        if (
            len(projection.known_losses) != 1
            or projection.marker is None
            or promise.gate_receipt.failures != projection.known_losses
        ):
            raise ValueError("non-authored Promise requires reconciled honesty")
    return promise


def _validate_prework(prework: PreWorkBrief) -> PreWorkBrief:
    if type(prework) is not PreWorkBrief:
        raise ValueError("pre-work snapshot must be an exact PreWorkBrief")
    prework = PreWorkBrief.model_validate(_trusted_model_dump(prework, PreWorkBrief), strict=True)
    if prework.friction_scale != FRICTION_SCALE:
        raise ValueError("pre-work callback requires the canonical Friction Scale")
    return prework


class ReflectionRequest(_StrictModel):
    lesson_ref: StableRef
    promise: PromiseProjectionResult
    prework: PreWorkBrief | None

    @model_validator(mode="after")
    def _recursive_authority(self) -> ReflectionRequest:
        promise = _validate_promise(self.promise)
        prework = _validate_prework(self.prework) if self.prework is not None else None
        object.__setattr__(self, "promise", promise)
        object.__setattr__(self, "prework", prework)
        return self


class ReflectionAbilityFocus(_StrictModel):
    ability_ref: StableRef
    capability_lens: CapabilityLens


class ReflectionWriterCandidate(_StrictModel):
    status: ReflectionStatus
    ability_focuses: tuple[ReflectionAbilityFocus, ...]
    known_losses: tuple[WriterLoss, ...]
    marker: NonBlankStr | None

    @model_validator(mode="after")
    def _honest_candidate(self) -> ReflectionWriterCandidate:
        if any(type(item) is not ReflectionAbilityFocus for item in self.ability_focuses):
            raise ValueError("candidate focuses must be exact ReflectionAbilityFocus models")
        focuses = tuple(
            ReflectionAbilityFocus.model_validate(
                _trusted_model_dump(item, ReflectionAbilityFocus), strict=True
            )
            for item in self.ability_focuses
        )
        if self.status == "authored":
            if not focuses or self.known_losses or self.marker is not None:
                raise ValueError("authored candidate requires only ability focuses")
            _unique(tuple(focus.ability_ref for focus in focuses), "candidate ability refs")
        elif self.status == "unavailable":
            if (
                focuses
                or self.known_losses != ("reflection_writer_unavailable",)
                or self.marker != REFLECTION_UNAVAILABLE_MARKER
            ):
                raise ValueError("unavailable candidate requires canonical honesty")
        elif (
            focuses
            or self.known_losses != ("reflection_writer_contract_invalid",)
            or self.marker != REFLECTION_DEGRADED_MARKER
        ):
            raise ValueError("degraded candidate requires canonical honesty")
        object.__setattr__(self, "ability_focuses", focuses)
        return self


class ReflectionAbilityCue(_StrictModel):
    ability_ref: StableRef
    vow_text: SafeVowText
    capability_lens: CapabilityLens


class ShiftedQuestionClauses(_StrictModel):
    callback: Literal[
        "Return to the friction mark, location, and honest line you wrote before the presentation."
    ] = CALLBACK_CLAUSE
    capability: Literal[
        "With the lesson abilities above in mind, what can you now name, see, or do "
        "about that friction?"
    ] = CAPABILITY_CLAUSE
    move: Literal["Write one concrete move you will make this week."] = MOVE_CLAUSE


class ShiftedQuestionPrompt(_StrictModel):
    ability_cues: tuple[ReflectionAbilityCue, ...]
    clauses: ShiftedQuestionClauses = ShiftedQuestionClauses()

    @model_validator(mode="after")
    def _requires_cues(self) -> ShiftedQuestionPrompt:
        if not self.ability_cues:
            raise ValueError("shifted question requires authoritative ability cues")
        if any(type(cue) is not ReflectionAbilityCue for cue in self.ability_cues):
            raise ValueError("prompt cues must be exact ReflectionAbilityCue models")
        if type(self.clauses) is not ShiftedQuestionClauses:
            raise ValueError("prompt clauses must be an exact ShiftedQuestionClauses model")
        cues = tuple(
            ReflectionAbilityCue.model_validate(
                _trusted_model_dump(cue, ReflectionAbilityCue), strict=True
            )
            for cue in self.ability_cues
        )
        _unique(tuple(cue.ability_ref for cue in cues), "prompt ability cue refs")
        clauses = ShiftedQuestionClauses.model_validate(
            _trusted_model_dump(self.clauses, ShiftedQuestionClauses), strict=True
        )
        object.__setattr__(self, "ability_cues", cues)
        object.__setattr__(self, "clauses", clauses)
        return self


class ClosingReflectionWriter(Protocol):
    def __call__(self, request: ReflectionRequest) -> ReflectionWriterCandidate: ...


NO_CANDIDATE_DIGEST = _canonical_json_digest(None)
NO_PREWORK_DIGEST = _canonical_json_digest(None)


def reflection_authority_digest(request: ReflectionRequest) -> str:
    if type(request) is not ReflectionRequest:
        raise TypeError("request must be an exact ReflectionRequest")
    request = ReflectionRequest.model_validate(
        _trusted_model_dump(request, ReflectionRequest), strict=True
    )
    return _canonical_json_digest(_trusted_model_dump(request, ReflectionRequest, mode="json"))


def reflection_candidate_digest(candidate: ReflectionWriterCandidate | None) -> str:
    if candidate is None:
        return NO_CANDIDATE_DIGEST
    if type(candidate) is not ReflectionWriterCandidate:
        raise TypeError("candidate must be an exact ReflectionWriterCandidate")
    candidate = ReflectionWriterCandidate.model_validate(
        _trusted_model_dump(candidate, ReflectionWriterCandidate), strict=True
    )
    return _canonical_json_digest(
        _trusted_model_dump(candidate, ReflectionWriterCandidate, mode="json")
    )


def prework_callback_digest(prework: PreWorkBrief | None) -> str:
    if prework is None:
        return NO_PREWORK_DIGEST
    prework = _validate_prework(prework)
    return _canonical_json_digest(_trusted_model_dump(prework, PreWorkBrief, mode="json"))


def _pre_gate(request: ReflectionRequest) -> PreGateDisposition:
    status = request.promise.projection.status
    if status == "unavailable":
        return "promise_unavailable"
    if status == "degraded":
        return "promise_degraded"
    if request.prework is None:
        return "prework_absent"
    if request.prework.promise != request.promise.projection:
        return "prework_mismatch"
    return "eligible"


def _ability_cues(
    request: ReflectionRequest, candidate: ReflectionWriterCandidate
) -> tuple[ReflectionAbilityCue, ...]:
    return tuple(
        ReflectionAbilityCue(
            ability_ref=vow.objective_id,
            vow_text=vow.text,
            capability_lens=focus.capability_lens,
        )
        for vow, focus in zip(
            request.promise.projection.vows, candidate.ability_focuses, strict=True
        )
    )


def _binding_valid(request: ReflectionRequest, candidate: ReflectionWriterCandidate) -> bool:
    declared = tuple(vow.objective_id for vow in request.promise.projection.vows)
    bound = tuple(focus.ability_ref for focus in candidate.ability_focuses)
    return declared == bound and len(bound) == len(set(bound))


_PRE_GATE_FAILURE: dict[PreGateDisposition, GateFailure] = {
    "promise_unavailable": "promise_authority_unavailable",
    "promise_degraded": "promise_authority_degraded",
    "prework_absent": "prework_callback_unavailable",
    "prework_mismatch": "prework_callback_mismatch",
    "eligible": "reflection_gate_failed",
}


class ReflectionGateReceipt(_StrictModel):
    authority_digest: Sha256Digest
    prework_digest: Sha256Digest
    candidate_digest: Sha256Digest
    pre_gate_disposition: PreGateDisposition
    status: Literal["pass", "fail"]
    declared_ability_refs: tuple[StableRef, ...]
    bound_ability_refs: tuple[StableRef, ...]
    failures: tuple[GateFailure, ...]
    operator_warnings: tuple[
        Literal["reflection_lens_mapping_requires_operator_spot_check"], ...
    ] = (OPERATOR_SEMANTIC_WARNING,)

    @model_validator(mode="after")
    def _reconcile(self) -> ReflectionGateReceipt:
        _unique(self.declared_ability_refs, "declared ability refs")
        _unique(self.bound_ability_refs, "bound ability refs")
        if self.pre_gate_disposition != "eligible":
            if (
                self.status != "fail"
                or self.candidate_digest != NO_CANDIDATE_DIGEST
                or self.bound_ability_refs
                or self.failures != (_PRE_GATE_FAILURE[self.pre_gate_disposition],)
            ):
                raise ValueError("pre-gate receipt must preserve zero-call honesty")
            if self.pre_gate_disposition in {"promise_unavailable", "promise_degraded"}:
                if self.declared_ability_refs:
                    raise ValueError("non-authored Promise receipt cannot declare abilities")
            elif not self.declared_ability_refs:
                raise ValueError("pre-work failure receipt requires Promise abilities")
            if (
                self.pre_gate_disposition == "prework_absent"
                and self.prework_digest != NO_PREWORK_DIGEST
            ):
                raise ValueError("absent pre-work requires the null snapshot digest")
            if (
                self.pre_gate_disposition == "prework_mismatch"
                and self.prework_digest == NO_PREWORK_DIGEST
            ):
                raise ValueError("pre-work mismatch requires a present snapshot digest")
        else:
            if (
                not self.declared_ability_refs
                or self.candidate_digest == NO_CANDIDATE_DIGEST
                or self.prework_digest == NO_PREWORK_DIGEST
            ):
                raise ValueError("eligible receipt requires declared authority and a candidate")
            if self.status == "pass":
                if self.failures or self.declared_ability_refs != self.bound_ability_refs:
                    raise ValueError("passing reflection gate requires exact binding")
            else:
                if len(self.failures) != 1:
                    raise ValueError(
                        "failed reflection gate requires one precedence-selected failure"
                    )
                failure = self.failures[0]
                if failure in {"writer_unavailable", "writer_contract_invalid"}:
                    if self.bound_ability_refs:
                        raise ValueError("writer failure cannot claim an ability binding")
                elif failure == "ability_binding_failed":
                    if (
                        not self.bound_ability_refs
                        or self.bound_ability_refs == self.declared_ability_refs
                    ):
                        raise ValueError("binding failure requires a nonempty mismatched binding")
                else:
                    raise ValueError("eligible receipt carries an impossible failure family")
        if self.operator_warnings != (OPERATOR_SEMANTIC_WARNING,):
            raise ValueError("reflection gate requires its canonical WARN")
        return self


def _gate(
    request: ReflectionRequest, candidate: ReflectionWriterCandidate | None
) -> ReflectionGateReceipt:
    disposition = _pre_gate(request)
    declared = tuple(vow.objective_id for vow in request.promise.projection.vows)
    if disposition != "eligible":
        return ReflectionGateReceipt(
            authority_digest=reflection_authority_digest(request),
            prework_digest=prework_callback_digest(request.prework),
            candidate_digest=NO_CANDIDATE_DIGEST,
            pre_gate_disposition=disposition,
            status="fail",
            declared_ability_refs=declared,
            bound_ability_refs=(),
            failures=(_PRE_GATE_FAILURE[disposition],),
        )
    if candidate is None:
        raise ValueError("eligible gate requires candidate snapshot")
    bound = tuple(focus.ability_ref for focus in candidate.ability_focuses)
    if candidate.status == "unavailable":
        failure: GateFailure = "writer_unavailable"
    elif candidate.status == "degraded":
        failure = "writer_contract_invalid"
    elif not _binding_valid(request, candidate):
        failure = "ability_binding_failed"
    else:
        failure = "reflection_gate_failed"
        return ReflectionGateReceipt(
            authority_digest=reflection_authority_digest(request),
            prework_digest=prework_callback_digest(request.prework),
            candidate_digest=reflection_candidate_digest(candidate),
            pre_gate_disposition="eligible",
            status="pass",
            declared_ability_refs=declared,
            bound_ability_refs=bound,
            failures=(),
        )
    return ReflectionGateReceipt(
        authority_digest=reflection_authority_digest(request),
        prework_digest=prework_callback_digest(request.prework),
        candidate_digest=reflection_candidate_digest(candidate),
        pre_gate_disposition="eligible",
        status="fail",
        declared_ability_refs=declared,
        bound_ability_refs=bound,
        failures=(failure,),
    )


_PRE_GATE_RESULT: dict[PreGateDisposition, tuple[ReflectionStatus, ResultLoss, str]] = {
    "promise_unavailable": (
        "unavailable",
        "reflection_promise_authority_unavailable",
        REFLECTION_UNAVAILABLE_MARKER,
    ),
    "promise_degraded": (
        "degraded",
        "reflection_promise_authority_degraded",
        REFLECTION_DEGRADED_MARKER,
    ),
    "prework_absent": (
        "unavailable",
        "reflection_prework_callback_unavailable",
        REFLECTION_UNAVAILABLE_MARKER,
    ),
    "prework_mismatch": (
        "degraded",
        "reflection_prework_callback_mismatch",
        REFLECTION_DEGRADED_MARKER,
    ),
    "eligible": ("degraded", "reflection_gate_failed", REFLECTION_DEGRADED_MARKER),
}


def _candidate_result(
    candidate: ReflectionWriterCandidate, gate: ReflectionGateReceipt
) -> tuple[ReflectionStatus, ResultLoss, str]:
    failure = gate.failures[0]
    if failure == "writer_unavailable":
        return "unavailable", "reflection_writer_unavailable", REFLECTION_UNAVAILABLE_MARKER
    if failure == "writer_contract_invalid":
        return "degraded", "reflection_writer_contract_invalid", REFLECTION_DEGRADED_MARKER
    if failure == "ability_binding_failed":
        return "degraded", "reflection_ability_binding_failed", REFLECTION_DEGRADED_MARKER
    return "degraded", "reflection_gate_failed", REFLECTION_DEGRADED_MARKER


class ReflectionResult(_StrictModel):
    status: ReflectionStatus
    prompt: ShiftedQuestionPrompt | None
    known_losses: tuple[ResultLoss, ...]
    marker: NonBlankStr | None
    authority: ReflectionRequest
    candidate_snapshot: ReflectionWriterCandidate | None
    authority_digest: Sha256Digest
    prework_digest: Sha256Digest
    candidate_digest: Sha256Digest
    gate: ReflectionGateReceipt

    @model_validator(mode="after")
    def _anti_forgery_replay(self) -> ReflectionResult:
        if type(self.authority) is not ReflectionRequest:
            raise ValueError("result authority must be an exact ReflectionRequest")
        if (
            self.candidate_snapshot is not None
            and type(self.candidate_snapshot) is not ReflectionWriterCandidate
        ):
            raise ValueError("result candidate must be an exact ReflectionWriterCandidate")
        if type(self.gate) is not ReflectionGateReceipt:
            raise ValueError("result gate must be an exact ReflectionGateReceipt")
        if self.prompt is not None and type(self.prompt) is not ShiftedQuestionPrompt:
            raise ValueError("result prompt must be an exact ShiftedQuestionPrompt")
        authority = ReflectionRequest.model_validate(
            _trusted_model_dump(self.authority, ReflectionRequest), strict=True
        )
        candidate = (
            ReflectionWriterCandidate.model_validate(
                _trusted_model_dump(self.candidate_snapshot, ReflectionWriterCandidate),
                strict=True,
            )
            if self.candidate_snapshot is not None
            else None
        )
        gate = ReflectionGateReceipt.model_validate(
            _trusted_model_dump(self.gate, ReflectionGateReceipt), strict=True
        )
        prompt = (
            ShiftedQuestionPrompt.model_validate(
                _trusted_model_dump(self.prompt, ShiftedQuestionPrompt), strict=True
            )
            if self.prompt is not None
            else None
        )
        object.__setattr__(self, "authority", authority)
        object.__setattr__(self, "candidate_snapshot", candidate)
        object.__setattr__(self, "gate", gate)
        object.__setattr__(self, "prompt", prompt)
        disposition = _pre_gate(authority)
        if self.authority_digest != reflection_authority_digest(authority):
            raise ValueError("result authority digest must be recomputed")
        if self.prework_digest != prework_callback_digest(authority.prework):
            raise ValueError("result pre-work digest must be recomputed")
        if disposition != "eligible":
            if candidate is not None:
                raise ValueError("pre-gate result cannot forge a candidate")
            expected_gate = _gate(authority, None)
            status, loss, marker = _PRE_GATE_RESULT[disposition]
            if (
                gate != expected_gate
                or self.candidate_digest != NO_CANDIDATE_DIGEST
                or self.status != status
                or prompt is not None
                or self.known_losses != (loss,)
                or self.marker != marker
            ):
                raise ValueError("pre-gate result must equal deterministic replay")
            return self
        if candidate is None:
            raise ValueError("eligible execution requires a candidate snapshot")
        expected_gate = _gate(authority, candidate)
        if self.candidate_digest != reflection_candidate_digest(candidate) or gate != expected_gate:
            raise ValueError("candidate digest and gate must equal deterministic replay")
        if expected_gate.status == "pass":
            expected_prompt = ShiftedQuestionPrompt(
                ability_cues=_ability_cues(authority, candidate)
            )
            if (
                self.status != "authored"
                or prompt != expected_prompt
                or self.known_losses
                or self.marker is not None
            ):
                raise ValueError("authored result must equal deterministic composition")
        else:
            status, loss, marker = _candidate_result(candidate, expected_gate)
            if (
                self.status != status
                or prompt is not None
                or self.known_losses != (loss,)
                or self.marker != marker
            ):
                raise ValueError("non-authored result must equal deterministic disposition")
        return self


def offline_closing_reflection_writer(request: ReflectionRequest) -> ReflectionWriterCandidate:
    del request
    return ReflectionWriterCandidate(
        status="unavailable",
        ability_focuses=(),
        known_losses=("reflection_writer_unavailable",),
        marker=REFLECTION_UNAVAILABLE_MARKER,
    )


def _invalid_writer_candidate() -> ReflectionWriterCandidate:
    return ReflectionWriterCandidate(
        status="degraded",
        ability_focuses=(),
        known_losses=("reflection_writer_contract_invalid",),
        marker=REFLECTION_DEGRADED_MARKER,
    )


def _dispose_rejected_closed_loop_task(task: asyncio.Task[object]) -> None:
    """Dispose a Task only after its closed loop relinquishes lifecycle ownership."""
    coroutine_closed = False
    try:
        coroutine = asyncio.Task.get_coro(task)
        if isinstance(coroutine, CoroutineType):
            CoroutineType.close(coroutine)
            coroutine_closed = inspect.getcoroutinestate(coroutine) == inspect.CORO_CLOSED
    except BaseException:
        pass
    terminal = False
    with suppress(BaseException):
        terminal = asyncio.Future.done(task) or asyncio.Future.cancelled(task)
    if terminal or coroutine_closed:
        with suppress(BaseException):
            asyncio.Task._log_destroy_pending.__set__(task, False)


def _trusted_task_waiter(task: asyncio.Task[object]) -> object | None:
    """Read Task-owned waiter state without consulting instance attributes."""
    with suppress(BaseException):
        return asyncio.Task._fut_waiter.__get__(task, asyncio.Task)
    return None


def _waiter_uses_base_future_cancel(waiter: asyncio.Future[object]) -> bool:
    """Return whether Task.cancel can reach only the trusted Future base method."""
    try:
        if inspect.getattr_static(type(waiter), "cancel") is not asyncio.Future.cancel:
            return False
        try:
            instance_state = object.__getattribute__(waiter, "__dict__")
        except AttributeError:
            pass
        else:
            if type(instance_state) is not dict or "cancel" in instance_state:
                return False
        resolved_cancel = object.__getattribute__(waiter, "cancel")
        trusted_cancel = asyncio.Future.cancel.__get__(waiter, type(waiter))
        return type(resolved_cancel) is type(trusted_cancel) and (
            object.__getattribute__(resolved_cancel, "__self__") is waiter
        )
    except BaseException:
        return False


def _cancel_future_through_trusted_base(future: asyncio.Future[object]) -> None:
    """Cancel a Future without consulting instance cancellation hooks."""
    with suppress(BaseException):
        asyncio.Future.cancel(future)


def _schedule_future_cancellation_on_owning_thread(
    future: asyncio.Future[object],
) -> bool:
    """Marshal standalone Future cleanup to a running foreign loop."""
    try:
        loop = asyncio.Future.get_loop(future)
        if asyncio.BaseEventLoop.is_closed(loop) or not asyncio.BaseEventLoop.is_running(loop):
            return False
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        if current_loop is loop:
            return False
        asyncio.BaseEventLoop.call_soon_threadsafe(
            loop, _cancel_future_through_trusted_base, future
        )
        return True
    except BaseException:
        return False


def _schedule_initial_cancellation_on_owning_thread(
    task: asyncio.Task[object],
) -> bool:
    """Marshal initial cleanup when a running loop belongs to another thread."""
    try:
        loop = asyncio.Task.get_loop(task)
        if asyncio.BaseEventLoop.is_closed(loop) or not asyncio.BaseEventLoop.is_running(loop):
            return False
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        if current_loop is loop:
            return False
        asyncio.BaseEventLoop.call_soon_threadsafe(loop, _request_trusted_task_cancellation, task)
        return True
    except BaseException:
        return False


def _schedule_trusted_task_cancellation_retry(
    task: asyncio.Task[object], remaining_turns: int = 4
) -> None:
    """Ask an open owning loop to retry after the Task's already queued wakeup."""
    if remaining_turns <= 0:
        return
    done = False
    with suppress(BaseException):
        done = asyncio.Future.done(task)
    if done:
        return
    with suppress(BaseException):
        loop = asyncio.Task.get_loop(task)
        if not asyncio.BaseEventLoop.is_closed(loop):
            asyncio.BaseEventLoop.call_soon_threadsafe(
                loop, _retry_trusted_task_cancellation, task, remaining_turns
            )


def _retry_trusted_task_cancellation(task: asyncio.Task[object], remaining_turns: int) -> None:
    """Repeat cancellation at a later Task suspension without running hostile hooks."""
    try:
        if asyncio.Future.done(task):
            return
        waiter = _trusted_task_waiter(task)
        if isinstance(waiter, asyncio.Task):
            _schedule_trusted_task_cancellation_retry(task, remaining_turns - 1)
        elif isinstance(waiter, asyncio.Future):
            asyncio.Future.cancel(waiter)
            if _waiter_uses_base_future_cancel(waiter):
                asyncio.Task.cancel(task)
            _schedule_trusted_task_cancellation_retry(task, remaining_turns - 1)
        else:
            asyncio.Task.cancel(task)
            _schedule_trusted_task_cancellation_retry(task, remaining_turns - 1)
    except BaseException:
        pass


def _request_trusted_task_cancellation(
    task: asyncio.Task[object],
    seen: set[int] | None = None,
    *,
    schedule_retry: bool = True,
) -> None:
    """Cancel a Task waiter chain without dispatching instance overrides."""
    if schedule_retry and _schedule_initial_cancellation_on_owning_thread(task):
        return
    if seen is None:
        seen = set()
    identity = id(task)
    if identity in seen:
        return
    seen.add(identity)

    waiter = _trusted_task_waiter(task)

    if isinstance(waiter, asyncio.Task):
        _request_trusted_task_cancellation(waiter, seen, schedule_retry=schedule_retry)
    elif isinstance(waiter, asyncio.Future):
        with suppress(BaseException):
            asyncio.Future.cancel(waiter)
        if _waiter_uses_base_future_cancel(waiter):
            with suppress(BaseException):
                asyncio.Task.cancel(task)
    else:
        with suppress(BaseException):
            asyncio.Task.cancel(task)

    loop_is_closed = False
    with suppress(BaseException):
        loop = asyncio.Task.get_loop(task)
        loop_is_closed = asyncio.BaseEventLoop.is_closed(loop)
    if loop_is_closed:
        done = False
        with suppress(BaseException):
            done = asyncio.Future.done(task)
        if not done:
            _dispose_rejected_closed_loop_task(task)
    elif schedule_retry:
        _schedule_trusted_task_cancellation_retry(task)


def _cleanup_rejected_awaitable(returned: object) -> None:
    """Best-effort cleanup through trusted runtime methods; never execute awaitables."""
    try:
        if isinstance(returned, CoroutineType):
            CoroutineType.close(returned)
        elif isinstance(returned, asyncio.Task):
            # An open loop owns each scheduled Task step even while currently idle.
            # Cancel the waiter chain through trusted base methods and let that loop
            # resume the outer Tasks; only a closed loop permits direct disposal.
            _request_trusted_task_cancellation(returned)
        elif isinstance(
            returned, asyncio.Future
        ) and not _schedule_future_cancellation_on_owning_thread(returned):
            _cancel_future_through_trusted_base(returned)
    except BaseException:
        pass


def compose_closing_reflection(
    request: ReflectionRequest,
    writer: ClosingReflectionWriter | Callable[[ReflectionRequest], ReflectionWriterCandidate],
) -> ReflectionResult:
    """Pre-gate authority and invoke the bounded writer at most once."""
    if type(request) is not ReflectionRequest:
        raise TypeError("request must be a ReflectionRequest")
    request = ReflectionRequest.model_validate(
        _trusted_model_dump(request, ReflectionRequest), strict=True
    )
    disposition = _pre_gate(request)
    if disposition != "eligible":
        gate = _gate(request, None)
        status, loss, marker = _PRE_GATE_RESULT[disposition]
        return ReflectionResult(
            status=status,
            prompt=None,
            known_losses=(loss,),
            marker=marker,
            authority=request,
            candidate_snapshot=None,
            authority_digest=gate.authority_digest,
            prework_digest=gate.prework_digest,
            candidate_digest=gate.candidate_digest,
            gate=gate,
        )
    if not callable(writer):
        candidate = _invalid_writer_candidate()
    else:
        returned = writer(request)  # Pinned policy: callable writer exceptions propagate.
        _cleanup_rejected_awaitable(returned)
        if type(returned) is not ReflectionWriterCandidate:
            candidate = _invalid_writer_candidate()
        else:
            try:
                candidate = ReflectionWriterCandidate.model_validate(
                    _trusted_model_dump(returned, ReflectionWriterCandidate), strict=True
                )
            except (ValidationError, ValueError, TypeError):
                candidate = _invalid_writer_candidate()
    gate = _gate(request, candidate)
    if gate.status == "pass":
        prompt = ShiftedQuestionPrompt(ability_cues=_ability_cues(request, candidate))
        return ReflectionResult(
            status="authored",
            prompt=prompt,
            known_losses=(),
            marker=None,
            authority=request,
            candidate_snapshot=candidate,
            authority_digest=gate.authority_digest,
            prework_digest=gate.prework_digest,
            candidate_digest=gate.candidate_digest,
            gate=gate,
        )
    status, loss, marker = _candidate_result(candidate, gate)
    return ReflectionResult(
        status=status,
        prompt=None,
        known_losses=(loss,),
        marker=marker,
        authority=request,
        candidate_snapshot=candidate,
        authority_digest=gate.authority_digest,
        prework_digest=gate.prework_digest,
        candidate_digest=gate.candidate_digest,
        gate=gate,
    )


__all__ = [
    "CALLBACK_CLAUSE",
    "CAPABILITY_CLAUSE",
    "MOVE_CLAUSE",
    "REFLECTION_DEGRADED_MARKER",
    "REFLECTION_UNAVAILABLE_MARKER",
    "ClosingReflectionWriter",
    "ReflectionAbilityCue",
    "ReflectionAbilityFocus",
    "ReflectionGateReceipt",
    "ReflectionRequest",
    "ReflectionResult",
    "ReflectionWriterCandidate",
    "ShiftedQuestionClauses",
    "ShiftedQuestionPrompt",
    "compose_closing_reflection",
    "offline_closing_reflection_writer",
    "prework_callback_digest",
    "reflection_authority_digest",
    "reflection_candidate_digest",
]
