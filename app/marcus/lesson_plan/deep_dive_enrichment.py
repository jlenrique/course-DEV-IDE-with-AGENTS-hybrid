"""Strict contracts + pure A2 citation-COVERAGE gate for Deep Dive enrichment (37.2b).

The enrichment layer takes the authored 37.2a Deep Dive skeleton and ADDS
net-new depth drawn ONLY from the Ask-A cited knowledge pool. Every enriched
claim is typed at the writer boundary: it carries either inherited skeleton
``source_claim_refs`` (role ``skeleton``) or one-or-more pool ``citation_refs``
(role ``enrichment``) — never neither, never both.

HONESTY BOUNDARY (declared verbatim per AC2): the machine gate proves the
claim-typing / citation-binding / coverage arithmetic; whether an enriched
sentence *semantically follows from* its cited ``evidence_excerpt`` remains an
**operator prose spot-check WARN** (per amendment A2's fallback clause — this
story does not call the semantic audit G2-enforced). Ability coverage inherited
from the 38.1 token-match association is reported as "association-covered" —
it never implies semantic coverage the machine did not prove (J3).

MATRIX-ROW HONESTY NOTES (no silent overclaim):

* **Row a is defense-in-depth, not the primary reject.** An uncited
  enrichment-role claim is CONSTRUCTION-REJECTED by
  :class:`EnrichedDeepDiveClaim` (the typed writer boundary), so a candidate
  built through the models can never reach the gate with one. The gate's
  ``enrichment_claim_uncited`` row is RETAINED for hand-built payloads that
  bypass model construction (``model_construct`` / mutated JSON) — it is the
  second lock on the same door, not the door.
* **Row h subsumption ordering.** The A3 proper-superset re-run
  (``skeleton_vo_coverage_regressed``) is measured over the inherited
  ``source_claim_refs`` trace. Any mutation that drops a skeleton claim first
  trips ``skeleton_prose_not_preserved`` (skeleton claims must be reproduced
  verbatim, in order); row h therefore usually fires TOGETHER WITH the
  preservation failure rather than alone. Row h fires alone only for a
  hand-built payload that keeps claim text/ref shape but re-labels the trace.
  Both tags are recorded; neither is collapsed into the other.

M3: this module imports ``lesson_plan`` only — never ``app.marcus.orchestrator``.
The skeleton and the Ask-A pool cross the wall disk-mediated (workbook brief
sidecar + ``run.json`` research packet).
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any, Final, Literal, Protocol

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from app.marcus.lesson_plan.ask_a_enrichment import AskAKnowledgeEntryV1
from app.marcus.lesson_plan.deep_dive_projection import (
    BoldTermMarker,
    DeepDiveAbilitySection,
    DeepDiveSkeletonResult,
    _candidate_payload_digest,
    _canonical_digest,
    _marked_terms,
    _numeric_witnesses,
    _require_unique,
    _source_contains_term,
)
from app.marcus.lesson_plan.prework_artifact import read_workbook_brief
from app.marcus.lesson_plan.research_packet import (
    ResearchPacket,
    resolve_for_enrichment_pool,
)

EnrichmentClaimRole = Literal["skeleton", "enrichment"]
EnrichmentStatus = Literal["enriched", "degraded", "unavailable"]
EnrichmentGateStatus = Literal["pass", "fail"]
EnrichmentDisposition = Literal[
    "enriched",
    "degraded_pool_empty",
    "degraded_pool_unused",
    "unavailable",
    "failed",
]
EnrichmentWriterLoss = Literal[
    "deep_dive_enrichment_pool_empty",
    "deep_dive_enrichment_pool_unused",
    "deep_dive_enrichment_writer_unavailable",
    "deep_dive_enrichment_execution_failed",
]
EnrichmentResultLoss = Literal[
    "deep_dive_enrichment_pool_empty",
    "deep_dive_enrichment_pool_unused",
    "deep_dive_enrichment_writer_unavailable",
    "deep_dive_enrichment_execution_failed",
    "deep_dive_enrichment_reference_validation_failed",
    "deep_dive_enrichment_gate_failed",
]

DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER: Final[str] = "deep_dive_enrichment_degraded"
DEEP_DIVE_ENRICHMENT_UNAVAILABLE_MARKER: Final[str] = "deep_dive_enrichment_unavailable"
POOL_EMPTY_LOSS: Final[str] = "deep_dive_enrichment_pool_empty"
POOL_UNUSED_LOSS: Final[str] = "deep_dive_enrichment_pool_unused"
SKELETON_UNAVAILABLE_LOSS: Final[str] = "deep_dive_enrichment_skeleton_unavailable"
# A skeleton that EXISTS but did not author is a different honest state from a
# missing skeleton: its loss names the recorded skeleton status so the render
# note never claims "no authored skeleton" about a present-but-degraded one.
SKELETON_NOT_AUTHORED_LOSS_PREFIX: Final[str] = (
    "deep_dive_enrichment_skeleton_not_authored"
)
SKELETON_ABSENT_LOSSES: Final[frozenset[str]] = frozenset(
    {
        SKELETON_UNAVAILABLE_LOSS,
        f"{SKELETON_NOT_AUTHORED_LOSS_PREFIX}_degraded",
        f"{SKELETON_NOT_AUTHORED_LOSS_PREFIX}_unavailable",
    }
)


def skeleton_not_authored_loss(skeleton_status: str) -> str:
    """The typed loss naming a present-but-non-authored skeleton's state."""
    loss = f"{SKELETON_NOT_AUTHORED_LOSS_PREFIX}_{skeleton_status}"
    if loss not in SKELETON_ABSENT_LOSSES:
        raise ValueError(f"unknown non-authored skeleton status: {skeleton_status!r}")
    return loss


CHECK_WRITER_STUB_LOSS: Final[str] = "check_writer_not_yet_wired"
REFLECTION_WRITER_STUB_LOSS: Final[str] = "reflection_writer_not_yet_wired"
OPERATOR_SEMANTIC_ENRICHMENT_WARNING: Final[str] = (
    "semantic_claim_evidence_support_and_association_coverage_require_operator_spot_check"
)

# Inline citation markers render as ``[ask-a-cite-###]`` immediately after the
# sentence they support and are excluded from bold-parity text.
CITATION_MARKER_RE: Final[re.Pattern[str]] = re.compile(r"\[(ask-a-cite-[0-9]{3})\]")
_TRAILING_MARKER_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:\s*\[ask-a-cite-[0-9]{3}\])+\s*$"
)
_HEX64_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
# R9: a reference line links to https://doi.org/ ONLY when the source_id is
# DOI-shaped; anything else renders as a source_ref-only entry (no fabricated
# link). Shape per the DOI handbook prefix grammar: 10.<4-9 digits>/<suffix>.
_DOI_SHAPE_RE: Final[re.Pattern[str]] = re.compile(r"^10\.\d{4,9}/\S+$")

# Contribution coordinates — LOCAL literals, deliberately NOT imported from
# app.marcus.orchestrator (Contract M3; mirrors research_packet's discipline).
WORKBOOK_REVIEW_NODE_ID_LITERAL: Final[str] = "07W.3"
WORKBOOK_REVIEW_SPECIALIST_ID_LITERAL: Final[str] = "workbook_review"


def _non_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("value must contain non-whitespace text")
    return value


def _single_line(value: str) -> str:
    if any(mark in value for mark in ("\n", "\r", " ", " ")):
        raise ValueError("value must be one line")
    return value


def _sha256_digest(value: str) -> str:
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError("value must be a canonical sha256 digest")
    return value


def _bare_hex_digest(value: str) -> str:
    if not _HEX64_RE.fullmatch(value):
        raise ValueError("value must be a bare 64-hex sha256 digest")
    return value


