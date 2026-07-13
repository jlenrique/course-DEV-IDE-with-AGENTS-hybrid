"""Pure, source-bound contracts and gates for the Deep Dive skeleton.

The module deliberately has no runtime, provider, persistence, or research
dependencies.  A writer may re-voice prose, but only declared IDs earn credit.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from typing import Annotated, Literal, Protocol

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator

DeepDiveStatus = Literal["authored", "degraded", "unavailable"]
ClaimRole = Literal["vo", "source_supported_delta"]
GateStatus = Literal["pass", "fail"]
WriterLoss = Literal[
    "deep_dive_writer_unavailable",
    "deep_dive_source_unavailable",
    "deep_dive_depth_delta_unavailable",
    "deep_dive_execution_failed",
]
ResultLoss = Literal[
    "deep_dive_writer_unavailable",
    "deep_dive_source_unavailable",
    "deep_dive_depth_delta_unavailable",
    "deep_dive_execution_failed",
    "deep_dive_reference_validation_failed",
    "deep_dive_skeleton_gate_failed",
]

DEEP_DIVE_UNAVAILABLE_MARKER = "deep_dive_skeleton_unavailable"
DEEP_DIVE_DEGRADED_MARKER = "deep_dive_skeleton_degraded"
DEPTH_LOSS = "deep_dive_depth_delta_unavailable"
OPERATOR_SEMANTIC_WARNING = (
    "full_semantic_equivalence_non_contradiction_and_depth_require_operator_spot_check"
)


def _non_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("value must contain non-whitespace text")
    return value


def _single_line(value: str) -> str:
    if any(mark in value for mark in ("\n", "\r", "\u2028", "\u2029")):
        raise ValueError("value must be one line")
    return value


def _sha256_digest(value: str) -> str:
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError("value must be a canonical sha256 digest")
    return value


NonBlankStr = Annotated[str, AfterValidator(_non_blank)]
NonBlankLine = Annotated[str, AfterValidator(_non_blank), AfterValidator(_single_line)]
Sha256Digest = Annotated[str, AfterValidator(_sha256_digest)]


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


class NarrationSourceSpan(_StrictModel):
    span_id: NonBlankLine
    text: NonBlankStr
    source_ref: NonBlankLine


class SourceClaim(_StrictModel):
    claim_id: NonBlankLine
    text: NonBlankStr
    source_span_refs: tuple[NonBlankLine, ...]
    role: ClaimRole

    @model_validator(mode="after")
    def _refs_are_nonempty_unique(self) -> SourceClaim:
        if not self.source_span_refs:
            raise ValueError("source claim requires at least one source span ref")
        _require_unique(self.source_span_refs, "source span refs")
        return self


class DeepDiveAbilityInput(_StrictModel):
    ability_id: NonBlankLine
    text: NonBlankStr


class DeepDiveSkeletonClaim(_StrictModel):
    skeleton_claim_id: NonBlankLine
    text: NonBlankStr
    source_claim_refs: tuple[NonBlankLine, ...]
    source_span_refs: tuple[NonBlankLine, ...]

    @model_validator(mode="after")
    def _refs_are_nonempty_unique(self) -> DeepDiveSkeletonClaim:
        if not self.source_claim_refs or not self.source_span_refs:
            raise ValueError("skeleton claim requires claim and source-span traces")
        if len(self.source_claim_refs) != 1:
            raise ValueError("skeleton claim must trace exactly one source claim")
        _require_unique(self.source_claim_refs, "claim refs")
        _require_unique(self.source_span_refs, "source span refs")
        return self


class DeepDiveAbilitySection(_StrictModel):
    ability_id: NonBlankLine
    prose: NonBlankStr
    claims: tuple[DeepDiveSkeletonClaim, ...]

    @model_validator(mode="after")
    def _has_claims(self) -> DeepDiveAbilitySection:
        if not self.claims:
            raise ValueError("ability section requires at least one skeleton claim")
        return self


class BoldTermMarker(_StrictModel):
    term: NonBlankLine

    @model_validator(mode="after")
    def _safe_term(self) -> BoldTermMarker:
        if "**" in self.term or self.term != self.term.strip() or self.term.startswith("#"):
            raise ValueError("bold term contains unsafe Markdown")
        return self


class DeepDiveSkeletonRequest(_StrictModel):
    lesson_ref: NonBlankLine
    source_spans: tuple[NarrationSourceSpan, ...]
    source_claims: tuple[SourceClaim, ...]
    abilities: tuple[DeepDiveAbilityInput, ...]

    @model_validator(mode="after")
    def _closed_authority(self) -> DeepDiveSkeletonRequest:
        if not self.source_spans:
            raise ValueError("request requires nonblank narration/source spans")
        if not self.source_claims:
            raise ValueError("request requires source claims")
        if not self.abilities:
            raise ValueError("request requires ratified ability authority")
        _require_unique(tuple(span.span_id for span in self.source_spans), "source span IDs")
        _require_unique(tuple(claim.claim_id for claim in self.source_claims), "claim IDs")
        _require_unique(tuple(item.ability_id for item in self.abilities), "ability IDs")
        span_ids = {span.span_id for span in self.source_spans}
        for claim in self.source_claims:
            unknown = tuple(ref for ref in claim.source_span_refs if ref not in span_ids)
            if unknown:
                raise ValueError(f"claim references unknown source span: {', '.join(unknown)}")
        if not any(claim.role == "vo" for claim in self.source_claims):
            raise ValueError("request requires at least one declared VO claim")
        return self


_BOLD_PATTERN = re.compile(r"\*\*([^*\r\n]+)\*\*")


def _marked_terms(prose: tuple[str, ...]) -> tuple[str, ...]:
    terms: list[str] = []
    for text in prose:
        if text.count("**") % 2:
            raise ValueError("unmatched bold marker")
        stripped = _BOLD_PATTERN.sub("", text)
        if "**" in stripped:
            raise ValueError("nested or malformed bold marker")
        for match in _BOLD_PATTERN.finditer(text):
            term = match.group(1)
            if term != term.strip() or "**" in term:
                raise ValueError("unsafe bold marker")
            before = text[match.start() - 1] if match.start() else ""
            after = text[match.end()] if match.end() < len(text) else ""
            if (before and (before.isalnum() or before == "_")) or (
                after and (after.isalnum() or after == "_")
            ):
                raise ValueError("bold term is not at a prose boundary")
            if term not in terms:
                terms.append(term)
    return tuple(terms)


class DeepDiveSkeletonWriterResult(_StrictModel):
    """Writer-side candidate; cross-authority references are gated by the adapter."""

    status: DeepDiveStatus
    sections: tuple[DeepDiveAbilitySection, ...]
    bold_terms: tuple[BoldTermMarker, ...]
    known_losses: tuple[WriterLoss, ...]
    marker: NonBlankLine | None

    @model_validator(mode="after")
    def _honest_local_shape(self) -> DeepDiveSkeletonWriterResult:
        if self.status == "authored":
            if not self.sections:
                raise ValueError("authored candidate requires sections")
            if self.known_losses or self.marker is not None:
                raise ValueError("authored candidate cannot carry losses or marker")
            _require_unique(
                tuple(
                    claim.skeleton_claim_id
                    for section in self.sections
                    for claim in section.claims
                ),
                "skeleton claim IDs",
            )
            _require_unique(tuple(term.term for term in self.bold_terms), "bold terms")
            if _marked_terms(tuple(section.prose for section in self.sections)) != tuple(
                term.term for term in self.bold_terms
            ):
                raise ValueError("bold marker/metadata mismatch")
        else:
            if self.sections or self.bold_terms:
                raise ValueError("non-authored candidate cannot carry prose or terms")
            if not self.known_losses or self.marker is None:
                raise ValueError("non-authored candidate requires losses and marker")
            if len(self.known_losses) != 1:
                raise ValueError("non-authored candidate requires exactly one typed loss")
            expected_marker = (
                DEEP_DIVE_UNAVAILABLE_MARKER
                if self.status == "unavailable"
                else DEEP_DIVE_DEGRADED_MARKER
            )
            if self.marker != expected_marker:
                raise ValueError("candidate status requires its canonical marker")
        return self


# Explicit semantic name for the writer's untrusted pre-gate return.  The
# longer legacy name remains public for Story 37.1 import compatibility.
DeepDiveWriterCandidate = DeepDiveSkeletonWriterResult


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _authority_digest(request: DeepDiveSkeletonRequest) -> str:
    return _canonical_digest(request.model_dump(mode="json"))


def deep_dive_authority_digest(request: DeepDiveSkeletonRequest) -> str:
    """Return the canonical digest consumers compare with a result's authority pin."""
    if not isinstance(request, DeepDiveSkeletonRequest):
        raise TypeError("request must be a DeepDiveSkeletonRequest")
    request = DeepDiveSkeletonRequest.model_validate(request.model_dump())
    return _authority_digest(request)


