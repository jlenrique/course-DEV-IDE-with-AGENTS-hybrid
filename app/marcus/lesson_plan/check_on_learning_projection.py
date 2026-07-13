"""Pure Promise-bound retrieval checks with source-grounded answer keys.

The module owns only the Story 37.3 contract/writer/gate seam.  It performs no
runtime, filesystem, research, provider, persistence, or rendering work.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Callable
from typing import Annotated, Literal, Protocol

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator

from app.marcus.lesson_plan.promise_projection import PromiseProjectionResult

CheckStatus = Literal["authored", "degraded", "unavailable"]
GateStatus = Literal["pass", "fail"]
PreGateDisposition = Literal[
    "eligible",
    "promise_unavailable",
    "promise_degraded",
    "source_unavailable",
    "missing_ability_proof",
]
WriterLoss = Literal["check_writer_unavailable", "check_execution_failed"]
ResultLoss = Literal[
    "check_writer_unavailable",
    "check_execution_failed",
    "check_source_unavailable",
    "check_promise_authority_unavailable",
    "check_promise_authority_degraded",
    "check_missing_ability_proof",
    "check_reference_validation_failed",
    "check_gate_failed",
]
GateFailure = Literal[
    "promise_authority_unavailable",
    "promise_authority_degraded",
    "source_authority_unavailable",
    "missing_ability_proof",
    "ability_order_mismatch",
    "answer_claim_composition_failed",
    "retrieval_posture_failed",
    "answer_leakage_failed",
    "unusable_answer_failed",
    "source_trace_mismatch",
    "ability_permission_mismatch",
    "numeric_fidelity_failed",
    "negation_fidelity_failed",
    "unknown_claim_reference",
    "unknown_source_reference",
    "unknown_ability_reference",
]

CHECK_UNAVAILABLE_MARKER = "check_on_learning_unavailable"
CHECK_DEGRADED_MARKER = "check_on_learning_degraded"
OPERATOR_SEMANTIC_WARNING = (
    "full_semantic_answer_correctness_ability_relevance_and_subtle_leakage_"
    "require_operator_spot_check"
)
_UNICODE_BULLETS = frozenset("•‣⁃◦∙▪▫●○")


def _non_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("value must contain non-whitespace text")
    return value


def _single_line(value: str) -> str:
    if any(
        unicodedata.category(character).startswith("C")
        or unicodedata.category(character) in {"Zl", "Zp"}
        for character in value
    ):
        raise ValueError("value cannot contain Unicode control or format characters")
    return value


def _trimmed(value: str) -> str:
    if value != value.strip():
        raise ValueError("stable IDs and refs cannot have surrounding whitespace")
    if any(character in _UNICODE_BULLETS for character in value):
        raise ValueError("stable IDs and refs cannot contain list bullets")
    return value


_RAW_HTML_TAG = re.compile(r"</?[A-Za-z][^<>]*>|<!--|<![A-Za-z\[]|<\?")


def _learner_safe(value: str) -> str:
    _single_line(value)
    if _RAW_HTML_TAG.search(value):
        raise ValueError("learner-facing text cannot contain raw HTML tags")
    return value


def _canonical_digest(value: str) -> str:
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError("value must be a canonical sha256 digest")
    return value


NonBlankStr = Annotated[str, AfterValidator(_non_blank)]
NonBlankLine = Annotated[str, AfterValidator(_non_blank), AfterValidator(_single_line)]
LearnerText = Annotated[str, AfterValidator(_non_blank), AfterValidator(_learner_safe)]
StableRef = Annotated[
    str, AfterValidator(_non_blank), AfterValidator(_single_line), AfterValidator(_trimmed)
]
Sha256Digest = Annotated[str, AfterValidator(_canonical_digest)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        validate_default=True,
    )


def _duplicates(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return tuple(duplicates)


def _require_unique(values: tuple[str, ...], label: str) -> None:
    duplicates = _duplicates(values)
    if duplicates:
        raise ValueError(f"duplicate {label}: {', '.join(duplicates)}")


class CheckSourceSpan(_StrictModel):
    span_id: StableRef
    text: NonBlankStr
    source_ref: StableRef


class CheckSourceClaim(_StrictModel):
    claim_id: StableRef
    text: NonBlankStr
    source_span_refs: tuple[StableRef, ...]
    ability_refs: tuple[StableRef, ...]

    @model_validator(mode="after")
    def _closed_refs(self) -> CheckSourceClaim:
        if not self.source_span_refs or not self.ability_refs:
            raise ValueError("source claim requires source-span and ability authority")
        _require_unique(self.source_span_refs, "source span refs")
        _require_unique(self.ability_refs, "ability refs")
        return self


class CheckAnswerClaim(_StrictModel):
    answer_claim_id: StableRef
    text: LearnerText
    source_claim_ref: StableRef
    source_span_refs: tuple[StableRef, ...]

    @model_validator(mode="after")
    def _closed_trace(self) -> CheckAnswerClaim:
        if not self.source_span_refs:
            raise ValueError("answer claim requires source-span traces")
        _require_unique(self.source_span_refs, "answer source span refs")
        return self


class RetrievalCheckItem(_StrictModel):
    item_id: StableRef
    ability_id: StableRef
    posture: Literal["free_response_from_memory"] = "free_response_from_memory"
    prompt: LearnerText
    expected_answer: NonBlankStr
    answer_claims: tuple[CheckAnswerClaim, ...]

    @model_validator(mode="after")
    def _has_atomic_answer(self) -> RetrievalCheckItem:
        if not self.answer_claims:
            raise ValueError("retrieval item requires atomic answer claims")
        validated_claims = tuple(
            CheckAnswerClaim.model_validate(claim.model_dump(mode="python"), strict=True)
            for claim in self.answer_claims
        )
        _require_unique(
            tuple(claim.answer_claim_id for claim in validated_claims),
            "answer claim IDs within item",
        )
        return self


class CheckOnLearningRequest(_StrictModel):
    lesson_ref: StableRef
    promise: PromiseProjectionResult
    quantity_unit_tokens: tuple[NonBlankLine, ...]
    source_spans: tuple[CheckSourceSpan, ...]
    source_claims: tuple[CheckSourceClaim, ...]

    @model_validator(mode="after")
    def _closed_authority(self) -> CheckOnLearningRequest:
        # Nested model instances can have been created via model_construct().
        promise = PromiseProjectionResult.model_validate(
            self.promise.model_dump(mode="python"), strict=True
        )
        projection = promise.projection
        vows = projection.vows
        ability_ids = tuple(vow.objective_id for vow in vows)
        if projection.status == "authored":
            if promise.gate_receipt.failures:
                raise ValueError("authored Promise authority requires an empty upstream gate")
            if not vows:
                raise ValueError("authored Promise authority requires vows")
            _require_unique(ability_ids, "Promise ability IDs")
            try:
                for ability in ability_ids:
                    _trimmed(_single_line(_non_blank(ability)))
                for ref in promise.authority_refs:
                    _trimmed(_single_line(_non_blank(ref)))
            except ValueError as exc:
                raise ValueError("Promise authority requires stable refs") from exc
            if len(promise.authority_refs) != len(vows):
                raise ValueError("Promise authority refs must align 1:1 with vows")
            _require_unique(promise.authority_refs, "Promise authority refs")
        else:
            if vows:
                raise ValueError("non-authored Promise authority cannot expose vows")
            if promise.gate_receipt.failures != projection.known_losses:
                raise ValueError("non-authored Promise losses must equal its upstream gate")
            if promise.authority_refs:
                raise ValueError("non-authored Promise authority cannot retain authority refs")

        validated_spans = tuple(
            CheckSourceSpan.model_validate(span.model_dump(mode="python"), strict=True)
            for span in self.source_spans
        )
        validated_claims = tuple(
            CheckSourceClaim.model_validate(claim.model_dump(mode="python"), strict=True)
            for claim in self.source_claims
        )
        span_ids = tuple(span.span_id for span in validated_spans)
        claim_ids = tuple(claim.claim_id for claim in validated_claims)
        for token in self.quantity_unit_tokens:
            if token != token.strip():
                raise ValueError("quantity unit tokens cannot have surrounding whitespace")
        _require_unique(self.quantity_unit_tokens, "quantity unit tokens")
        _require_unique(span_ids, "source span IDs")
        _require_unique(tuple(span.source_ref for span in validated_spans), "source refs")
        _require_unique(claim_ids, "source claim IDs")
        span_set = set(span_ids)
        ability_set = set(ability_ids)
        for claim in validated_claims:
            unknown_spans = tuple(ref for ref in claim.source_span_refs if ref not in span_set)
            unknown_abilities = tuple(ref for ref in claim.ability_refs if ref not in ability_set)
            if unknown_spans:
                raise ValueError(
                    f"source claim references unknown span: {', '.join(unknown_spans)}"
                )
            if unknown_abilities:
                raise ValueError(
                    f"source claim references unknown ability: {', '.join(unknown_abilities)}"
                )
        return self


class CheckOnLearningWriterCandidate(_StrictModel):
    status: CheckStatus
    items: tuple[RetrievalCheckItem, ...]
    known_losses: tuple[WriterLoss, ...]
    marker: NonBlankLine | None

    @model_validator(mode="after")
    def _honest_candidate(self) -> CheckOnLearningWriterCandidate:
        if self.status == "authored":
            if not self.items or self.known_losses or self.marker is not None:
                raise ValueError("authored candidate requires items and no loss state")
            validated_items = tuple(
                RetrievalCheckItem.model_validate(item.model_dump(mode="python"), strict=True)
                for item in self.items
            )
            _require_unique(tuple(item.item_id for item in validated_items), "item IDs")
            _require_unique(
                tuple(
                    claim.answer_claim_id
                    for item in validated_items
                    for claim in item.answer_claims
                ),
                "answer claim IDs",
            )
        else:
            if self.items or len(self.known_losses) != 1 or self.marker is None:
                raise ValueError("non-authored candidate requires one loss and empty payload")
            expected_loss: WriterLoss = (
                "check_writer_unavailable"
                if self.status == "unavailable"
                else "check_execution_failed"
            )
            if self.known_losses != (expected_loss,):
                raise ValueError("candidate status requires its canonical typed loss")
            expected = (
                CHECK_UNAVAILABLE_MARKER if self.status == "unavailable" else CHECK_DEGRADED_MARKER
            )
            if self.marker != expected:
                raise ValueError("candidate status requires its canonical marker")
        return self


class CheckOnLearningWriter(Protocol):
    """Injected semantic writer returning an untrusted candidate."""

    def __call__(self, request: CheckOnLearningRequest) -> CheckOnLearningWriterCandidate: ...


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


NO_CANDIDATE_DIGEST = _digest(None)


def check_authority_digest(request: CheckOnLearningRequest) -> str:
    validated = CheckOnLearningRequest.model_validate(
        request.model_dump(mode="python"), strict=True
    )
    return _digest(validated.model_dump(mode="json"))


def check_candidate_digest(candidate: CheckOnLearningWriterCandidate | None) -> str:
    if candidate is None:
        return NO_CANDIDATE_DIGEST
    validated = CheckOnLearningWriterCandidate.model_validate(
        candidate.model_dump(mode="python"), strict=True
    )
    return _digest(validated.model_dump(mode="json"))


class CheckGateReceipt(_StrictModel):
    authority_digest: Sha256Digest
    candidate_digest: Sha256Digest
    pre_gate_disposition: PreGateDisposition
    status: GateStatus
    declared_ability_ids: tuple[StableRef, ...]
    declared_claim_ids: tuple[StableRef, ...]
    declared_span_ids: tuple[StableRef, ...]
    covered_ability_ids: tuple[StableRef, ...]
    missing_ability_ids: tuple[StableRef, ...]
    unknown_claim_refs: tuple[StableRef, ...]
    unknown_source_refs: tuple[StableRef, ...]
    unknown_ability_refs: tuple[StableRef, ...]
    failures: tuple[GateFailure, ...]
    operator_warnings: tuple[NonBlankLine, ...] = (OPERATOR_SEMANTIC_WARNING,)

    @model_validator(mode="after")
    def _reconciled_diagnostics(self) -> CheckGateReceipt:
        if (self.status == "pass") == bool(self.failures):
            raise ValueError("gate status must reconcile with failures")
        for values, label in (
            (self.declared_ability_ids, "declared ability IDs"),
            (self.declared_claim_ids, "declared claim IDs"),
            (self.declared_span_ids, "declared span IDs"),
            (self.covered_ability_ids, "covered ability IDs"),
            (self.missing_ability_ids, "missing ability IDs"),
            (self.unknown_claim_refs, "unknown claim refs"),
            (self.unknown_source_refs, "unknown source refs"),
            (self.unknown_ability_refs, "unknown ability refs"),
            (self.failures, "gate failures"),
        ):
            _require_unique(values, label)
        covered = set(self.covered_ability_ids)
        missing = set(self.missing_ability_ids)
        declared = set(self.declared_ability_ids)
        if covered & missing or covered | missing != declared:
            raise ValueError("covered/missing abilities must exactly partition authority")
        if self.covered_ability_ids != tuple(
            item for item in self.declared_ability_ids if item in covered
        ) or self.missing_ability_ids != tuple(
            item for item in self.declared_ability_ids if item in missing
        ):
            raise ValueError("ability diagnostics must preserve Promise order")
        if set(self.unknown_claim_refs) & set(self.declared_claim_ids):
            raise ValueError("unknown claim diagnostics cannot name declared claims")
        if set(self.unknown_source_refs) & set(self.declared_span_ids):
            raise ValueError("unknown span diagnostics cannot name declared spans")
        if set(self.unknown_ability_refs) & declared:
            raise ValueError("unknown ability diagnostics cannot name declared abilities")
        if self.pre_gate_disposition == "eligible":
            if self.candidate_digest == NO_CANDIDATE_DIGEST:
                raise ValueError("eligible gate requires a candidate digest")
            if (
                not self.declared_ability_ids
                or not self.declared_claim_ids
                or not self.declared_span_ids
            ):
                raise ValueError("eligible gate requires complete declared authority inventories")
        elif self.candidate_digest != NO_CANDIDATE_DIGEST:
            raise ValueError("pre-gate disposition requires no-candidate digest")
        pre_gate_failure = {
            "promise_unavailable": "promise_authority_unavailable",
            "promise_degraded": "promise_authority_degraded",
            "source_unavailable": "source_authority_unavailable",
            "missing_ability_proof": "missing_ability_proof",
        }
        if self.pre_gate_disposition != "eligible" and self.failures != (
            pre_gate_failure[self.pre_gate_disposition],
        ):
            raise ValueError("pre-gate disposition requires its canonical failure")
        diagnostic_failures = (
            (self.unknown_claim_refs, "unknown_claim_reference", "claim"),
            (self.unknown_source_refs, "unknown_source_reference", "source"),
            (self.unknown_ability_refs, "unknown_ability_reference", "ability"),
        )
        for values, failure, label in diagnostic_failures:
            if bool(values) != (failure in self.failures):
                raise ValueError(f"unknown {label} diagnostics must reconcile with failures")
        if self.pre_gate_disposition in {"eligible", "missing_ability_proof"} and bool(
            self.missing_ability_ids
        ) != ("missing_ability_proof" in self.failures):
            raise ValueError("missing ability diagnostics must reconcile with failures")
        if self.status == "pass" and (
            self.pre_gate_disposition != "eligible"
            or self.missing_ability_ids
            or self.unknown_claim_refs
            or self.unknown_source_refs
            or self.unknown_ability_refs
        ):
            raise ValueError("passing gate requires eligible, complete, known authority")
        if self.operator_warnings != (OPERATOR_SEMANTIC_WARNING,):
            raise ValueError("gate requires the canonical operator warning")
        return self


_NUMBER_WORDS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
    "hundred",
    "thousand",
    "million",
    "billion",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "eleventh",
    "twelfth",
    "thirteenth",
    "fourteenth",
    "fifteenth",
    "sixteenth",
    "seventeenth",
    "eighteenth",
    "nineteenth",
    "twentieth",
    "thirtieth",
    "fortieth",
    "fiftieth",
    "sixtieth",
    "seventieth",
    "eightieth",
    "ninetieth",
    "hundredth",
    "thousandth",
    "millionth",
    "billionth",
    "dozen",
    "half",
    "quarter",
    "percent",
)
_NUMBER_WORD_ALTERNATION = "|".join(_NUMBER_WORDS)
_SIGN = r"[+\-−]?"
_DECIMAL = r"(?:\d+(?:\.\d+)?|\.\d+)"
_SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"
_SCIENTIFIC_EXPONENT = rf"(?:[eE]{_SIGN}\d+|\s*[×x]\s*10(?:\s*\^\s*{_SIGN}\d+|[{_SUPERSCRIPTS}]+))?"
_DIGIT_VALUE = rf"{_SIGN}{_DECIMAL}{_SCIENTIFIC_EXPONENT}(?i:st|nd|rd|th)?"
_WORD_NUMBER = (
    rf"\b(?:{_NUMBER_WORD_ALTERNATION})"
    rf"(?:(?:[\s-]+and)?[\s-]+(?:{_NUMBER_WORD_ALTERNATION}))*\b"
)
_WORD_PATTERN = re.compile(r"\b[\w'-]+\b", flags=re.UNICODE)
_TENS_NUMBER_WORDS = {
    "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"
}
_ONES_NUMBER_WORDS = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"
}
_ONES_ORDINAL_WORDS = {
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
}
_FRACTION_SCALE_NUMBER_WORDS = {
    "hundred",
    "thousand",
    "million",
    "billion",
    "hundredth",
    "thousandth",
    "millionth",
    "billionth",
    "dozen",
    "half",
    "quarter",
    "percent",
}
_NEGATIONS = {"no", "not", "never", "without", "neither", "nor"}
_FREE_RESPONSE_GRAMMAR = re.compile(
    r"^(?:from\s+memory,\s+)?(?:"
    r"(?:what|how|why)\b.+\?|"
    r"(?:explain|describe|identify|name|state|summarize|outline|map|"
    r"distinguish|compare)\b.+)$",
    flags=re.IGNORECASE,
)
_SUPPLIED_ALTERNATIVES = re.compile(
    r"^(?:from\s+memory,\s+)?(?:"
    r"(?:compare|what|why)\b.*\bor\b|explain\s+whether\b.*\bor\b|"
    r"(?:compare|explain|what|why)\b.*\bbetween\b.+\band\b)",
    flags=re.IGNORECASE,
)


def _has_supplied_alternatives(prompt: str) -> bool:
    folded = unicodedata.normalize("NFKC", prompt).casefold()
    folded = re.sub(
        rf"\b(?:\d+|(?:{_NUMBER_WORD_ALTERNATION})"
        rf"(?:(?:[\s-]+and)?[\s-]+(?:{_NUMBER_WORD_ALTERNATION}))*)"
        r"\s+or\s+more\b",
        "",
        folded,
    )
    if re.search(r"\bversus\b|\bvs\.?\b|\|", folded):
        return True
    if re.search(r"\b(?:yes|no|true|false)\s*(?:or|/)\s*(?:yes|no|true|false)\b", folded):
        return True
    if re.search(r"\bwhether\b.*\bor\b", folded):
        return True
    if re.search(r"\b[\w-]+\s*/\s*[\w-]+\b", folded):
        return True
    if re.search(r"\bor\b", folded):
        return True
    return bool(_SUPPLIED_ALTERNATIVES.search(folded))
_IMPERATIVE_PREAMBLE = (
    r"^\s*(?:(?:before|after)\b[^,]{0,80},\s*|for\s+this\s+check,\s*)?"
    r"(?:(?:please|now|first|next|carefully|briefly)\s*,?\s*)*"
)
_SOURCE_OBJECT = (
    r"(?:(?:the|this|that|these|those|your|my|our|provided|original)\s+)*"
    r"(?:text|passage|source(?:\s+material)?|material|notes?|transcript|worked\s+example)"
)
_CHOICE_OR_REREAD = re.compile(
    r"\b(?:multiple[- ]choice|which of the following|all of the above|"
    r"true\s*(?:or|/)\s*false)\b|^\s*hint\s*(?::|-|=)|"
    + _IMPERATIVE_PREAMBLE
    + r"(?:"
    r"(?:consult|review|reread|re-read|read|look\s+back\s+at|go\s+back\s+to|"
    r"refer(?:\s+back)?\s+to)\s+(?:carefully\s+|briefly\s+)?"
    + _SOURCE_OBJECT
    + r"|(?:listen\s+(?:carefully\s+)?to|study)\s+"
    + _SOURCE_OBJECT
    + r"|use\s+"
    + _SOURCE_OBJECT
    + r"\s+to\s+answer|follow\s+"
    + _SOURCE_OBJECT
    + r"|decide\s+(?:carefully\s+|briefly\s+)?between\b)"
    r"|^\s*according\s+to\s+(?:the\s+)?transcript\b",
    flags=re.IGNORECASE,
)
_EMBEDDED_SOURCE_CONSULT = re.compile(
    r"\b(?:using|reviewing|consulting|referencing|according\s+to|"
    r"referring\s+to|based\s+on|after\s+(?:reading|reviewing)|"
    r"(?:by|while|after)\s+(?:reading|reviewing|consulting|studying|"
    r"listening\s+to)|while\s+referring\s+to|by\s+consulting|"
    r"with(?:\s+reference\s+to)?|drawing\s+from|guided\s+by|"
    r"as\s+shown\s+in|from)\s+"
    + _SOURCE_OBJECT,
    flags=re.IGNORECASE,
)
_CHOICE_SCAFFOLD = re.compile(
    r"\b(?:(?:yes\s*(?:or|/)\s*no|no\s*(?:or|/)\s*yes)|"
    r"\d+\s*(?:or|/)\s*\d+|"
    r"between\s+\d+(?:\.\d+)?\s+and\s+\d+(?:\.\d+)?|"
    r"which\s+(?:one\s+)?is\s+correct|"
    r"(?:choose|select)\s+(?:(?:an?|the|one)\s+)?(?:best\s+|correct\s+)?"
    r"(?:option|answer|response)|pick\s+which\s+(?:statement|option|answer|response)|"
    r"\d+(?:\s*,\s*\d+)+(?:\s*,?\s*or\s*\d+)?|"
    r"(?:if|whether)\b(?=.*\byes\b)(?=.*\bno\b).*)\b|"
    r"^\s*(?:is|are|was|were|does|do|did|can|could|should|would)\b"
    r".*(?:\bor\b|\bbetween\b.*\band\b)|"
    r"^\s*decide\s+between\b|^\s*pick\s+(?:the\s+)?best\b|"
    r"^\s*(?:listen\s+to|study)\s+(?:the\s+)?(?:transcript|worked\s+example)\b",
    flags=re.IGNORECASE,
)
_DISCLOSURE_MARKER = re.compile(
    r"\b(?:hint|answer(?:[- ]key|(?![- ]key))|solution|response|key|transcript)"
    r"\s*(?::|-|=)|"
    r"(?:^|[,;:—-]\s*|[.!?]\s+|\b(?:and|but)\s+)"
    r"(?:the\s+)?(?:correct\s+)?"
    r"(?:hint|answer(?:[- ]key|(?![- ]key))|solution|response|key|transcript)"
    r"\s+is\b",
    flags=re.IGNORECASE,
)
_DEIXIS = re.compile(
    r"\b(?:this|that|the)\s+(?:slide|deck|screen)\b|"
    r"\b(?:slide|deck)\s+(?:above|below)\b|"
    r"\b(?:on|in|from)\s+(?:the\s+)?(?:slide|deck|screen)\b",
    flags=re.IGNORECASE,
)
_ENUMERATOR_CORE = r"(?:\d+|[A-Za-z]|[IVXLCDMivxlcdm]{2,})"
_ENUMERATOR_LABEL = (
    rf"(?:\(\s*{_ENUMERATOR_CORE}\s*\)|"
    rf"{_ENUMERATOR_CORE}[.):]|{_ENUMERATOR_CORE}\s+-)"
)
_ENUMERATED_CHOICE = re.compile(
    r"\b(?:choose|select|pick)\s+(?:an?|the|one)\s+(?:option|answer|response)\b|"
    rf"(?:^|\s){_ENUMERATOR_LABEL}\s+.+(?:^|\s){_ENUMERATOR_LABEL}\s+"
)
_UNICODE_ENUMERATOR = re.compile(r"[\u2460-\u2473•‣⁃◦∙▪▫●○]")


def _has_unicode_enumeration(prompt: str) -> bool:
    paired_markers = 0
    for character in prompt:
        name = unicodedata.name(character, "")
        if any(
            marker in name
            for marker in (
                "CIRCLED",
                "PARENTHESIZED",
                "SQUARED LATIN",
                "ENCLOSING KEYCAP",
            )
        ):
            return True
        if "ARROW" in name or "BULLET" in name or character in _UNICODE_BULLETS:
            paired_markers += 1
    return paired_markers >= 2


_STANDALONE_SYMBOL = re.compile(r"(?<!\S)([^\w\s])(?=\s)")
_MATH_OPERATOR_SYMBOLS = frozenset("*+−-×÷/=")
_SIMPLE_MATH_OPERAND = re.compile(r"(?:[A-Za-z]|\d+(?:\.\d+)?)")


def _has_repeated_symbol_enumeration(prompt: str) -> bool:
    marker_counts: dict[str, int] = {}
    for match in _STANDALONE_SYMBOL.finditer(prompt):
        marker = match.group(1)
        if not unicodedata.category(marker).startswith(("P", "S")):
            continue
        left_match = re.search(r"(\S+)\s*$", prompt[: match.start()])
        right_match = re.match(r"\s+(\S+)", prompt[match.end() :])
        if (
            marker in _MATH_OPERATOR_SYMBOLS
            and left_match is not None
            and right_match is not None
            and _SIMPLE_MATH_OPERAND.fullmatch(left_match.group(1))
            and _SIMPLE_MATH_OPERAND.fullmatch(right_match.group(1))
        ):
            continue
        marker_counts[marker] = marker_counts.get(marker, 0) + 1
        if marker_counts[marker] >= 2:
            return True
    return False
_RAW_HTML_BLOCK = re.compile(
    r"</?(?:h[1-6]|div|p|ul|ol|li|table|section|article|header|footer|blockquote)\b",
    flags=re.IGNORECASE,
)


def _numeric_pattern(quantity_unit_tokens: tuple[str, ...]) -> re.Pattern[str]:
    unit_pattern = "|".join(
        re.escape(token)
        for token in sorted(quantity_unit_tokens, key=len, reverse=True)
    )
    optional_unit = rf"(?:\s*(?:{unit_pattern}))?" if unit_pattern else ""
    value = rf"(?:{_DIGIT_VALUE}|(?i:{_WORD_NUMBER}))"
    atom = rf"{value}{optional_unit}"
    range_pattern = (
        rf"(?:\b(?i:between)\s+{atom}\s+(?i:and)\s+{atom}|"
        rf"{atom}\s*(?:[-–—]|(?i:to|through))\s*{atom})"
    )
    return re.compile(rf"(?<!\w)(?:{range_pattern}|{atom})(?!\w)")


def _numeric_witnesses(
    text: str, quantity_unit_tokens: tuple[str, ...]
) -> tuple[str, ...]:
    witnesses: list[str] = []
    # NFC preserves superscript unit exponents (m², s⁻²) so the complete unit
    # remains part of the witness instead of being split by compatibility fold.
    normalized = unicodedata.normalize("NFC", text)
    pattern = _numeric_pattern(quantity_unit_tokens)
    unit_pattern = (
        re.compile(
            "|".join(
                re.escape(token)
                for token in sorted(quantity_unit_tokens, key=len, reverse=True)
            )
        )
        if quantity_unit_tokens
        else None
    )
    for match in pattern.finditer(normalized):
        matched = match.group(0)
        unit_occurrences = (
            tuple(unit.group(0) for unit in unit_pattern.finditer(matched))
            if unit_pattern is not None
            else ()
        )
        declared_units = (
            (unit_occurrences[0],)
            if unit_occurrences and len(set(unit_occurrences)) == 1
            else unit_occurrences
        )
        numeric_text = unit_pattern.sub("", matched) if unit_pattern is not None else matched
        numeric_text = re.sub(
            r"(?<=[\d.])\s*[-–—]\s*(?=[+\-−]?(?:\d|\.\d))",
            "~",
            numeric_text,
        )
        witness = (
            numeric_text
            .casefold()
            .replace("−", "-")
            .replace("µ", "u")
            .replace("μ", "u")
        )
        if witness.startswith("between "):
            witness = witness.removeprefix("between ")
            witness = re.sub(r"\s+and\s+", "~", witness, count=1)
        else:
            witness = re.sub(r"\s+(?:to|through)\s+|[–—]", "~", witness)
            witness = re.sub(r"(?<=\w)\s+-\s+(?=\w)", "~", witness)
            witness = re.sub(r"(?<=\d)-(?=\d)", "~", witness)
            witness = re.sub(
                rf"\b({_NUMBER_WORD_ALTERNATION})-({_NUMBER_WORD_ALTERNATION})\b",
                lambda match: (
                    match.group(0)
                    if match.group(1) in _TENS_NUMBER_WORDS
                    and match.group(2)
                    in (_ONES_NUMBER_WORDS | _ONES_ORDINAL_WORDS)
                    or match.group(2) in _FRACTION_SCALE_NUMBER_WORDS
                    else f"{match.group(1)}~{match.group(2)}"
                ),
                witness,
            )
        if any(character.isdigit() for character in witness):
            witness = re.sub(r"\s+", "", witness)
        else:
            witness = re.sub(r"\band\b", " ", witness.replace("-", " "))
            witness = " ".join(witness.split())
        if declared_units:
            witness += "|units:" + ",".join(declared_units)
        witnesses.append(witness)
    return tuple(witnesses)


_NEGATION_CLAUSE_BREAK = re.compile(
    r"[,.;:!?]+|\b(?:but|then|whereas|while)\b", flags=re.IGNORECASE
)
_NEGATION_POSITION_STOP = {
    "a", "an", "the", "any", "to", "be", "being", "been", "do", "does",
    "did", "can", "could", "will", "would", "shall", "should", "may", "might",
    "must", "have", "has", "had", "is", "are", "was", "were", "it", "its",
    "they", "them", "their", "this", "that", "these", "those",
}
_NEGATION_SCOPE_EQUIVALENTS = {
    "omit": "skip", "omits": "skip", "omitted": "skip", "omitting": "skip",
    "skip": "skip", "skips": "skip", "skipped": "skip", "skipping": "skip",
    "proceed": "act", "proceeds": "act", "proceeded": "act", "proceeding": "act",
    "act": "act", "acts": "act", "acted": "act", "acting": "act",
}


def _normalize_contractions(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold().replace("’", "'")
    normalized = re.sub(r"\bcan't\b", "can not", normalized)
    normalized = re.sub(r"\bwon't\b", "will not", normalized)
    normalized = re.sub(r"\bshan't\b", "shall not", normalized)
    normalized = re.sub(r"\bain't\b", "is not", normalized)
    normalized = re.sub(r"\b([a-z]+)n't\b", r"\1 not", normalized)
    normalized = re.sub(r"\bcannot\b", "can not", normalized)
    return re.sub(r"\bavoid(?:s|ed|ing)?\b", "not", normalized)


def _negation_witnesses(
    text: str,
) -> tuple[tuple[int, int, str, int, str, str], ...]:
    clauses = tuple(
        clause.strip()
        for clause in _NEGATION_CLAUSE_BREAK.split(_normalize_contractions(text))
        if clause.strip()
    )
    witnesses: list[tuple[int, int, str, int, str, str]] = []
    for clause_index, clause in enumerate(clauses):
        tokens = tuple(
            _NEGATION_SCOPE_EQUIVALENTS.get(word.casefold(), word.casefold())
            for word in _WORD_PATTERN.findall(clause)
            if word.casefold() not in _NEGATION_POSITION_STOP
        )
        occurrence = 0
        for index, token in enumerate(tokens):
            if token not in _NEGATIONS:
                continue
            previous_scope = tokens[index - 1] if index else ""
            next_scope = tokens[index + 1] if index + 1 < len(tokens) else ""
            witnesses.append(
                (
                    clause_index,
                    occurrence,
                    token,
                    index,
                    previous_scope,
                    next_scope,
                )
            )
            occurrence += 1
    return tuple(witnesses)


def _normalized(text: str) -> str:
    folded = unicodedata.normalize("NFKC", text).casefold()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in folded).split())


def _complete_copy(prompt: str, text: str) -> bool:
    def copy_tokens(value: str) -> tuple[str, ...]:
        tokens = tuple(
            token[:-1] if len(token) > 4 and token.endswith("s") else token
            for token in _normalized(value).split()
        )
        collapsed: list[str] = []
        index = 0
        while index < len(tokens):
            if len(tokens[index]) == 1 and tokens[index].isalnum():
                end = index
                while (
                    end < len(tokens)
                    and len(tokens[end]) == 1
                    and tokens[end].isalnum()
                ):
                    end += 1
                if end - index > 1:
                    collapsed.append("".join(tokens[index:end]))
                    index = end
                    continue
            collapsed.append(tokens[index])
            index += 1
        return tuple(collapsed)

    prompt_tokens = copy_tokens(prompt)
    text_tokens = copy_tokens(text)
    if not text_tokens:
        return False
    width = len(text_tokens)
    return any(
        prompt_tokens[index : index + width] == text_tokens
        for index in range(len(prompt_tokens) - width + 1)
    )


_GENERIC_ANSWER = re.compile(
    r"(?:the\s+answer\s+is\s+)?pending(?:\s+review)?|"
    r"tbd|tba|tbc|nil|n\s*a|none|unavailable|"
    r"(?:(?:the\s+answer|answer|response|information|data)\s+(?:is\s+)?)?"
    r"(?:currently|presently|temporarily|momentarily)\s+"
    r"(?:unavailable|not\s+available)|"
    r"(?:the\s+answer\s+is\s+)?not\s+(?:currently\s+)?available|"
    r"(?:answer|response|information|data)\s+(?:is\s+)?"
    r"(?:unavailable|not\s+available)|no\s+data\s+available|"
    r"no\s+(?:response|idea|information)|not\s+(?:known|sure)|undetermined|"
    r"not\s+applicable|i\s+don\s+t\s+know|"
    r"to\s+be\s+(?:determined|announced|advised|confirmed)|"
    r"(?:(?:it|this|that|the\s+answer|the\s+response)\s+(?:is\s+)?)?"
    r"unknown(?:\s+at\s+this\s+time)?|"
    r"indeterminate(?:\s+at\s+present)?|"
    r"(?:the\s+answer\s+is\s+)?not\s+provided(?:\s+yet)?|"
    r"answer\s+unavailable|insufficient\s+information|"
    r"not\s+enough\s+(?:information|data)|"
    r"no\s+(?:answer|response)\s+is\s+available|"
    r"(?:it|this|that|the\s+answer)\s+(?:is\s+)?"
    r"(?:dependent\s+on|depends(?:\s+on)?)(?:\s+context)?|"
    r"(?:(?:it|this|that|the\s+answer|the\s+response)\s+)?"
    r"(?:cannot|can\s+not|unable\s+to)\s+(?:be\s+)?"
    r"(?:determine|determined|answer|say|establish|established)"
    r"(?:\s+from\s+available\s+information)?"
)


def _generic_answer(text: str) -> bool:
    normalized = _normalized(text)
    return not normalized or bool(_GENERIC_ANSWER.fullmatch(normalized))


def _pre_gate(request: CheckOnLearningRequest) -> tuple[PreGateDisposition, tuple[str, ...]]:
    status = request.promise.projection.status
    if status == "unavailable":
        return "promise_unavailable", ()
    if status == "degraded":
        return "promise_degraded", ()
    ability_ids = tuple(vow.objective_id for vow in request.promise.projection.vows)
    if not request.source_spans or not request.source_claims:
        return "source_unavailable", ability_ids
    authorized = {ability for claim in request.source_claims for ability in claim.ability_refs}
    missing = tuple(ability for ability in ability_ids if ability not in authorized)
    if missing:
        return "missing_ability_proof", missing
    return "eligible", ()


def _inventory(
    request: CheckOnLearningRequest,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(vow.objective_id for vow in request.promise.projection.vows),
        tuple(claim.claim_id for claim in request.source_claims),
        tuple(span.span_id for span in request.source_spans),
    )


def _pre_gate_receipt(
    request: CheckOnLearningRequest,
    disposition: PreGateDisposition,
    missing: tuple[str, ...],
) -> CheckGateReceipt:
    ability_ids, claim_ids, span_ids = _inventory(request)
    covered = tuple(item for item in ability_ids if item not in set(missing))
    failure_by_disposition = {
        "promise_unavailable": "promise_authority_unavailable",
        "promise_degraded": "promise_authority_degraded",
        "source_unavailable": "source_authority_unavailable",
        "missing_ability_proof": "missing_ability_proof",
    }
    return CheckGateReceipt(
        authority_digest=check_authority_digest(request),
        candidate_digest=NO_CANDIDATE_DIGEST,
        pre_gate_disposition=disposition,
        status="fail",
        declared_ability_ids=ability_ids,
        declared_claim_ids=claim_ids,
        declared_span_ids=span_ids,
        covered_ability_ids=covered,
        missing_ability_ids=missing,
        unknown_claim_refs=(),
        unknown_source_refs=(),
        unknown_ability_refs=(),
        failures=(failure_by_disposition[disposition],),
    )


def _candidate_gate(
    request: CheckOnLearningRequest,
    candidate: CheckOnLearningWriterCandidate,
) -> CheckGateReceipt:
    ability_ids, claim_ids, span_ids = _inventory(request)
    ability_set, span_set = set(ability_ids), set(span_ids)
    claim_by_id = {claim.claim_id: claim for claim in request.source_claims}
    span_by_id = {span.span_id: span for span in request.source_spans}
    failures: list[str] = []
    unknown_claims: list[str] = []
    unknown_spans: list[str] = []
    unknown_abilities: list[str] = []
    credited: list[str] = []

    item_abilities = tuple(item.ability_id for item in candidate.items)
    unknown_abilities.extend(item for item in item_abilities if item not in ability_set)
    known_item_abilities = tuple(item for item in item_abilities if item in ability_set)
    indices = tuple(ability_ids.index(item) for item in known_item_abilities)
    if indices != tuple(sorted(indices)):
        failures.append("ability_order_mismatch")

    for item in candidate.items:
        item_valid = item.ability_id in ability_set
        expected_answer = " ".join(claim.text for claim in item.answer_claims)
        if item.expected_answer != expected_answer:
            failures.append("answer_claim_composition_failed")
            item_valid = False
        prompt = item.prompt.strip()
        leading_marker = unicodedata.category(prompt[0]).startswith(("P", "S")) and (
            len(prompt) == 1 or prompt[1].isspace()
        )
        if (
            prompt != item.prompt
            or prompt.startswith(("#", ">", "-", "*", "+"))
            or prompt[0] in _UNICODE_BULLETS
            or leading_marker
            or _RAW_HTML_BLOCK.search(prompt)
            or not _FREE_RESPONSE_GRAMMAR.fullmatch(prompt)
            or _has_supplied_alternatives(prompt)
            or re.match(r"^\d+[.)]\s", prompt)
            or _CHOICE_OR_REREAD.search(prompt)
            or _EMBEDDED_SOURCE_CONSULT.search(prompt)
            or _CHOICE_SCAFFOLD.search(prompt)
            or _DISCLOSURE_MARKER.search(prompt)
            or _ENUMERATED_CHOICE.search(prompt)
            or _UNICODE_ENUMERATOR.search(prompt)
            or _has_unicode_enumeration(prompt)
            or _has_repeated_symbol_enumeration(prompt)
            or _DEIXIS.search(prompt)
        ):
            failures.append("retrieval_posture_failed")
            item_valid = False
        if _complete_copy(prompt, item.expected_answer):
            failures.append("answer_leakage_failed")
            item_valid = False
        if _generic_answer(item.expected_answer):
            failures.append("unusable_answer_failed")
            item_valid = False
        for answer_claim in item.answer_claims:
            source_claim = claim_by_id.get(answer_claim.source_claim_ref)
            if source_claim is None:
                unknown_claims.append(answer_claim.source_claim_ref)
                item_valid = False
            else:
                if _complete_copy(prompt, source_claim.text):
                    failures.append("answer_leakage_failed")
                    item_valid = False
                for span_ref in source_claim.source_span_refs:
                    source_span = span_by_id.get(span_ref)
                    if source_span is not None and _complete_copy(prompt, source_span.text):
                        failures.append("answer_leakage_failed")
                        item_valid = False
                if set(answer_claim.source_span_refs) != set(
                    source_claim.source_span_refs
                ):
                    failures.append("source_trace_mismatch")
                    item_valid = False
                if item.ability_id not in source_claim.ability_refs:
                    failures.append("ability_permission_mismatch")
                    item_valid = False
                if _numeric_witnesses(
                    answer_claim.text, request.quantity_unit_tokens
                ) != _numeric_witnesses(
                    source_claim.text, request.quantity_unit_tokens
                ):
                    failures.append("numeric_fidelity_failed")
                    item_valid = False
                if _negation_witnesses(answer_claim.text) != _negation_witnesses(
                    source_claim.text
                ):
                    failures.append("negation_fidelity_failed")
                    item_valid = False
            unknown_spans.extend(
                ref for ref in answer_claim.source_span_refs if ref not in span_set
            )
            if any(ref not in span_set for ref in answer_claim.source_span_refs):
                item_valid = False
        if item_valid and item.ability_id not in credited:
            credited.append(item.ability_id)

    covered = tuple(item for item in ability_ids if item in set(credited))
    missing = tuple(item for item in ability_ids if item not in set(credited))
    if missing:
        failures.append("missing_ability_proof")
    if unknown_claims:
        failures.append("unknown_claim_reference")
    if unknown_spans:
        failures.append("unknown_source_reference")
    if unknown_abilities:
        failures.append("unknown_ability_reference")
    failures = list(dict.fromkeys(failures))
    return CheckGateReceipt(
        authority_digest=check_authority_digest(request),
        candidate_digest=check_candidate_digest(candidate),
        pre_gate_disposition="eligible",
        status="fail" if failures else "pass",
        declared_ability_ids=ability_ids,
        declared_claim_ids=claim_ids,
        declared_span_ids=span_ids,
        covered_ability_ids=covered,
        missing_ability_ids=missing,
        unknown_claim_refs=tuple(sorted(set(unknown_claims))),
        unknown_source_refs=tuple(sorted(set(unknown_spans))),
        unknown_ability_refs=tuple(sorted(set(unknown_abilities))),
        failures=tuple(failures),
    )


def _pre_gate_result_loss(
    disposition: PreGateDisposition,
) -> tuple[CheckStatus, ResultLoss, str]:
    mapping: dict[PreGateDisposition, tuple[CheckStatus, ResultLoss, str]] = {
        "promise_unavailable": (
            "unavailable",
            "check_promise_authority_unavailable",
            CHECK_UNAVAILABLE_MARKER,
        ),
        "promise_degraded": (
            "degraded",
            "check_promise_authority_degraded",
            CHECK_DEGRADED_MARKER,
        ),
        "source_unavailable": (
            "unavailable",
            "check_source_unavailable",
            CHECK_UNAVAILABLE_MARKER,
        ),
        "missing_ability_proof": (
            "degraded",
            "check_missing_ability_proof",
            CHECK_DEGRADED_MARKER,
        ),
        "eligible": ("degraded", "check_gate_failed", CHECK_DEGRADED_MARKER),
    }
    return mapping[disposition]


def _candidate_result_loss(
    candidate: CheckOnLearningWriterCandidate,
    gate: CheckGateReceipt,
) -> tuple[CheckStatus, ResultLoss, str]:
    if candidate.status != "authored":
        loss = candidate.known_losses[0]
        return candidate.status, loss, candidate.marker or CHECK_DEGRADED_MARKER
    if gate.unknown_claim_refs or gate.unknown_source_refs or gate.unknown_ability_refs:
        return "unavailable", "check_reference_validation_failed", CHECK_UNAVAILABLE_MARKER
    if gate.missing_ability_ids:
        return "degraded", "check_missing_ability_proof", CHECK_DEGRADED_MARKER
    return "degraded", "check_gate_failed", CHECK_DEGRADED_MARKER


class CheckOnLearningResult(_StrictModel):
    status: CheckStatus
    items: tuple[RetrievalCheckItem, ...]
    known_losses: tuple[ResultLoss, ...]
    marker: NonBlankLine | None
    authority: CheckOnLearningRequest
    candidate_snapshot: CheckOnLearningWriterCandidate | None
    authority_digest: Sha256Digest
    candidate_digest: Sha256Digest
    gate: CheckGateReceipt

    @model_validator(mode="after")
    def _anti_forgery_replay(self) -> CheckOnLearningResult:
        authority = CheckOnLearningRequest.model_validate(
            self.authority.model_dump(mode="python"), strict=True
        )
        disposition, missing = _pre_gate(authority)
        if self.authority_digest != check_authority_digest(authority):
            raise ValueError("result requires recomputed authority digest")
        if disposition != "eligible":
            if self.candidate_snapshot is not None:
                raise ValueError("pre-gate result cannot forge candidate presence")
            expected_gate = _pre_gate_receipt(authority, disposition, missing)
            expected_status, expected_loss, expected_marker = _pre_gate_result_loss(disposition)
            if self.candidate_digest != NO_CANDIDATE_DIGEST:
                raise ValueError("pre-gate result requires no-candidate digest")
            if (
                self.gate != expected_gate
                or self.status != expected_status
                or self.known_losses != (expected_loss,)
                or self.marker != expected_marker
                or self.items
            ):
                raise ValueError("pre-gate result must equal recomputed disposition")
            return self

        if self.candidate_snapshot is None:
            raise ValueError("eligible result requires a candidate snapshot")
        candidate = CheckOnLearningWriterCandidate.model_validate(
            self.candidate_snapshot.model_dump(mode="python"), strict=True
        )
        expected_digest = check_candidate_digest(candidate)
        expected_gate = _candidate_gate(authority, candidate)
        if self.candidate_digest != expected_digest or self.gate != expected_gate:
            raise ValueError("result candidate digest/gate must equal deterministic replay")
        if candidate.status == "authored" and expected_gate.status == "pass":
            if (
                self.status != "authored"
                or self.items != candidate.items
                or self.known_losses
                or self.marker is not None
            ):
                raise ValueError("authored result must equal its passing candidate")
        else:
            status, loss, marker = _candidate_result_loss(candidate, expected_gate)
            if (
                self.status != status
                or self.items
                or self.known_losses != (loss,)
                or self.marker != marker
            ):
                raise ValueError("non-authored result must equal recomputed disposition")
        return self


def offline_check_on_learning_writer(
    request: CheckOnLearningRequest,
) -> CheckOnLearningWriterCandidate:
    del request
    return CheckOnLearningWriterCandidate(
        status="unavailable",
        items=(),
        known_losses=("check_writer_unavailable",),
        marker=CHECK_UNAVAILABLE_MARKER,
    )


def compose_check_on_learning(
    request: CheckOnLearningRequest,
    writer: CheckOnLearningWriter
    | Callable[[CheckOnLearningRequest], CheckOnLearningWriterCandidate],
) -> CheckOnLearningResult:
    """Pre-gate authority, call the writer exactly once when eligible, and gate."""
    if not isinstance(request, CheckOnLearningRequest):
        raise TypeError("request must be a CheckOnLearningRequest")
    request = CheckOnLearningRequest.model_validate(request.model_dump(mode="python"), strict=True)
    disposition, missing = _pre_gate(request)
    authority_digest = check_authority_digest(request)
    if disposition != "eligible":
        gate = _pre_gate_receipt(request, disposition, missing)
        status, loss, marker = _pre_gate_result_loss(disposition)
        return CheckOnLearningResult(
            status=status,
            items=(),
            known_losses=(loss,),
            marker=marker,
            authority=request,
            candidate_snapshot=None,
            authority_digest=authority_digest,
            candidate_digest=NO_CANDIDATE_DIGEST,
            gate=gate,
        )

    candidate = writer(request)  # Pinned policy: writer exceptions propagate unchanged.
    if not isinstance(candidate, CheckOnLearningWriterCandidate):
        raise TypeError("writer must return CheckOnLearningWriterCandidate")
    candidate = CheckOnLearningWriterCandidate.model_validate(
        candidate.model_dump(mode="python"), strict=True
    )
    gate = _candidate_gate(request, candidate)
    candidate_digest = check_candidate_digest(candidate)
    if candidate.status == "authored" and gate.status == "pass":
        return CheckOnLearningResult(
            status="authored",
            items=candidate.items,
            known_losses=(),
            marker=None,
            authority=request,
            candidate_snapshot=candidate,
            authority_digest=authority_digest,
            candidate_digest=candidate_digest,
            gate=gate,
        )
    status, loss, marker = _candidate_result_loss(candidate, gate)
    return CheckOnLearningResult(
        status=status,
        items=(),
        known_losses=(loss,),
        marker=marker,
        authority=request,
        candidate_snapshot=candidate,
        authority_digest=authority_digest,
        candidate_digest=candidate_digest,
        gate=gate,
    )


__all__ = [
    "CHECK_DEGRADED_MARKER",
    "CHECK_UNAVAILABLE_MARKER",
    "NO_CANDIDATE_DIGEST",
    "CheckAnswerClaim",
    "CheckGateReceipt",
    "CheckOnLearningRequest",
    "CheckOnLearningResult",
    "CheckOnLearningWriter",
    "CheckOnLearningWriterCandidate",
    "CheckSourceClaim",
    "CheckSourceSpan",
    "RetrievalCheckItem",
    "check_authority_digest",
    "check_candidate_digest",
    "compose_check_on_learning",
    "offline_check_on_learning_writer",
]