NonBlankStr = Annotated[str, AfterValidator(_non_blank)]
NonBlankLine = Annotated[str, AfterValidator(_non_blank), AfterValidator(_single_line)]
Sha256Digest = Annotated[str, AfterValidator(_sha256_digest)]
BareHexDigest = Annotated[str, AfterValidator(_bare_hex_digest)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        validate_default=True,
    )


class DeepDiveEnrichmentAuthorityError(ValueError):
    """Raised when the run substrate cannot yield an enrichment request."""


class DeepDiveSkeletonMissingError(DeepDiveEnrichmentAuthorityError):
    """The workbook brief carries NO Deep Dive skeleton at all (typed routing, R5)."""


class DeepDiveSkeletonNotAuthoredError(DeepDiveEnrichmentAuthorityError):
    """A skeleton EXISTS but its status is not ``authored`` (typed routing, R5).

    Carries ``skeleton_status`` so callers can name the honest degraded state
    instead of routing to the "no authored skeleton" note.
    """

    def __init__(self, skeleton_status: str) -> None:
        self.skeleton_status = skeleton_status
        super().__init__(
            f"enrichment requires an authored skeleton; status={skeleton_status!r}"
        )


def _validate_json_payload(model: type[_StrictModel], payload: object) -> Any:
    """Validate a JSON-decoded payload through the strict JSON path.

    The strict models reject Python ``list`` where the contract declares
    ``tuple``; routing through ``model_validate_json`` keeps strictness while
    accepting canonical JSON arrays (mirrors the research_packet idiom).
    """
    return model.model_validate_json(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False),
        strict=True,
    )


def prose_citation_markers(text: str) -> tuple[str, ...]:
    """Ordered inline citation IDs measured from prose (never writer-asserted)."""
    return tuple(CITATION_MARKER_RE.findall(text))


def strip_citation_markers(text: str) -> str:
    """Remove inline citation markers (they are excluded from bold-parity text)."""
    return CITATION_MARKER_RE.sub("", text)


# ---------------------------------------------------------------------------
# Request side — digest-bound skeleton + pool + D2.4 overlay-covered input
# ---------------------------------------------------------------------------


class OverlayCoveredObjective(_StrictModel):
    objective_id: NonBlankLine
    statement: str


class DeepDiveOverlayCoveredInputV1(_StrictModel):
    """D2.4 MERGE authoring-time dedup INPUT (party record §D2.4).

    The overlay's covered-LO/fact list is an INPUT the deep-dive authoring
    flexes around; residual duplication is an operator spot-check at governed
    run A — declared honestly, never claimed machine-caught.
    """

    schema_version: Literal["deep-dive-overlay-covered-input.v1"] = (
        "deep-dive-overlay-covered-input.v1"
    )
    card_present: bool
    covered_learning_objectives: tuple[OverlayCoveredObjective, ...]
    covered_exercise_facts: tuple[str, ...]

    @model_validator(mode="after")
    def _honest_empty(self) -> DeepDiveOverlayCoveredInputV1:
        if not self.card_present and (
            self.covered_learning_objectives or self.covered_exercise_facts
        ):
            raise ValueError("absent enrichment card must project an honest-empty overlay input")
        _require_unique(
            tuple(item.objective_id for item in self.covered_learning_objectives),
            "overlay objective IDs",
        )
        return self


class DeepDiveSkeletonBindingV1(_StrictModel):
    """The authored 37.2a skeleton bound by its own digests (join by digest, never prose)."""

    schema_version: Literal["deep-dive-skeleton-binding.v1"] = "deep-dive-skeleton-binding.v1"
    authority_digest: Sha256Digest
    candidate_payload_digest: Sha256Digest
    sections: tuple[DeepDiveAbilitySection, ...]
    bold_terms: tuple[BoldTermMarker, ...]
    declared_vo_claim_ids: tuple[NonBlankLine, ...]
    covered_vo_claim_ids: tuple[NonBlankLine, ...]

    @model_validator(mode="after")
    def _bound(self) -> DeepDiveSkeletonBindingV1:
        if not self.sections:
            raise ValueError("skeleton binding requires authored sections")
        _require_unique(
            tuple(section.ability_id for section in self.sections), "skeleton ability IDs"
        )
        _require_unique(
            tuple(
                claim.skeleton_claim_id
                for section in self.sections
                for claim in section.claims
            ),
            "skeleton claim IDs",
        )
        _require_unique(tuple(term.term for term in self.bold_terms), "skeleton bold terms")
        if self.candidate_payload_digest != _candidate_payload_digest(
            self.sections, self.bold_terms
        ):
            raise ValueError("skeleton binding requires the recomputed candidate payload digest")
        if not set(self.covered_vo_claim_ids) <= set(self.declared_vo_claim_ids):
            raise ValueError("covered VO claim IDs must be declared VO claim IDs")
        return self

    @property
    def source_claim_ref_set(self) -> frozenset[str]:
        return frozenset(
            ref
            for section in self.sections
            for claim in section.claims
            for ref in claim.source_claim_refs
        )


def skeleton_binding_from_result(result: DeepDiveSkeletonResult) -> DeepDiveSkeletonBindingV1:
    """Project the authored skeleton result into its digest-bound enrichment view."""
    result = DeepDiveSkeletonResult.model_validate(result.model_dump())
    if result.status != "authored":
        raise DeepDiveSkeletonNotAuthoredError(result.status)
    return DeepDiveSkeletonBindingV1(
        authority_digest=result.authority_digest,
        candidate_payload_digest=result.candidate_payload_digest,
        sections=result.sections,
        bold_terms=result.bold_terms,
        declared_vo_claim_ids=result.gate.declared_vo_claim_ids,
        covered_vo_claim_ids=result.gate.covered_vo_claim_ids,
    )


class DeepDiveEnrichmentRequestV1(_StrictModel):
    """The digest-bound enrichment request (AC1).

    Binds (a) the authored skeleton by ``authority_digest`` +
    ``candidate_payload_digest``, (b) the Ask-A pool identity by packet digest +
    ``scope_digest``, (c) the ordered usable pool rows as the REAL
    :class:`AskAKnowledgeEntryV1` (amendment A2 — no re-typed subset; T7/T8
    exclusion is model-enforced by the entry's tier Literal), and (d) the D2.4
    overlay-covered input. ``excluded_citation_ids`` names citation IDs the
    upstream packet recorded as excluded/known-loss rows so the gate can reject
    them DISTINGUISHABLY from invented IDs (amendment M2a); the current 38.1
    producer records exclusions by raw-row index without citation IDs, so this
    tuple is empty on today's live packets.
    """

    schema_version: Literal["deep-dive-enrichment-request.v1"] = "deep-dive-enrichment-request.v1"
    skeleton: DeepDiveSkeletonBindingV1
    pool_packet_digest: BareHexDigest
    pool_status: Literal["absent", "empty", "ready", "degraded"]
    pool_scope_digest: Sha256Digest | None
    pool_rows: tuple[AskAKnowledgeEntryV1, ...]
    pool_known_losses: tuple[NonBlankLine, ...]
    excluded_citation_ids: tuple[NonBlankLine, ...] = ()
    intake_covered_ability_ids: tuple[NonBlankLine, ...] = ()
    intake_uncovered_ability_ids: tuple[NonBlankLine, ...] = ()
    overlay_covered: DeepDiveOverlayCoveredInputV1
    request_digest: Sha256Digest

    @model_validator(mode="after")
    def _bound(self) -> DeepDiveEnrichmentRequestV1:
        _require_unique(tuple(row.citation_id for row in self.pool_rows), "pool citation IDs")
        _require_unique(self.excluded_citation_ids, "excluded citation IDs")
        if set(self.excluded_citation_ids) & {row.citation_id for row in self.pool_rows}:
            raise ValueError("excluded citation IDs cannot also be usable pool rows")
        if self.pool_rows:
            if self.pool_status not in {"ready", "degraded"}:
                raise ValueError("usable pool rows require a ready/degraded packet status")
            if self.pool_scope_digest is None:
                raise ValueError("usable pool rows require the bound scope digest")
        elif self.pool_status in {"ready", "degraded"}:
            raise ValueError("ready/degraded packet status requires usable pool rows")
        expected = _canonical_digest(
            self.model_dump(mode="json", exclude={"request_digest"})
        )
        if self.request_digest != expected:
            raise ValueError("enrichment request digest mismatch")
        return self