def _candidate_payload_digest(
    sections: tuple[DeepDiveAbilitySection, ...],
    bold_terms: tuple[BoldTermMarker, ...],
) -> str:
    return _canonical_digest(
        {
            "sections": [section.model_dump(mode="json") for section in sections],
            "bold_terms": [term.model_dump(mode="json") for term in bold_terms],
        }
    )


class DeepDiveGateReceipt(_StrictModel):
    gate_version: Literal["deep-dive-skeleton-gate.v1"] = "deep-dive-skeleton-gate.v1"
    authority_digest: Sha256Digest
    candidate_payload_digest: Sha256Digest
    declared_vo_claim_ids: tuple[NonBlankLine, ...]
    declared_delta_claim_ids: tuple[NonBlankLine, ...]
    declared_ability_ids: tuple[NonBlankLine, ...]
    declared_span_ids: tuple[NonBlankLine, ...]
    status: GateStatus
    covered_vo_claim_ids: tuple[NonBlankLine, ...]
    missing_vo_claim_ids: tuple[NonBlankLine, ...]
    used_delta_claim_ids: tuple[NonBlankLine, ...]
    unknown_claim_refs: tuple[NonBlankLine, ...]
    unknown_source_refs: tuple[NonBlankLine, ...]
    unknown_ability_refs: tuple[NonBlankLine, ...]
    failures: tuple[NonBlankLine, ...]
    operator_warnings: tuple[NonBlankLine, ...] = (OPERATOR_SEMANTIC_WARNING,)

    @model_validator(mode="after")
    def _status_matches_failures(self) -> DeepDiveGateReceipt:
        if (self.status == "pass") == bool(self.failures):
            raise ValueError("gate status must reconcile with failures")
        _require_unique(self.failures, "gate failures")
        for values, label in (
            (self.declared_vo_claim_ids, "declared VO inventory"),
            (self.declared_delta_claim_ids, "declared delta inventory"),
            (self.declared_ability_ids, "declared ability inventory"),
            (self.declared_span_ids, "declared span inventory"),
            (self.covered_vo_claim_ids, "covered VO diagnostics"),
            (self.missing_vo_claim_ids, "missing VO diagnostics"),
            (self.used_delta_claim_ids, "delta diagnostics"),
            (self.unknown_claim_refs, "unknown claim diagnostics"),
            (self.unknown_source_refs, "unknown source diagnostics"),
            (self.unknown_ability_refs, "unknown ability diagnostics"),
        ):
            _require_unique(values, label)
        if not self.declared_vo_claim_ids:
            raise ValueError("receipt requires a declared VO inventory")
        if not self.declared_ability_ids or not self.declared_span_ids:
            raise ValueError("receipt requires declared ability and span inventories")
        if set(self.declared_vo_claim_ids) & set(self.declared_delta_claim_ids):
            raise ValueError("declared VO and delta inventories must be disjoint")
        if set(self.covered_vo_claim_ids) & set(self.missing_vo_claim_ids):
            raise ValueError("covered and missing VO diagnostics must be disjoint")
        covered = set(self.covered_vo_claim_ids)
        missing = set(self.missing_vo_claim_ids)
        if covered | missing != set(self.declared_vo_claim_ids):
            raise ValueError("covered and missing VO IDs must form an exact partition")
        if self.covered_vo_claim_ids != tuple(
            item for item in self.declared_vo_claim_ids if item in covered
        ) or self.missing_vo_claim_ids != tuple(
            item for item in self.declared_vo_claim_ids if item in missing
        ):
            raise ValueError("VO partition must preserve declared order")
        if not set(self.used_delta_claim_ids) <= set(self.declared_delta_claim_ids):
            raise ValueError("used delta diagnostics must be a declared delta subset")
        if self.used_delta_claim_ids != tuple(
            item for item in self.declared_delta_claim_ids if item in self.used_delta_claim_ids
        ):
            raise ValueError("used delta diagnostics must preserve declared order")
        if set(self.unknown_claim_refs) & (
            set(self.declared_vo_claim_ids) | set(self.declared_delta_claim_ids)
        ):
            raise ValueError("unknown claim diagnostics cannot name declared claims")
        if set(self.unknown_source_refs) & set(self.declared_span_ids):
            raise ValueError("unknown source diagnostics cannot name declared spans")
        if set(self.unknown_ability_refs) & set(self.declared_ability_ids):
            raise ValueError("unknown ability diagnostics cannot name declared abilities")
        diagnostic_pairs = (
            (self.missing_vo_claim_ids, "declared_vo_claim_coverage_failed", "VO"),
            (self.unknown_claim_refs, "unknown_claim_reference", "unknown claim"),
            (self.unknown_source_refs, "unknown_source_reference", "unknown source"),
            (self.unknown_ability_refs, "unknown_ability_reference", "unknown ability"),
        )
        for values, failure, label in diagnostic_pairs:
            if bool(values) != (failure in self.failures):
                raise ValueError(f"{label} diagnostics must reconcile with failures")
        if bool(self.used_delta_claim_ids) == (DEPTH_LOSS in self.failures):
            raise ValueError("delta diagnostics must reconcile with depth failure")
        if self.operator_warnings != (OPERATOR_SEMANTIC_WARNING,):
            raise ValueError("gate requires the canonical operator warning")
        return self


class DeepDiveSkeletonResult(_StrictModel):
    status: DeepDiveStatus
    sections: tuple[DeepDiveAbilitySection, ...]
    bold_terms: tuple[BoldTermMarker, ...]
    known_losses: tuple[ResultLoss, ...]
    marker: NonBlankLine | None
    authority: DeepDiveSkeletonRequest
    candidate_snapshot: DeepDiveWriterCandidate
    authority_digest: Sha256Digest
    candidate_payload_digest: Sha256Digest
    gate: DeepDiveGateReceipt

    @model_validator(mode="after")
    def _honest_result(self) -> DeepDiveSkeletonResult:
        authority = DeepDiveSkeletonRequest.model_validate(self.authority.model_dump())
        candidate = DeepDiveSkeletonWriterResult.model_validate(
            self.candidate_snapshot.model_dump()
        )
        if self.authority_digest != _authority_digest(authority):
            raise ValueError("result requires recomputed request authority digest")
        if self.candidate_payload_digest != _candidate_payload_digest(
            candidate.sections, candidate.bold_terms
        ):
            raise ValueError("result requires recomputed candidate payload digest from snapshot")
        if self.authority_digest != self.gate.authority_digest:
            raise ValueError("result authority digest must equal gate authority digest")
        if self.candidate_payload_digest != self.gate.candidate_payload_digest:
            raise ValueError(
                "result candidate payload digest must equal gate candidate payload digest"
            )
        recomputed_gate = _gate(authority, candidate)
        if self.gate != recomputed_gate:
            raise ValueError("result gate must equal the recomputed gate receipt")
        if self.status == "authored":
            if not self.sections or self.known_losses or self.marker is not None:
                raise ValueError("authored result requires prose and no loss state")
            if candidate.status != "authored" or recomputed_gate.status != "pass":
                raise ValueError("authored result requires a passing authored candidate")
            if self.sections != candidate.sections or self.bold_terms != candidate.bold_terms:
                raise ValueError("authored result payload must equal the candidate snapshot")
            if self.candidate_payload_digest != _candidate_payload_digest(
                self.sections, self.bold_terms
            ):
                raise ValueError("authored result requires recomputed candidate payload digest")
        else:
            if self.sections or self.bold_terms or not self.known_losses or self.marker is None:
                raise ValueError("non-authored result requires empty payload and loss state")
            if len(self.known_losses) != 1:
                raise ValueError("non-authored result requires exactly one typed loss")
            if self.gate.status != "fail":
                raise ValueError("non-authored result requires a failed gate")
            expected_status, expected_marker, expected_losses = _failed_result_disposition(
                candidate, recomputed_gate
            )
            if (
                self.status != expected_status
                or self.marker != expected_marker
                or self.known_losses != expected_losses
            ):
                raise ValueError("non-authored result must equal the recomputed disposition")
        return self