def enrichment_request_digest(payload: dict[str, Any]) -> str:
    """Canonical digest over the request payload minus its own digest field."""
    reduced = {key: value for key, value in payload.items() if key != "request_digest"}
    return _canonical_digest(reduced)


# ---------------------------------------------------------------------------
# Writer-side candidate — typed claim boundary
# ---------------------------------------------------------------------------


class EnrichedDeepDiveClaim(_StrictModel):
    """One enriched claim, typed at the writer boundary (AC1).

    Role ``skeleton``: inherits the skeleton claim's ``source_claim_refs``;
    ``citation_refs`` must be empty. Role ``enrichment``: carries one-or-more
    pool ``citation_refs``; ``source_claim_refs`` must be empty. Never neither,
    never both.
    """

    enriched_claim_id: NonBlankLine
    text: NonBlankStr
    role: EnrichmentClaimRole
    source_claim_refs: tuple[NonBlankLine, ...]
    citation_refs: tuple[NonBlankLine, ...]

    @model_validator(mode="after")
    def _typed_boundary(self) -> EnrichedDeepDiveClaim:
        _require_unique(self.source_claim_refs, "claim refs")
        _require_unique(self.citation_refs, "citation refs")
        if self.role == "skeleton":
            if not self.source_claim_refs:
                raise ValueError("skeleton-role claim requires inherited source claim refs")
            if self.citation_refs:
                raise ValueError("skeleton-role claim cannot carry citation refs")
        else:
            if not self.citation_refs:
                raise ValueError("enrichment-role claim requires at least one citation ref")
            if self.source_claim_refs:
                raise ValueError("enrichment-role claim cannot carry source claim refs")
        return self


class EnrichedDeepDiveSection(_StrictModel):
    ability_id: NonBlankLine
    prose: NonBlankStr
    claims: tuple[EnrichedDeepDiveClaim, ...]

    @model_validator(mode="after")
    def _has_claims(self) -> EnrichedDeepDiveSection:
        if not self.claims:
            raise ValueError("enriched section requires at least one claim")
        return self


class DeepDiveEnrichedWriterResult(_StrictModel):
    """Writer-side candidate; pool/citation coverage is gated by the pure gate."""

    status: EnrichmentStatus
    sections: tuple[EnrichedDeepDiveSection, ...]
    bold_terms: tuple[BoldTermMarker, ...]
    known_losses: tuple[EnrichmentWriterLoss, ...]
    marker: NonBlankLine | None

    @model_validator(mode="after")
    def _honest_local_shape(self) -> DeepDiveEnrichedWriterResult:
        if self.status == "enriched":
            if not self.sections:
                raise ValueError("enriched candidate requires sections")
            if self.known_losses or self.marker is not None:
                raise ValueError("enriched candidate cannot carry losses or marker")
            _require_unique(
                tuple(
                    claim.enriched_claim_id
                    for section in self.sections
                    for claim in section.claims
                ),
                "enriched claim IDs",
            )
            _require_unique(tuple(term.term for term in self.bold_terms), "bold terms")
            stripped = tuple(
                strip_citation_markers(section.prose) for section in self.sections
            )
            if _marked_terms(stripped) != tuple(term.term for term in self.bold_terms):
                raise ValueError("bold marker/metadata mismatch")
        else:
            if self.sections or self.bold_terms:
                raise ValueError("non-enriched candidate cannot carry prose or terms")
            if not self.known_losses or self.marker is None:
                raise ValueError("non-enriched candidate requires losses and marker")
            if len(self.known_losses) != 1:
                raise ValueError("non-enriched candidate requires exactly one typed loss")
            loss = self.known_losses[0]
            if self.status == "degraded":
                if loss not in {POOL_EMPTY_LOSS, POOL_UNUSED_LOSS}:
                    raise ValueError("degraded candidate requires a pool-honesty loss")
                if self.marker != DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER:
                    raise ValueError("degraded candidate requires its canonical marker")
            else:
                if loss not in {
                    "deep_dive_enrichment_writer_unavailable",
                    "deep_dive_enrichment_execution_failed",
                }:
                    raise ValueError("unavailable candidate requires a writer loss")
                if self.marker != DEEP_DIVE_ENRICHMENT_UNAVAILABLE_MARKER:
                    raise ValueError("unavailable candidate requires its canonical marker")
        return self


class DeepDiveEnrichmentWriter(Protocol):
    """Injected semantic writer returning an untrusted, pre-gate candidate."""

    def __call__(self, request: DeepDiveEnrichmentRequestV1) -> DeepDiveEnrichedWriterResult: ...


def offline_deep_dive_enrichment_writer(
    request: DeepDiveEnrichmentRequestV1,
) -> DeepDiveEnrichedWriterResult:
    """Deterministic offline stub: honest non-authored (goldens run without a model)."""
    del request
    return DeepDiveEnrichedWriterResult(
        status="unavailable",
        sections=(),
        bold_terms=(),
        known_losses=("deep_dive_enrichment_writer_unavailable",),
        marker=DEEP_DIVE_ENRICHMENT_UNAVAILABLE_MARKER,
    )


# ---------------------------------------------------------------------------
# The A2 citation-COVERAGE gate — pure and deterministic (the teeth)
# ---------------------------------------------------------------------------


class EnrichedClaimBinding(_StrictModel):
    enriched_claim_id: NonBlankLine
    ability_id: NonBlankLine
    role: EnrichmentClaimRole
    source_claim_refs: tuple[NonBlankLine, ...]
    citation_refs: tuple[NonBlankLine, ...]