class DeepDiveWriter(Protocol):
    """Injected semantic writer returning an untrusted, pre-gate candidate."""

    def __call__(self, request: DeepDiveSkeletonRequest) -> DeepDiveWriterCandidate: ...


_NUMBER_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty",
    "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand",
    "million", "billion", "first", "second", "third", "fourth", "fifth", "sixth",
    "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth", "dozen", "half",
    "quarter", "percent",
)
_NUMBER_WORD_ALTERNATION = "|".join(_NUMBER_WORDS)
_SIGN = r"[+\-−]?"
_DECIMAL = r"(?:\d+(?:\.\d+)?|\.\d+)"
_SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"
_SCIENTIFIC_EXPONENT = (
    rf"(?:[eE]{_SIGN}\d+|\s*[×x]\s*10(?:\s*\^\s*{_SIGN}\d+|[{_SUPERSCRIPTS}]+))?"
)
_UNIT_EXPONENT = rf"(?:[{_SUPERSCRIPTS}]|[²³]|[+\-−]\d+)*"
_UNIT_COMPONENT = rf"[A-Za-zµμ°]+{_UNIT_EXPONENT}"
_COMPOUND_UNIT = rf"{_UNIT_COMPONENT}(?:\s*(?:/|[·⋅*])\s*{_UNIT_COMPONENT})*"
_DIGIT_ATOM = rf"{_SIGN}{_DECIMAL}{_SCIENTIFIC_EXPONENT}(?:\s*(?:%|{_COMPOUND_UNIT}))?"
_DIGIT_RANGE = rf"{_DIGIT_ATOM}(?:\s*[-–—]\s*{_DIGIT_ATOM})?"
_WORD_NUMBER = (
    rf"\b(?:{_NUMBER_WORD_ALTERNATION})"
    rf"(?:(?:[\s-]+and)?[\s-]+(?:{_NUMBER_WORD_ALTERNATION}))*\b"
)
_NUMERIC_PATTERN = re.compile(
    rf"(?<!\w)(?:{_DIGIT_RANGE}|{_WORD_NUMBER})(?!\w)", flags=re.IGNORECASE
)
_WORD_PATTERN = re.compile(r"\b[\w'-]+\b", flags=re.UNICODE)
_NEGATIONS = {"no", "not", "never", "without", "neither", "nor"}
_FORBIDDEN_PROSE_TOKENS = (
    "revoice-required",
    "voice-profile:",
    "empty narration",
    "narration unavailable",
)
_SLIDE_DEIXIS = re.compile(
    r"\b(?:this|that|the)\s+(?:slide|deck|screen)\b|\b(?:above|below)\s+(?:slide|figure)\b",
    flags=re.IGNORECASE,
)


def _numeric_witnesses(text: str) -> tuple[str, ...]:
    witnesses: list[str] = []
    for match in _NUMERIC_PATTERN.finditer(text):
        witness = (
            match.group(0)
            .lower()
            .replace("−", "-")
            .replace("–", "-")
            .replace("—", "-")
        )
        if any(character.isdigit() for character in witness):
            witness = re.sub(r"\s+", "", witness)
        else:
            witness = witness.replace("-", " ")
            witness = re.sub(r"\band\b", " ", witness)
            witness = " ".join(witness.split())
        witnesses.append(witness)
    return tuple(witnesses)


def _negation_count(text: str) -> int:
    return sum(word.lower() in _NEGATIONS for word in _WORD_PATTERN.findall(text))


def _ordered_known(values: list[str], authority_order: tuple[str, ...]) -> tuple[str, ...]:
    present = set(values)
    return tuple(value for value in authority_order if value in present)


def _source_contains_term(source_text: str, term: str) -> bool:
    return bool(
        re.search(
            rf"(?<!\w){re.escape(term)}(?!\w)",
            source_text,
            flags=re.IGNORECASE,
        )
    )


def _gate(
    request: DeepDiveSkeletonRequest, candidate: DeepDiveSkeletonWriterResult
) -> DeepDiveGateReceipt:
    claim_by_id = {claim.claim_id: claim for claim in request.source_claims}
    span_ids = {span.span_id for span in request.source_spans}
    ability_order = tuple(ability.ability_id for ability in request.abilities)
    ability_ids = set(ability_order)
    vo_ids = tuple(claim.claim_id for claim in request.source_claims if claim.role == "vo")
    delta_ids = tuple(
        claim.claim_id for claim in request.source_claims if claim.role == "source_supported_delta"
    )
    traced: list[str] = []
    unknown_claims: list[str] = []
    unknown_spans: list[str] = []
    unknown_abilities: list[str] = []
    failures: list[str] = []

    section_abilities = tuple(section.ability_id for section in candidate.sections)
    unknown_abilities.extend(item for item in section_abilities if item not in ability_ids)
    if section_abilities != ability_order:
        failures.append("ability_order_mismatch")
    if _duplicates(section_abilities):
        failures.append("duplicate_ability_section")

    for section in candidate.sections:
        lowered = section.prose.lower()
        expected_prose = " ".join(claim.text for claim in section.claims)
        if section.prose != expected_prose:
            failures.append("prose_claim_composition_failed")
        if (
            any(token in lowered for token in _FORBIDDEN_PROSE_TOKENS)
            or _SLIDE_DEIXIS.search(section.prose)
            or any(line.lstrip().startswith(">") for line in section.prose.splitlines())
            or any(line.lstrip().startswith("#") for line in section.prose.splitlines())
        ):
            failures.append("transform_only_read_prose_failed")

    for section in candidate.sections:
        for skeleton_claim in section.claims:
            known_claims: list[SourceClaim] = []
            for ref in skeleton_claim.source_claim_refs:
                if ref not in claim_by_id:
                    unknown_claims.append(ref)
                else:
                    traced.append(ref)
                    known_claims.append(claim_by_id[ref])
            unknown_spans.extend(
                ref for ref in skeleton_claim.source_span_refs if ref not in span_ids
            )
            expected_spans = {
                ref for claim in known_claims for ref in claim.source_span_refs
            }
            if known_claims and set(skeleton_claim.source_span_refs) != expected_spans:
                failures.append("source_trace_mismatch")
            source_text = " ".join(claim.text for claim in known_claims)
            if known_claims and _numeric_witnesses(source_text) != _numeric_witnesses(
                skeleton_claim.text
            ):
                failures.append("numeric_fidelity_failed")
            if known_claims and _negation_count(source_text) != _negation_count(
                skeleton_claim.text
            ):
                failures.append("negation_fidelity_failed")
            for term in _marked_terms((skeleton_claim.text,)):
                if len(known_claims) != 1 or not _source_contains_term(
                    known_claims[0].text, term
                ):
                    failures.append("bold_term_source_authorization_failed")

    covered_vo = _ordered_known(traced, vo_ids)
    missing_vo = tuple(item for item in vo_ids if item not in set(traced))
    used_delta = _ordered_known(traced, delta_ids)
    if missing_vo:
        failures.append("declared_vo_claim_coverage_failed")
    if not used_delta:
        failures.append(DEPTH_LOSS)
    if unknown_claims:
        failures.append("unknown_claim_reference")
    if unknown_spans:
        failures.append("unknown_source_reference")
    if unknown_abilities:
        failures.append("unknown_ability_reference")
    try:
        parity = _marked_terms(tuple(section.prose for section in candidate.sections)) == tuple(
            term.term for term in candidate.bold_terms
        )
    except ValueError:
        parity = False
    if not parity:
        failures.append("bold_term_parity_failed")
    failures = list(dict.fromkeys(failures))
    return DeepDiveGateReceipt(
        authority_digest=_authority_digest(request),
        candidate_payload_digest=_candidate_payload_digest(
            candidate.sections, candidate.bold_terms
        ),
        declared_vo_claim_ids=vo_ids,
        declared_delta_claim_ids=delta_ids,
        declared_ability_ids=ability_order,
        declared_span_ids=tuple(span.span_id for span in request.source_spans),
        status="fail" if failures else "pass",
        covered_vo_claim_ids=covered_vo,
        missing_vo_claim_ids=missing_vo,
        used_delta_claim_ids=used_delta,
        unknown_claim_refs=tuple(dict.fromkeys(unknown_claims)),
        unknown_source_refs=tuple(dict.fromkeys(unknown_spans)),
        unknown_ability_refs=tuple(dict.fromkeys(unknown_abilities)),
        failures=tuple(failures),
    )