class DeepDiveEnrichmentGateReceipt(_StrictModel):
    """Inspectable A2 receipt: counts + ordered ID lists — never only a Boolean.

    ``used_citation_ids`` is MEASURED FROM PROSE markers (row g:
    measured-not-asserted); ``prose_association_covered_ability_ids`` is the
    per-ability coverage measured from prose-claim placement joined to the pool
    rows' ``supports_ability_ids`` (amendment M1); the ``intake_*`` lists carry
    the upstream 38.1 token-match "association-covered" verdicts verbatim (J3
    wording — never semantic coverage).

    Row-honesty notes (R17): an ``enrichment_claim_uncited`` failure in this
    receipt can only come from a hand-built payload — the typed claim model
    construction-rejects that shape (row a is defense-in-depth). A
    ``skeleton_vo_coverage_regressed`` failure normally appears TOGETHER WITH
    ``skeleton_prose_not_preserved`` (row h is ordered after, and usually
    subsumed by, the verbatim-preservation check); both are recorded.
    """

    gate_version: Literal["deep-dive-enrichment-gate.v1"] = "deep-dive-enrichment-gate.v1"
    request_digest: Sha256Digest
    skeleton_authority_digest: Sha256Digest
    skeleton_candidate_digest: Sha256Digest
    pool_packet_digest: BareHexDigest
    pool_scope_digest: Sha256Digest | None
    status: EnrichmentGateStatus
    disposition: EnrichmentDisposition
    available_citation_ids: tuple[NonBlankLine, ...]
    used_citation_ids: tuple[NonBlankLine, ...]
    unused_citation_ids: tuple[NonBlankLine, ...]
    available_citation_count: int = Field(ge=0)
    used_citation_count: int = Field(ge=0)
    unused_citation_count: int = Field(ge=0)
    intake_covered_ability_ids: tuple[NonBlankLine, ...]
    intake_uncovered_ability_ids: tuple[NonBlankLine, ...]
    prose_association_covered_ability_ids: tuple[NonBlankLine, ...]
    prose_association_uncovered_ability_ids: tuple[NonBlankLine, ...]
    claim_bindings: tuple[EnrichedClaimBinding, ...]
    unknown_citation_refs: tuple[NonBlankLine, ...]
    excluded_citation_refs: tuple[NonBlankLine, ...]
    cross_scope_citation_refs: tuple[NonBlankLine, ...]
    failures: tuple[NonBlankLine, ...]
    operator_warnings: tuple[NonBlankLine, ...] = (OPERATOR_SEMANTIC_ENRICHMENT_WARNING,)

    @model_validator(mode="after")
    def _reconciled(self) -> DeepDiveEnrichmentGateReceipt:
        if (self.status == "pass") == bool(self.failures):
            raise ValueError("gate status must reconcile with failures")
        _require_unique(self.failures, "gate failures")
        for values, label in (
            (self.available_citation_ids, "available citation IDs"),
            (self.used_citation_ids, "used citation IDs"),
            (self.unused_citation_ids, "unused citation IDs"),
            (self.unknown_citation_refs, "unknown citation diagnostics"),
            (self.excluded_citation_refs, "excluded citation diagnostics"),
            (self.cross_scope_citation_refs, "cross-scope citation diagnostics"),
        ):
            _require_unique(values, label)
        # M2c arithmetic invariant: used + unused == available, as an exact
        # order-preserving partition of the pool.
        if self.available_citation_count != len(self.available_citation_ids):
            raise ValueError("available citation count mismatch")
        if self.used_citation_count != len(self.used_citation_ids):
            raise ValueError("used citation count mismatch")
        if self.unused_citation_count != len(self.unused_citation_ids):
            raise ValueError("unused citation count mismatch")
        if self.used_citation_count + self.unused_citation_count != self.available_citation_count:
            raise ValueError("used + unused must equal available")
        used = set(self.used_citation_ids)
        unused = set(self.unused_citation_ids)
        if used & unused:
            raise ValueError("used and unused citation IDs must be disjoint")
        if used | unused != set(self.available_citation_ids):
            raise ValueError("used and unused citation IDs must partition the pool")
        if self.used_citation_ids != tuple(
            item for item in self.available_citation_ids if item in used
        ) or self.unused_citation_ids != tuple(
            item for item in self.available_citation_ids if item in unused
        ):
            raise ValueError("citation partition must preserve pool order")
        if set(self.prose_association_covered_ability_ids) & set(
            self.prose_association_uncovered_ability_ids
        ):
            raise ValueError("prose ability coverage must be disjoint")
        diagnostic_pairs = (
            (self.unknown_citation_refs, "unknown_citation_reference"),
            (self.excluded_citation_refs, "excluded_citation_reference"),
            (self.cross_scope_citation_refs, "cross_scope_citation"),
        )
        for values, failure in diagnostic_pairs:
            if bool(values) != (failure in self.failures):
                raise ValueError(f"{failure} diagnostics must reconcile with failures")
        if self.disposition == "enriched" and (self.status != "pass" or not used):
            raise ValueError("enriched disposition requires a passing gate with used rows")
        if self.disposition == "failed" and self.status != "fail":
            raise ValueError("failed disposition requires a failing gate")
        if self.disposition != "failed" and self.status == "fail":
            raise ValueError("failing gate requires the failed disposition")
        if self.disposition == "degraded_pool_empty" and self.available_citation_ids:
            raise ValueError("degraded_pool_empty requires an empty pool")
        if self.disposition == "degraded_pool_unused" and (
            not self.available_citation_ids or used
        ):
            raise ValueError("degraded_pool_unused requires unused nonempty pool")
        if self.operator_warnings != (OPERATOR_SEMANTIC_ENRICHMENT_WARNING,):
            raise ValueError("gate requires the canonical operator warning")
        return self


def _trailing_markers_only(text: str) -> bool:
    """True when every inline marker in the text sits in one trailing marker block."""
    stripped = _TRAILING_MARKER_RE.sub("", text)
    return not CITATION_MARKER_RE.search(stripped)