def _failed_result_disposition(
    candidate: DeepDiveWriterCandidate,
    receipt: DeepDiveGateReceipt,
) -> tuple[
    Literal["degraded", "unavailable"],
    Literal["deep_dive_skeleton_degraded", "deep_dive_skeleton_unavailable"],
    tuple[ResultLoss, ...],
]:
    unknown = bool(
        receipt.unknown_claim_refs
        or receipt.unknown_source_refs
        or receipt.unknown_ability_refs
    )
    if candidate.status == "unavailable" or unknown:
        status: Literal["degraded", "unavailable"] = "unavailable"
        marker: Literal[
            "deep_dive_skeleton_degraded", "deep_dive_skeleton_unavailable"
        ] = DEEP_DIVE_UNAVAILABLE_MARKER
    else:
        status = "degraded"
        marker = DEEP_DIVE_DEGRADED_MARKER
    if candidate.known_losses:
        losses: tuple[ResultLoss, ...] = candidate.known_losses
    elif unknown:
        losses = ("deep_dive_reference_validation_failed",)
    elif DEPTH_LOSS in receipt.failures:
        losses = (DEPTH_LOSS,)
    else:
        losses = ("deep_dive_skeleton_gate_failed",)
    return status, marker, losses


def offline_deep_dive_writer(
    request: DeepDiveSkeletonRequest,
) -> DeepDiveWriterCandidate:
    del request
    return DeepDiveSkeletonWriterResult(
        status="unavailable",
        sections=(),
        bold_terms=(),
        known_losses=("deep_dive_writer_unavailable",),
        marker=DEEP_DIVE_UNAVAILABLE_MARKER,
    )


def compose_deep_dive_skeleton(
    request: DeepDiveSkeletonRequest,
    writer: DeepDiveWriter | Callable[[DeepDiveSkeletonRequest], DeepDiveWriterCandidate],
) -> DeepDiveSkeletonResult:
    """Invoke an injected writer once, then independently validate and gate it."""
    if not isinstance(request, DeepDiveSkeletonRequest):
        raise TypeError("request must be a DeepDiveSkeletonRequest")
    # Defeat model_construct/model_copy bypasses before exposing authority to a writer.
    request = DeepDiveSkeletonRequest.model_validate(request.model_dump())
    candidate = writer(request)
    if not isinstance(candidate, DeepDiveSkeletonWriterResult):
        raise TypeError("writer must return DeepDiveSkeletonWriterResult")
    # Defeat model_construct/model_copy bypasses before trusting any invariant.
    candidate = DeepDiveSkeletonWriterResult.model_validate(candidate.model_dump())
    receipt = _gate(request, candidate)
    if candidate.status == "authored" and receipt.status == "pass":
        return DeepDiveSkeletonResult(
            status="authored",
            sections=candidate.sections,
            bold_terms=candidate.bold_terms,
            known_losses=(),
            marker=None,
            authority=request,
            candidate_snapshot=candidate,
            authority_digest=receipt.authority_digest,
            candidate_payload_digest=receipt.candidate_payload_digest,
            gate=receipt,
        )
    status, marker, losses = _failed_result_disposition(candidate, receipt)
    return DeepDiveSkeletonResult(
        status=status,
        sections=(),
        bold_terms=(),
        known_losses=losses,
        marker=marker,
        authority=request,
        candidate_snapshot=candidate,
        authority_digest=receipt.authority_digest,
        candidate_payload_digest=receipt.candidate_payload_digest,
        gate=receipt,
    )


__all__ = [
    "DEEP_DIVE_DEGRADED_MARKER",
    "DEEP_DIVE_UNAVAILABLE_MARKER",
    "BoldTermMarker",
    "DeepDiveAbilityInput",
    "DeepDiveAbilitySection",
    "DeepDiveGateReceipt",
    "DeepDiveSkeletonClaim",
    "DeepDiveSkeletonRequest",
    "DeepDiveSkeletonResult",
    "DeepDiveSkeletonWriterResult",
    "DeepDiveWriterCandidate",
    "DeepDiveWriter",
    "NarrationSourceSpan",
    "SourceClaim",
    "compose_deep_dive_skeleton",
    "deep_dive_authority_digest",
    "offline_deep_dive_writer",
]