def _ordered_by_pool(ids: set[str], pool_order: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(item for item in pool_order if item in ids)


def deep_dive_enrichment_gate(
    request: DeepDiveEnrichmentRequestV1, candidate: DeepDiveEnrichedWriterResult
) -> DeepDiveEnrichmentGateReceipt:
    """Pure A2 coverage gate over the full amended matrix (rows a–i, d′, i-a, i-b).

    Row-honesty notes (mirrors the module docstring): row a
    (``enrichment_claim_uncited``) is defense-in-depth — the typed claim model
    construction-rejects that shape, so this row only fires on hand-built
    payloads. Row h (``skeleton_vo_coverage_regressed``) is ordered AFTER the
    verbatim-preservation check and is usually subsumed by
    ``skeleton_prose_not_preserved``; both tags are recorded when both apply.
    This gate sees only the request + candidate; execution-receipt honesty
    (e.g. a live provider call that succeeded yet claims writer-unavailable —
    ``unavailable_shape_dishonest``) is enforced at the receipt-aware seam,
    :class:`WorkbookReviewContributionV1`.
    """
    pool_order = tuple(row.citation_id for row in request.pool_rows)
    pool_by_id = {row.citation_id: row for row in request.pool_rows}
    excluded_ids = set(request.excluded_citation_ids)
    skeleton = request.skeleton
    skeleton_ability_order = tuple(section.ability_id for section in skeleton.sections)
    skeleton_by_ability = {section.ability_id: section for section in skeleton.sections}
    skeleton_ref_set = skeleton.source_claim_ref_set

    failures: list[str] = []
    unknown_refs: list[str] = []
    excluded_refs: list[str] = []
    cross_scope_refs: list[str] = []
    claim_bindings: list[EnrichedClaimBinding] = []
    prose_used: set[str] = set()
    prose_covered_abilities: set[str] = set()
    # R16: claim-LOCAL bold-term trace — a new bold term must be supported by
    # a row cited by the CLAIM that contains the term (no document-global
    # fallback; cross-claim laundering fails).
    new_term_claim_rows: dict[str, list[AskAKnowledgeEntryV1]] = {}

    if candidate.status in {"degraded", "unavailable"}:
        loss = candidate.known_losses[0]
        if loss == POOL_EMPTY_LOSS and request.pool_rows:
            failures.append("degraded_shape_dishonest")
        if loss == POOL_UNUSED_LOSS and not request.pool_rows:
            failures.append("degraded_shape_dishonest")
        if failures:
            disposition: EnrichmentDisposition = "failed"
        elif loss == POOL_EMPTY_LOSS:
            disposition = "degraded_pool_empty"
        elif loss == POOL_UNUSED_LOSS:
            disposition = "degraded_pool_unused"
        else:
            disposition = "unavailable"
    else:
        section_abilities = tuple(section.ability_id for section in candidate.sections)
        unknown_abilities = tuple(
            item for item in section_abilities if item not in set(skeleton_ability_order)
        )
        if unknown_abilities:
            failures.append("unknown_ability_reference")
        if section_abilities != skeleton_ability_order:
            failures.append("ability_order_mismatch")
        if len(set(section_abilities)) != len(section_abilities):
            failures.append("duplicate_ability_section")

        for section in candidate.sections:
            skeleton_section = skeleton_by_ability.get(section.ability_id)
            skeleton_role = tuple(c for c in section.claims if c.role == "skeleton")
            enrichment_role = tuple(c for c in section.claims if c.role == "enrichment")
            for claim in section.claims:
                claim_bindings.append(
                    EnrichedClaimBinding(
                        enriched_claim_id=claim.enriched_claim_id,
                        ability_id=section.ability_id,
                        role=claim.role,
                        source_claim_refs=claim.source_claim_refs,
                        citation_refs=claim.citation_refs,
                    )
                )
            # Row i-b: skeleton-side phantom refs — refs naming claim IDs absent
            # from the digest-bound skeleton's claim set FAIL distinguishably.
            for claim in skeleton_role:
                if any(ref not in skeleton_ref_set for ref in claim.source_claim_refs):
                    failures.append("skeleton_claim_phantom_reference")
                if CITATION_MARKER_RE.search(claim.text):
                    failures.append("stray_citation_marker_in_skeleton_claim")
            # Enrichment may only ADD: the skeleton claims are preserved verbatim
            # (text + inherited refs), in skeleton order, ahead of any additions.
            if skeleton_section is None:
                preserved = False
            else:
                preserved = tuple(
                    (claim.text, claim.source_claim_refs) for claim in skeleton_role
                ) == tuple(
                    (claim.text, claim.source_claim_refs)
                    for claim in skeleton_section.claims
                )
            if not preserved:
                failures.append("skeleton_prose_not_preserved")
            for claim in enrichment_role:
                if not claim.citation_refs:
                    # Row a defense-in-depth: construction-rejected by the typed
                    # claim model; this gate row is retained for hand-built
                    # payloads only (see module docstring).
                    failures.append("enrichment_claim_uncited")
                    continue
                # R11: a claim whose text minus its citation markers is
                # empty/whitespace carries no sentence — reject.
                if not strip_citation_markers(claim.text).strip():
                    failures.append("enrichment_claim_empty_sentence")
                markers = prose_citation_markers(claim.text)
                if markers != claim.citation_refs or not _trailing_markers_only(claim.text):
                    failures.append("citation_declaration_prose_mismatch")
                cited_known: list[AskAKnowledgeEntryV1] = []
                for ref in claim.citation_refs:
                    row = pool_by_id.get(ref)
                    if row is None:
                        if ref in excluded_ids:
                            # M2a: excluded/known-loss row — DISTINGUISHABLE
                            # from an invented ID.
                            if ref not in excluded_refs:
                                excluded_refs.append(ref)
                        elif ref not in unknown_refs:
                            unknown_refs.append(ref)
                        continue
                    # Row c: cross-run/cross-packet citation.
                    if (
                        request.pool_scope_digest is None
                        or row.scope_digest != request.pool_scope_digest
                    ):
                        if ref not in cross_scope_refs:
                            cross_scope_refs.append(ref)
                        continue
                    cited_known.append(row)
                for marker_id in markers:
                    if marker_id in pool_by_id:
                        prose_used.add(marker_id)
                # R16 claim-local trace substrate: terms bolded WITHIN this
                # claim may only trace to rows cited BY this claim.
                try:
                    claim_terms = _marked_terms(
                        (strip_citation_markers(claim.text),)
                    )
                except ValueError:
                    claim_terms = ()  # malformed markup already fails parity
                for claim_term in claim_terms:
                    new_term_claim_rows.setdefault(claim_term, []).extend(cited_known)
                # R8 (per-row): EVERY cited row must support the section's
                # ability — a non-supporting EXTRA citation fails with a tag
                # distinct from the all-rows case below.
                if any(
                    section.ability_id not in row.supports_ability_ids
                    for row in cited_known
                ):
                    failures.append("citation_ability_mismatch")
                # Row i-a (all-rows case): no cited row supports the ability.
                if cited_known and all(
                    section.ability_id not in row.supports_ability_ids for row in cited_known
                ):
                    failures.append("enrichment_ability_attribution_failed")
                if cited_known and section.ability_id in {
                    ability
                    for row in cited_known
                    for ability in row.supports_ability_ids
                }:
                    prose_covered_abilities.add(section.ability_id)
                # Numeric fidelity over enriched prose: every numeric witness in
                # the enrichment sentence must appear among its cited evidence
                # excerpts' witnesses (37.2a witness extractor re-run).
                if cited_known:
                    excerpt_witnesses = list(
                        _numeric_witnesses(
                            " ".join(row.evidence_excerpt for row in cited_known)
                        )
                    )
                    for witness in _numeric_witnesses(strip_citation_markers(claim.text)):
                        if witness in excerpt_witnesses:
                            excerpt_witnesses.remove(witness)
                        else:
                            failures.append("enrichment_numeric_fidelity_failed")
                            break
            # Prose composition: measured, not asserted.
            if section.prose != " ".join(claim.text for claim in section.claims):
                failures.append("prose_claim_composition_failed")

        # Row h: A3 proper-superset re-run — every 37.2a-covered VO claim must
        # remain in the enriched trace.
        enriched_trace = {
            ref
            for section in candidate.sections
            for claim in section.claims
            if claim.role == "skeleton"
            for ref in claim.source_claim_refs
        }
        if any(ref not in enriched_trace for ref in skeleton.covered_vo_claim_ids):
            failures.append("skeleton_vo_coverage_regressed")

        # AC4 bold-term continuity: skeleton terms preserved EXACTLY; new terms
        # only when traced to a used pool citation; parity re-run over the
        # enriched prose with citation markers excluded.
        candidate_terms = tuple(term.term for term in candidate.bold_terms)
        try:
            parity = (
                _marked_terms(
                    tuple(strip_citation_markers(s.prose) for s in candidate.sections)
                )
                == candidate_terms
            )
        except ValueError:
            parity = False
        if not parity:
            failures.append("bold_term_parity_failed")
        skeleton_terms = tuple(term.term for term in skeleton.bold_terms)
        if any(term not in set(candidate_terms) for term in skeleton_terms):
            failures.append("skeleton_bold_terms_not_preserved")
        # R16: a NEW bold term traces CLAIM-LOCALLY — it must appear in the
        # evidence_excerpt of a row cited by the claim containing the term
        # (document-global fallback removed; cross-claim laundering fails).
        for term in candidate_terms:
            if term in set(skeleton_terms):
                continue
            claim_local_rows = new_term_claim_rows.get(term, [])
            if not any(
                _source_contains_term(row.evidence_excerpt, term)
                for row in claim_local_rows
            ):
                failures.append("untraced_new_bold_term")
        if unknown_refs:
            failures.append("unknown_citation_reference")
        if excluded_refs:
            failures.append("excluded_citation_reference")
        if cross_scope_refs:
            failures.append("cross_scope_citation")
        # Row e: cannot claim enrichment it didn't use.
        if not prose_used:
            failures.append("enrichment_claimed_without_pool_use")
        disposition = "enriched" if not failures else "failed"

    failures = list(dict.fromkeys(failures))
    used_ids = _ordered_by_pool(prose_used, pool_order)
    unused_ids = tuple(item for item in pool_order if item not in prose_used)
    prose_covered = tuple(
        ability for ability in skeleton_ability_order if ability in prose_covered_abilities
    )
    prose_uncovered = tuple(
        ability for ability in skeleton_ability_order if ability not in prose_covered_abilities
    )
    return DeepDiveEnrichmentGateReceipt(
        request_digest=request.request_digest,
        skeleton_authority_digest=skeleton.authority_digest,
        skeleton_candidate_digest=skeleton.candidate_payload_digest,
        pool_packet_digest=request.pool_packet_digest,
        pool_scope_digest=request.pool_scope_digest,
        status="fail" if failures else "pass",
        disposition=disposition,
        available_citation_ids=pool_order,
        used_citation_ids=used_ids,
        unused_citation_ids=unused_ids,
        available_citation_count=len(pool_order),
        used_citation_count=len(used_ids),
        unused_citation_count=len(unused_ids),
        intake_covered_ability_ids=request.intake_covered_ability_ids,
        intake_uncovered_ability_ids=request.intake_uncovered_ability_ids,
        prose_association_covered_ability_ids=prose_covered,
        prose_association_uncovered_ability_ids=prose_uncovered,
        claim_bindings=tuple(claim_bindings),
        unknown_citation_refs=tuple(unknown_refs),
        excluded_citation_refs=tuple(excluded_refs),
        cross_scope_citation_refs=tuple(cross_scope_refs),
        failures=tuple(failures),
    )


# ---------------------------------------------------------------------------
# Result — authored/degraded/unavailable status↔payload↔loss reconciliation
# ---------------------------------------------------------------------------


def _failed_enrichment_disposition(
    receipt: DeepDiveEnrichmentGateReceipt,
) -> tuple[Literal["degraded", "unavailable"], str, tuple[EnrichmentResultLoss, ...]]:
    unknown = bool(
        receipt.unknown_citation_refs
        or receipt.excluded_citation_refs
        or receipt.cross_scope_citation_refs
    )
    if unknown:
        return (
            "unavailable",
            DEEP_DIVE_ENRICHMENT_UNAVAILABLE_MARKER,
            ("deep_dive_enrichment_reference_validation_failed",),
        )
    return (
        "degraded",
        DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER,
        ("deep_dive_enrichment_gate_failed",),
    )


class DeepDiveEnrichedResultV1(_StrictModel):
    """Post-gate enrichment result, revalidated end-to-end on every load."""

    schema_version: Literal["deep-dive-enriched-result.v1"] = "deep-dive-enriched-result.v1"
    status: EnrichmentStatus
    sections: tuple[EnrichedDeepDiveSection, ...]
    bold_terms: tuple[BoldTermMarker, ...]
    known_losses: tuple[EnrichmentResultLoss, ...]
    marker: NonBlankLine | None
    request: DeepDiveEnrichmentRequestV1
    candidate_snapshot: DeepDiveEnrichedWriterResult
    enriched_payload_digest: Sha256Digest
    gate: DeepDiveEnrichmentGateReceipt

    @model_validator(mode="after")
    def _honest_result(self) -> DeepDiveEnrichedResultV1:
        request = DeepDiveEnrichmentRequestV1.model_validate(self.request.model_dump())
        candidate = DeepDiveEnrichedWriterResult.model_validate(
            self.candidate_snapshot.model_dump()
        )
        recomputed = deep_dive_enrichment_gate(request, candidate)
        if self.gate != recomputed:
            raise ValueError("result gate must equal the recomputed gate receipt")
        if self.enriched_payload_digest != _candidate_payload_digest(
            # DeepDiveAbilitySection/EnrichedDeepDiveSection dump identically
            # through the shared helper's json projection.
            self.sections,  # type: ignore[arg-type]
            self.bold_terms,
        ):
            raise ValueError("result requires the recomputed enriched payload digest")
        if self.status == "enriched":
            if not self.sections or self.known_losses or self.marker is not None:
                raise ValueError("enriched result requires prose and no loss state")
            if candidate.status != "enriched" or recomputed.status != "pass":
                raise ValueError("enriched result requires a passing enriched candidate")
            if self.sections != candidate.sections or self.bold_terms != candidate.bold_terms:
                raise ValueError("enriched result payload must equal the candidate snapshot")
        else:
            if self.sections or self.bold_terms or not self.known_losses or self.marker is None:
                raise ValueError("non-enriched result requires empty payload and loss state")
            if len(self.known_losses) != 1:
                raise ValueError("non-enriched result requires exactly one typed loss")
            if recomputed.status == "pass":
                if candidate.status == "enriched":
                    raise ValueError("passing enriched candidate cannot yield a loss result")
                expected_status = candidate.status
                expected_marker = candidate.marker
                expected_losses: tuple[str, ...] = candidate.known_losses
            else:
                expected_status, expected_marker, expected_losses = (
                    _failed_enrichment_disposition(recomputed)
                )
            if (
                self.status != expected_status
                or self.marker != expected_marker
                or self.known_losses != expected_losses
            ):
                raise ValueError("non-enriched result must equal the recomputed disposition")
        return self


def compose_deep_dive_enrichment(
    request: DeepDiveEnrichmentRequestV1,
    writer: DeepDiveEnrichmentWriter
    | Callable[[DeepDiveEnrichmentRequestV1], DeepDiveEnrichedWriterResult],
) -> DeepDiveEnrichedResultV1:
    """Invoke an injected writer once, then independently validate and gate it."""
    if not isinstance(request, DeepDiveEnrichmentRequestV1):
        raise TypeError("request must be a DeepDiveEnrichmentRequestV1")
    # Defeat model_construct/model_copy bypasses before exposing the request.
    request = DeepDiveEnrichmentRequestV1.model_validate(request.model_dump())
    candidate = writer(request)
    if not isinstance(candidate, DeepDiveEnrichedWriterResult):
        raise TypeError("writer must return DeepDiveEnrichedWriterResult")
    candidate = DeepDiveEnrichedWriterResult.model_validate(candidate.model_dump())
    receipt = deep_dive_enrichment_gate(request, candidate)
    if candidate.status == "enriched" and receipt.status == "pass":
        return DeepDiveEnrichedResultV1(
            status="enriched",
            sections=candidate.sections,
            bold_terms=candidate.bold_terms,
            known_losses=(),
            marker=None,
            request=request,
            candidate_snapshot=candidate,
            enriched_payload_digest=_candidate_payload_digest(
                candidate.sections,  # type: ignore[arg-type]
                candidate.bold_terms,
            ),
            gate=receipt,
        )
    if receipt.status == "pass":
        status: Literal["degraded", "unavailable"] = candidate.status  # type: ignore[assignment]
        marker = candidate.marker
        losses: tuple[str, ...] = candidate.known_losses
    else:
        status, marker, losses = _failed_enrichment_disposition(receipt)
    return DeepDiveEnrichedResultV1(
        status=status,
        sections=(),
        bold_terms=(),
        known_losses=losses,  # type: ignore[arg-type]
        marker=marker,
        request=request,
        candidate_snapshot=candidate,
        enriched_payload_digest=_candidate_payload_digest((), ()),
        gate=receipt,
    )


# ---------------------------------------------------------------------------
# Request builder — disk-mediated (workbook brief + Ask-A packet + G0 overlay)
# ---------------------------------------------------------------------------


def build_overlay_covered_input(run_dir: Path) -> DeepDiveOverlayCoveredInputV1:
    """Project the D2.4 covered-LO/fact dedup input from the frozen G0 card.

    Honest-empty when no enrichment card exists on the run.
    """
    from app.marcus.lesson_plan.workbook_enrichment import (  # noqa: PLC0415 - cycle guard
        load_enrichment_card,
        project_enrichment_to_workbook_inputs,
    )

    card = load_enrichment_card(Path(run_dir))
    if card is None:
        return DeepDiveOverlayCoveredInputV1(
            card_present=False,
            covered_learning_objectives=(),
            covered_exercise_facts=(),
        )
    projection = project_enrichment_to_workbook_inputs(card)
    facts: list[str] = []
    for section in projection.spec.sections:
        for exercise in section.exercises:
            if exercise.prompt_intent and exercise.prompt_intent not in facts:
                facts.append(exercise.prompt_intent)
    return DeepDiveOverlayCoveredInputV1(
        card_present=True,
        covered_learning_objectives=tuple(
            OverlayCoveredObjective(objective_id=lo.objective_id, statement=lo.statement)
            for lo in projection.learning_objectives
        ),
        covered_exercise_facts=tuple(facts),
    )


def _pool_rows_from_packet(packet: ResearchPacket) -> tuple[AskAKnowledgeEntryV1, ...]:
    rows: list[AskAKnowledgeEntryV1] = []
    for entry in packet.entries:
        try:
            rows.append(_validate_json_payload(AskAKnowledgeEntryV1, entry))
        except ValueError as exc:
            raise DeepDiveEnrichmentAuthorityError(
                f"Ask-A pool row is not a valid ask-a-knowledge-entry.v1: {exc}"
            ) from exc
    return tuple(rows)


def build_deep_dive_enrichment_request(run_dir: Path) -> DeepDiveEnrichmentRequestV1:
    """Build the digest-bound enrichment request from a run directory (AC3).

    The pool comes ONLY from the exact ``ask_a_enrichment@07W.2`` packet via
    :func:`resolve_for_enrichment_pool` with ``require_usable=False`` —
    deliberately: a thin/empty pool is a legitimate degraded path (matrix row
    d), not a dispatch failure. Raises
    :class:`DeepDiveEnrichmentAuthorityError` when the workbook brief is absent
    or its skeleton is not authored.
    """
    run_dir = Path(run_dir)
    try:
        brief = read_workbook_brief(run_dir)
    except ValueError as exc:
        raise DeepDiveEnrichmentAuthorityError(
            f"workbook brief authority is unavailable: {exc}"
        ) from exc
    skeleton_result = brief.payload.deep_dive_skeleton
    if skeleton_result is None:
        raise DeepDiveSkeletonMissingError(
            "workbook brief carries no Deep Dive skeleton"
        )
    skeleton = skeleton_binding_from_result(skeleton_result)
    packet = resolve_for_enrichment_pool(run_dir, require_usable=False)
    pool_rows = _pool_rows_from_packet(packet)
    scope_digest: str | None = None
    intake_covered: tuple[str, ...] = ()
    intake_uncovered: tuple[str, ...] = ()
    intake = packet.research_intake
    if isinstance(intake, dict):
        scope = intake.get("scope")
        if isinstance(scope, dict) and isinstance(scope.get("scope_digest"), str):
            scope_digest = scope["scope_digest"]
        covered = intake.get("covered_ability_ids")
        uncovered = intake.get("uncovered_ability_ids")
        if isinstance(covered, list):
            intake_covered = tuple(str(item) for item in covered)
        if isinstance(uncovered, list):
            intake_uncovered = tuple(str(item) for item in uncovered)
    if pool_rows and scope_digest is None:
        scope_digest = pool_rows[0].scope_digest
    payload: dict[str, Any] = {
        "schema_version": "deep-dive-enrichment-request.v1",
        "skeleton": skeleton.model_dump(mode="json"),
        "pool_packet_digest": packet.packet_digest,
        "pool_status": packet.status,
        "pool_scope_digest": scope_digest if pool_rows else None,
        "pool_rows": [row.model_dump(mode="json") for row in pool_rows],
        "pool_known_losses": list(packet.known_losses),
        # 38.1 records credibility exclusions by raw-row index (no citation ID
        # was ever minted for an excluded row), so this stays empty on live
        # packets; the field exists so the gate can distinguish an
        # excluded-row citation from an invented ID (M2a).
        "excluded_citation_ids": [],
        "intake_covered_ability_ids": list(intake_covered),
        "intake_uncovered_ability_ids": list(intake_uncovered),
        "overlay_covered": build_overlay_covered_input(run_dir).model_dump(mode="json"),
    }
    payload["request_digest"] = enrichment_request_digest(payload)
    return _validate_json_payload(DeepDiveEnrichmentRequestV1, payload)


# ---------------------------------------------------------------------------
# Execution receipt + 07W.3 contribution contract + disk reader + renderers
# ---------------------------------------------------------------------------


class DeepDiveEnrichmentExecutionReceiptV1(_StrictModel):
    schema_version: Literal["deep-dive-enrichment-execution-receipt.v1"] = (
        "deep-dive-enrichment-execution-receipt.v1"
    )
    writer: Literal["deep_dive_enrichment"] = "deep_dive_enrichment"
    mode: Literal["offline_stub", "live"]
    calls: Literal[0, 1]
    idempotency_key: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    request_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    pool_packet_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    model: str | None = None
    model_config_digest: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    request_id: str | None = None
    latency_ms: float | None = Field(default=None, ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cost_usd: float | None = Field(default=None, ge=0)
    cost_unavailable_reason: str | None = None

    @model_validator(mode="after")
    def _cost_posture(self) -> DeepDiveEnrichmentExecutionReceiptV1:
        if self.cost_usd is not None and self.cost_unavailable_reason is not None:
            raise ValueError("cost receipt cannot carry both cost and unavailable reason")
        if (
            self.mode == "live"
            and self.calls == 1
            and self.cost_usd is None
            and not self.cost_unavailable_reason
        ):
            raise ValueError("live writer call without cost requires an explicit reason")
        return self


class WorkbookReviewContributionV1(_StrictModel):
    """The activated ``workbook_review@07W.3`` contribution output (AC5).

    This story wires ONLY the deep-dive-enrichment leg of the review node:
    Check/Reflection stay honestly stubbed via typed ``known_losses``.
    """

    schema_version: Literal["workbook-review-contribution.v1"] = (
        "workbook-review-contribution.v1"
    )
    node_id: Literal["07W.3"] = "07W.3"
    specialist_id: Literal["workbook_review"] = "workbook_review"
    deep_dive_enrichment: DeepDiveEnrichedResultV1 | None
    deep_dive_enrichment_receipt: DeepDiveEnrichmentExecutionReceiptV1 | None
    known_losses: tuple[NonBlankLine, ...]
    output_digest: Sha256Digest

    @model_validator(mode="after")
    def _reconciled(self) -> WorkbookReviewContributionV1:
        if (self.deep_dive_enrichment is None) != (self.deep_dive_enrichment_receipt is None):
            raise ValueError("enrichment result and execution receipt must appear together")
        if self.deep_dive_enrichment is None:
            if (
                len(self.known_losses) != 3
                or self.known_losses[0] not in SKELETON_ABSENT_LOSSES
                or self.known_losses[1:]
                != (CHECK_WRITER_STUB_LOSS, REFLECTION_WRITER_STUB_LOSS)
            ):
                raise ValueError(
                    "workbook review contribution losses must be exactly typed"
                )
        else:
            if self.known_losses != (
                CHECK_WRITER_STUB_LOSS,
                REFLECTION_WRITER_STUB_LOSS,
            ):
                raise ValueError(
                    "workbook review contribution losses must be exactly typed"
                )
            if (
                self.deep_dive_enrichment_receipt is not None
                and self.deep_dive_enrichment_receipt.request_digest
                != self.deep_dive_enrichment.request.request_digest
            ):
                raise ValueError("execution receipt request digest mismatch")
            # R2 (receipt-aware honesty seam): a candidate that CLAIMS
            # writer-unavailable while the receipt records a SUCCESSFUL live
            # provider call is dishonest — the call happened. Honest offline
            # unavailable (mode=offline_stub, calls=0) stays valid.
            if (
                self.deep_dive_enrichment_receipt is not None
                and self.deep_dive_enrichment_receipt.mode == "live"
                and self.deep_dive_enrichment_receipt.calls >= 1
                and self.deep_dive_enrichment.candidate_snapshot.status == "unavailable"
            ):
                raise ValueError(
                    "unavailable_shape_dishonest: a successful live provider call "
                    "cannot yield a writer-unavailable candidate"
                )
        if self.output_digest != _canonical_digest(
            self.model_dump(mode="json", exclude={"output_digest"})
        ):
            raise ValueError("workbook review contribution digest mismatch")
        return self


def build_workbook_review_contribution(
    result: DeepDiveEnrichedResultV1 | None,
    receipt: DeepDiveEnrichmentExecutionReceiptV1 | None,
    *,
    skeleton_loss: str = SKELETON_UNAVAILABLE_LOSS,
) -> WorkbookReviewContributionV1:
    if skeleton_loss not in SKELETON_ABSENT_LOSSES:
        raise ValueError(f"unknown skeleton loss: {skeleton_loss!r}")
    losses: tuple[str, ...] = (CHECK_WRITER_STUB_LOSS, REFLECTION_WRITER_STUB_LOSS)
    if result is None:
        losses = (skeleton_loss, *losses)
    payload: dict[str, Any] = {
        "schema_version": "workbook-review-contribution.v1",
        "node_id": WORKBOOK_REVIEW_NODE_ID_LITERAL,
        "specialist_id": WORKBOOK_REVIEW_SPECIALIST_ID_LITERAL,
        "deep_dive_enrichment": result.model_dump(mode="json") if result else None,
        "deep_dive_enrichment_receipt": (
            receipt.model_dump(mode="json") if receipt else None
        ),
        "known_losses": list(losses),
    }
    payload["output_digest"] = _canonical_digest(payload)
    return _validate_json_payload(WorkbookReviewContributionV1, payload)


def load_workbook_review_contribution(
    run_dir: Path,
) -> WorkbookReviewContributionV1 | None:
    """Disk-read the activated 07W.3 contribution from ``run.json`` (M3-safe).

    Returns ``None`` when the run carries no activated review contribution
    (absent envelope, absent coordinate, or the legacy ``workbook_review_stub``
    payload). A present-but-invalid activated payload fails loud.
    """
    from app.marcus.lesson_plan.workbook_enrichment import (  # noqa: PLC0415 - cycle guard
        load_run_envelope,
    )

    envelope = load_run_envelope(Path(run_dir))
    if envelope is None:
        return None
    contribution = envelope.get_contribution(
        WORKBOOK_REVIEW_SPECIALIST_ID_LITERAL, node_id=WORKBOOK_REVIEW_NODE_ID_LITERAL
    )
    if contribution is None:
        return None
    output = contribution.output if isinstance(contribution.output, dict) else {}
    if output.get("stub_status") == "not_yet_wired":
        return None
    try:
        return _validate_json_payload(WorkbookReviewContributionV1, output)
    except ValueError as exc:
        raise ValueError(
            f"workbook review contribution contract is invalid: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# Render seam (consumed lazily by workbook_producer; deterministic, model-free)
# ---------------------------------------------------------------------------


def render_deep_dive_markdown(contribution: WorkbookReviewContributionV1 | None) -> str:
    """Render the ``## Deep Dive`` section body (heading added by the composer).

    Enriched: per-ability subsections in ratified ability order, enriched prose
    with ``**bold**`` terms and inline ``[ask-a-cite-###]`` markers. Degraded /
    unavailable / not-run: the skeleton-or-honesty note with the typed loss
    visible (mirror of the ``lo_overlay_loss`` visible-degrade idiom) and ZERO
    ``ask-a-cite-`` markers — never a silent absence.
    """
    if contribution is None:
        return (
            "> _Deep Dive enrichment loss: deep_dive_enrichment_not_recorded — no "
            "activated workbook-review contribution exists for this run; the "
            "read-channel deep dive is not claimed here._"
        )
    result = contribution.deep_dive_enrichment
    if result is None:
        skeleton_loss = (
            contribution.known_losses[0]
            if contribution.known_losses
            and contribution.known_losses[0] in SKELETON_ABSENT_LOSSES
            else SKELETON_UNAVAILABLE_LOSS
        )
        if skeleton_loss.startswith(SKELETON_NOT_AUTHORED_LOSS_PREFIX):
            # R5: a present-but-non-authored skeleton names its recorded state
            # honestly — it never routes to the "no authored skeleton" note.
            state = skeleton_loss.removeprefix(f"{SKELETON_NOT_AUTHORED_LOSS_PREFIX}_")
            return (
                f"> _Deep Dive enrichment loss: {skeleton_loss} — the workbook "
                f"brief's Deep Dive skeleton exists but did not author "
                f"(status={state}), so there is nothing to enrich; the "
                "read-channel deep dive is not claimed here._"
            )
        return (
            f"> _Deep Dive enrichment loss: {skeleton_loss} — the "
            "workbook brief carries no Deep Dive skeleton, so there is "
            "nothing to enrich; the read-channel deep dive is not claimed here._"
        )
    lines: list[str] = []
    if result.status == "enriched":
        for section in result.sections:
            lines.append(f"### {section.ability_id}")
            lines.append(section.prose)
            lines.append("")
        return "\n".join(lines).rstrip()
    loss = result.known_losses[0] if result.known_losses else "deep_dive_enrichment_unknown_loss"
    lines.append(
        f"> _Deep Dive enrichment loss: {loss} — the cited enrichment did not "
        "author on this run; the traceable skeleton read-prose below stands "
        "without pool citations._"
    )
    lines.append("")
    for section in result.request.skeleton.sections:
        lines.append(f"### {section.ability_id}")
        lines.append(section.prose)
        lines.append("")
    return "\n".join(lines).rstrip()


def used_pool_rows(result: DeepDiveEnrichedResultV1) -> tuple[AskAKnowledgeEntryV1, ...]:
    """The pool rows actually cited in prose (for the References resolvability floor)."""
    used = set(result.gate.used_citation_ids)
    return tuple(row for row in result.request.pool_rows if row.citation_id in used)


def render_deep_dive_reference_lines(
    contribution: WorkbookReviewContributionV1 | None,
) -> tuple[str, ...]:
    """Reference entries for every used Ask-A row (resolvability floor only; A8).

    Full References assemble/dedupe/render ownership stays with Story 37.5.
    """
    if contribution is None or contribution.deep_dive_enrichment is None:
        return ()
    result = contribution.deep_dive_enrichment
    if result.status != "enriched":
        return ()
    lines: list[str] = []
    for row in used_pool_rows(result):
        peer = "peer-reviewed" if row.peer_reviewed else "not peer-reviewed"
        provenance = ",".join(row.provider_provenance) or row.provider
        # R9: a doi.org link is emitted ONLY for a DOI-shaped source_id;
        # anything else renders as a source_ref-only entry (never a fabricated
        # link). A blank title renders the source_ref as the line label (no
        # "- . " artifacts).
        label = row.title.strip() or row.source_ref
        link = (
            f" https://doi.org/{row.source_id}"
            if _DOI_SHAPE_RE.fullmatch(row.source_id)
            else ""
        )
        lines.append(
            f"- {label}.{link} "
            f"(provider: {row.provider}, source_ref: `{row.source_ref}`, "
            f"citation_id: `{row.citation_id}`, tier={row.evidence_hierarchy_tier}, "
            f"{peer}, provenance={provenance}, triangulation={row.triangulation_status})"
        )
    return tuple(lines)


__all__ = [
    "CHECK_WRITER_STUB_LOSS",
    "CITATION_MARKER_RE",
    "DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER",
    "DEEP_DIVE_ENRICHMENT_UNAVAILABLE_MARKER",
    "OPERATOR_SEMANTIC_ENRICHMENT_WARNING",
    "POOL_EMPTY_LOSS",
    "POOL_UNUSED_LOSS",
    "REFLECTION_WRITER_STUB_LOSS",
    "SKELETON_ABSENT_LOSSES",
    "SKELETON_NOT_AUTHORED_LOSS_PREFIX",
    "SKELETON_UNAVAILABLE_LOSS",
    "DeepDiveEnrichmentAuthorityError",
    "DeepDiveSkeletonMissingError",
    "DeepDiveSkeletonNotAuthoredError",
    "DeepDiveEnrichmentExecutionReceiptV1",
    "DeepDiveEnrichmentGateReceipt",
    "DeepDiveEnrichmentRequestV1",
    "DeepDiveEnrichmentWriter",
    "DeepDiveEnrichedResultV1",
    "DeepDiveEnrichedWriterResult",
    "DeepDiveOverlayCoveredInputV1",
    "DeepDiveSkeletonBindingV1",
    "EnrichedClaimBinding",
    "EnrichedDeepDiveClaim",
    "EnrichedDeepDiveSection",
    "OverlayCoveredObjective",
    "WorkbookReviewContributionV1",
    "build_deep_dive_enrichment_request",
    "build_overlay_covered_input",
    "build_workbook_review_contribution",
    "compose_deep_dive_enrichment",
    "deep_dive_enrichment_gate",
    "enrichment_request_digest",
    "load_workbook_review_contribution",
    "offline_deep_dive_enrichment_writer",
    "prose_citation_markers",
    "render_deep_dive_markdown",
    "render_deep_dive_reference_lines",
    "skeleton_binding_from_result",
    "skeleton_not_authored_loss",
    "strip_citation_markers",
    "used_pool_rows",
]
