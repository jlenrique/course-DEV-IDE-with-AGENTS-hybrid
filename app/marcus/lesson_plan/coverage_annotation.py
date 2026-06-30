"""Coverage-annotation pass (T4 — segmentation + derived-first intent).

The AUTHORED side of the coverage interlock: one :class:`CoverageAnnotation` per
presentation-note-bearing component, each carrying the re-segmented
:class:`~app.marcus.lesson_plan.source_point.SourcePoint` assertions. Layered onto
:class:`~app.marcus.lesson_plan.g0_enrichment.G0EnrichmentResult` via
``repin_additive`` (the frozen side), exactly like P2 citations / P3 pedagogy.

MIRRORS ``pedagogy_annotation.build_pedagogy_annotations`` (Winston/Irene reuse
map): offline deterministic pass (default; what the test surface exercises) + a
LIVE gpt-5 segmentation leg (the orchestrator's job at T8). Reuses the P3 gpt-5
binding (``PEDAGOGY_LIVE_MODEL = "marcus"`` → gpt-5); the LLM ONLY cuts verbatim
spans — risk flags + coverage intents are assigned DETERMINISTICALLY (AC5/AC7), so
the model paraphrase is never trusted and identity keys on the verbatim span
(AC-OP2-DET).

HARNESS DISCIPLINE (AC-OP2, T0-spike-proven; the live leg only): every gpt-5 call
runs on a client with a hard PER-REQUEST timeout (``OpenAI(timeout=…,
max_retries=0)``) — a missing per-request timeout hung the first spike ~8 min;
generous ``max_completion_tokens`` (reasoning models return EMPTY if too small);
``reasoning_effort="low"``. ≤ ``MAX_ASSERTIONS_PER_BLOCK`` per block (else
investigate over-segmentation, AC-OP1 escalation threshold).

ARCHITECTURE: this module depends only on the leaf ``source_point`` entity + a
deterministic risk detector. It MUST NOT import ``g0_enrichment`` at runtime (that
module imports :class:`CoverageAnnotation`; a back-import is a cycle) and MUST NOT
import ``app.marcus.orchestrator`` (one-way arrow).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.marcus.lesson_plan.source_point import (
    RiskFlagLiteral,
    SegmentationGrain,
    SourcePoint,
    derive_coverage_intents,
    make_source_point_id,
)
from app.models.state._base import enforce_tz_aware

if TYPE_CHECKING:  # annotation only — a runtime import would be a cycle
    from app.marcus.lesson_plan.g0_enrichment import G0EnrichmentResult  # noqa: F401

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Transform identity + harness constants
# ---------------------------------------------------------------------------

COVERAGE_TRANSFORM_VERSION: Final[str] = "cov-v1"
COVERAGE_OFFLINE_MODEL: Final[str] = "deterministic-coverage-offline"
COVERAGE_LIVE_MODEL: Final[str] = "marcus"
"""Reuse the P3 gpt-5 binding (``pedagogy_annotation.PEDAGOGY_LIVE_MODEL``); do not
mint a new model seam (AC-OP2)."""

MAX_ASSERTIONS_PER_BLOCK: Final[int] = 15
"""T0-spike escalation ceiling (10–13 observed). > this → investigate over-segmentation."""
COVERAGE_REQUEST_TIMEOUT_S: Final[float] = 60.0
"""Hard per-request gpt-5 client timeout (AC-OP2). NEVER omit on the live leg."""
COVERAGE_MAX_COMPLETION_TOKENS: Final[int] = 8000
"""Generous budget — a reasoning model burns the budget on hidden reasoning first."""

# Component types whose presentation-note block is re-segmented into source points.
# Speaker notes are the existing ``narration``-typed components (AC1: no new type).
NOTE_BEARING_TYPES: Final[frozenset[str]] = frozenset({"narration"})

# ---------------------------------------------------------------------------
# Deterministic risk detector (AC5/AC7 — no LLM; the verbatim floor is mechanical)
# ---------------------------------------------------------------------------

_DIGIT_RE: Final[re.Pattern[str]] = re.compile(r"\d")
# A dose: a number adjacent to a dose unit (mg/mcg/g/ml/l/units/iu/%/mmhg…).
_DOSE_RE: Final[re.Pattern[str]] = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|ug|g|kg|ml|l|units?|iu|mmol|mg/dl|mmhg|%)\b",
    re.IGNORECASE,
)
# FIX 5: negative CONTRACTIONS escaped the floor — "don't exceed 5 mg" carried no
# `negation` flag, so a safety/dosing prohibition was not verbatim_required → not
# must_cover. The word tokenizer keeps the apostrophe (``[A-Za-z][A-Za-z'-]*``), so a
# contraction surfaces as a single token; we list the common ones (curly apostrophes
# are normalized to straight in ``_words`` so both "don't" and "don’t" match).
_NEGATION_CONTRACTIONS: Final[frozenset[str]] = frozenset(
    {
        "don't", "doesn't", "didn't", "isn't", "aren't", "wasn't", "weren't",
        "won't", "wouldn't", "can't", "couldn't", "shouldn't", "mustn't",
        "needn't", "haven't", "hasn't", "hadn't", "ain't", "shan't", "mightn't",
    }
)
_NEGATION_LEXICON: Final[frozenset[str]] = frozenset(
    {"no", "not", "never", "none", "nor", "neither", "without", "cannot", "nothing"}
) | _NEGATION_CONTRACTIONS
_COMPARATOR_LEXICON: Final[frozenset[str]] = frozenset(
    {
        "more", "less", "fewer", "greater", "lower", "higher", "than", "most",
        "least", "increase", "increased", "decrease", "decreased", "rose", "fell",
        "doubled", "halved", "surged", "drastically",
    }
)
_EXEMPLARY_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:for example|for instance|such as|e\.g\.|like)\b", re.IGNORECASE
)
_WORD_RE: Final[re.Pattern[str]] = re.compile(r"[A-Za-z][A-Za-z'-]*")


def _words(text: str) -> set[str]:
    # Normalize curly apostrophes (U+2019 / U+2018) to a straight ' so a contraction
    # ("don't" vs "don’t") tokenizes identically and hits the negation lexicon (FIX 5).
    normalized = text.replace("’", "'").replace("‘", "'")
    return {m.group(0).lower() for m in _WORD_RE.finditer(normalized)}


def detect_risk_flags(
    text: str,
    *,
    clinical_terms: frozenset[str] | None = None,
) -> tuple[RiskFlagLiteral, ...]:
    """Deterministic risk-flag detection over a verbatim span (AC5; no LLM).

    ``clinical_claim`` is detected ONLY when a ``clinical_terms`` lexicon is injected
    (the deferred clinical-ontology leg, mirroring R7's documented stub) — default
    off. ``numeric``/``dosing``/``negation``/``comparator``/``exemplary_language``
    are mechanical. Returns a unique, sorted tuple.
    """
    flags: set[RiskFlagLiteral] = set()
    words = _words(text)
    if _DOSE_RE.search(text):
        flags.add("dosing")
    if _DIGIT_RE.search(text):
        flags.add("numeric")
    if words & _NEGATION_LEXICON:
        flags.add("negation")
    if words & _COMPARATOR_LEXICON:
        flags.add("comparator")
    if _EXEMPLARY_RE.search(text):
        flags.add("exemplary_language")
    if clinical_terms and (words & {t.lower() for t in clinical_terms}):
        flags.add("clinical_claim")
    return tuple(sorted(flags))


# Sentence boundary for the OFFLINE deterministic segmenter (reproducible
# placeholder; the LIVE gpt-5 pass cuts the real teaching-assertion spans). Splits
# ONLY at a terminator followed by whitespace + a capital/digit/quote start, so a
# decimal ("$5.2") and a dotted abbreviation ("U.S.") are NOT fragmented — a number
# split mid-span would silently lose its 'numeric' risk floor.
_SENTENCE_SPLIT_RE: Final[re.Pattern[str]] = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"“])')


def _segment_block_offline(text: str) -> list[str]:
    """Deterministic offline segmentation of a note block into assertion spans.

    Splits at real sentence boundaries (terminator + space + capitalized/numeric
    start), trims, drops empties. Byte-stable across runs. Capped at
    :data:`MAX_ASSERTIONS_PER_BLOCK`.
    """
    stripped = text.strip().strip('"“”')
    spans = [s.strip().strip('"“”') for s in _SENTENCE_SPLIT_RE.split(stripped)]
    spans = [s for s in spans if s]
    return spans[:MAX_ASSERTIONS_PER_BLOCK]


# ---------------------------------------------------------------------------
# The annotation model (rides G0EnrichmentResult; freeze-once, AC9 + AC-OP2-DET)
# ---------------------------------------------------------------------------


class CoverageAnnotation(BaseModel):
    """One component's re-segmented source-point set (additive; never gates here).

    Frozen value object. All ``source_points`` belong to this component
    (``component_id`` parent join key, AC1); the ``segmentation`` grain is a single
    load-bearing stamp for the whole block (Irene caveat) and must be consistent
    across its points.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    component_id: str = Field(..., min_length=1, description="Parent component (join key, AC1).")
    slide_key: str = Field(..., min_length=1, description="The parent's 'Slide N' locator key.")
    source_points: tuple[SourcePoint, ...] = Field(
        ..., description="Re-segmented teaching assertions (non-empty)."
    )
    segmentation: SegmentationGrain = Field(
        ..., description="Block-level provenance grain (load-bearing; declared on the report face)."
    )
    transform_model: str = Field(default=COVERAGE_OFFLINE_MODEL, min_length=1)
    transform_version: str = Field(default=COVERAGE_TRANSFORM_VERSION, min_length=1)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @field_validator("generated_at")
    @classmethod
    def _tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @model_validator(mode="after")
    def _enforce_block_invariants(self) -> CoverageAnnotation:
        if not self.source_points:
            raise ValueError(f"coverage annotation for {self.component_id!r} has no source points")
        for sp in self.source_points:
            if sp.component_id != self.component_id:
                raise ValueError(
                    f"source point {sp.source_point_id!r} parent {sp.component_id!r} != "
                    f"annotation component_id {self.component_id!r} (AC1 join-key integrity)"
                )
            if sp.segmentation != self.segmentation:
                raise ValueError(
                    f"source point {sp.source_point_id!r} segmentation {sp.segmentation!r} != "
                    f"block grain {self.segmentation!r} (Irene caveat: stamp is load-bearing)"
                )
        return self

    def is_v1_shippable(self) -> bool:
        """AC-OP1: v1 ships ONLY at ``assertion_level`` (``block_level_v1`` is diagnostic)."""
        return self.segmentation == "assertion_level"


def coverage_annotation_json_schema() -> dict[str, Any]:
    return CoverageAnnotation.model_json_schema()


def load_coverage_annotation(payload: dict[str, Any]) -> CoverageAnnotation:
    return CoverageAnnotation.model_validate(payload)


# ---------------------------------------------------------------------------
# Ship gate (FIX 4 / AC-OP1) — block_level_v1 is NEVER a v1 ship state
# ---------------------------------------------------------------------------


class CoverageNotShippableError(ValueError):
    """A coverage annotation set carries a non-``assertion_level`` grain (AC-OP1).

    ``block_level_v1`` is a DIAGNOSTIC-only provenance value; v1 ships ONLY when every
    annotation is at ``assertion_level``. Orchestrator-callable ship gate (raised
    before the receipt ships).
    """


def assert_v1_shippable(annotations: tuple[CoverageAnnotation, ...]) -> None:
    """Raise :class:`CoverageNotShippableError` if any annotation is not v1-shippable.

    AC-OP1: ``block_level_v1`` is never an acceptable v1 ship state. The orchestrator
    calls this before the receipt ships — there is NO coarse-ship fallback (the spike
    proved assertion-level bounded; a ``block_level_v1`` stamp means re-segmentation
    failed and the run must STOP/ESCALATE, not ship a coarse receipt).
    """
    bad = [a for a in annotations if not a.is_v1_shippable()]
    if bad:
        offenders = ", ".join(f"{a.component_id}({a.segmentation})" for a in bad)
        raise CoverageNotShippableError(
            f"AC-OP1: {len(bad)} coverage annotation(s) carry a non-'assertion_level' grain "
            f"[{offenders}] — 'block_level_v1' is NEVER a v1 ship state; STOP and escalate "
            "(no coarse-ship fallback)."
        )


# ---------------------------------------------------------------------------
# Incompleteness signal (FIX 3) — a non-empty note block that yields zero spans
# must NOT silently empty the ledger (indistinguishable from "0 holes").
# ---------------------------------------------------------------------------


class IncompleteSegment(BaseModel):
    """A note-bearing component whose non-empty notes produced ZERO source points.

    The explicit, structured ``coverage_incomplete`` marker (FIX 3): segmentation
    that yields nothing for a note-bearing block is surfaced, never swallowed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    component_id: str = Field(..., min_length=1)
    slide_key: str = Field(..., min_length=1)
    reason: str = Field(default="non-empty note block produced zero teaching assertions")


class CoverageIncompleteError(ValueError):
    """Segmentation produced nothing for one or more non-empty note blocks (FIX 3).

    Carries the offending :class:`IncompleteSegment` markers so the orchestrator can
    surface the holes rather than ship an empty (toothless) ledger.
    """

    def __init__(self, message: str, *, incomplete: tuple[IncompleteSegment, ...]):
        super().__init__(message)
        self.incomplete = incomplete


def detect_incomplete_segmentation(
    components: list[dict[str, Any]],
    annotations: tuple[CoverageAnnotation, ...],
) -> tuple[IncompleteSegment, ...]:
    """Find note-bearing components with non-empty notes but ZERO produced points (FIX 3).

    A genuinely empty note block is NOT incompleteness; a non-empty one that yielded
    no assertions IS (a malformed/empty live response, a parse failure, or all-empty
    assertions). Pure projection — no LLM, no I/O.
    """
    produced = {a.component_id for a in annotations if a.source_points}
    out: list[IncompleteSegment] = []
    for rec in components:
        if not is_note_bearing(_rec_type(rec)):
            continue
        cid = _rec_id(rec)
        if not cid or not _rec_excerpt(rec).strip():
            continue  # no id, or genuinely empty notes → not a hole
        if cid not in produced:
            out.append(IncompleteSegment(component_id=str(cid), slide_key=_rec_slide_key(rec)))
    return tuple(out)


def assert_segmentation_complete(
    components: list[dict[str, Any]],
    annotations: tuple[CoverageAnnotation, ...],
) -> None:
    """Raise :class:`CoverageIncompleteError` if any non-empty note block produced nothing.

    Orchestrator-callable (FIX 3): the live pass must DISTINGUISH "segmentation
    produced nothing for a note-bearing component" from "no must-cover holes".
    """
    incomplete = detect_incomplete_segmentation(components, annotations)
    if incomplete:
        ids = ", ".join(seg.component_id for seg in incomplete)
        raise CoverageIncompleteError(
            f"coverage segmentation produced ZERO assertions for {len(incomplete)} non-empty "
            f"note-bearing component(s) [{ids}] — the ledger would be silently empty "
            "(indistinguishable from '0 holes'); surface + investigate, do not ship.",
            incomplete=incomplete,
        )


# ---------------------------------------------------------------------------
# Verbatim re-anchor guard (F-012) — the LIVE path must NEVER mint a SourcePoint
# from a model paraphrase. Identity keys on the VERBATIM SOURCE SPAN (AC-OP2-DET),
# so a model assertion must be recoverable as a byte-exact slice of the parent
# component's source excerpt (exact, or after whitespace/quote drift) — else DROP.
# The OFFLINE pass is substring-safe by construction (it cuts spans FROM the
# excerpt); only this live guard re-anchors model-supplied spans.
# ---------------------------------------------------------------------------

# Curly quotes/apostrophes → straight ASCII. ``str.maketrans`` maps single code
# point → single code point, so the translation is LENGTH-PRESERVING: byte offsets
# into the straightened string map 1:1 back onto the ORIGINAL, letting us recover the
# byte-exact source slice (curly quote intact) after matching on the straightened text.
_CURLY_QUOTE_TRANSLATION: Final[dict[int, str]] = str.maketrans(
    {"’": "'", "‘": "'", "“": '"', "”": '"'}
)


def _straighten_quotes(text: str) -> str:
    """Straighten curly quotes/apostrophes (length-preserving; offsets unchanged)."""
    return text.translate(_CURLY_QUOTE_TRANSLATION)


def reanchor_verbatim_span(span: str, excerpt: str) -> str | None:
    """Recover the BYTE-EXACT source slice a model span was cut from, else ``None``.

    AC-OP2-DET: identity keys on the verbatim source span, never an LLM paraphrase.

    1. **Exact byte-substring (fast path):** the raw span is already a byte-exact slice
       → return it unchanged.
    2. **Whitespace/quote-normalized re-anchor:** straighten curly quotes in BOTH sides,
       split the span on whitespace, and search the straightened excerpt with a
       ``\\s+``-joined case-sensitive regex of the escaped tokens. A match means the span
       differs from the source ONLY by whitespace/quote drift → return the byte-exact
       ORIGINAL slice (``excerpt[start:end]``; curly quotes + the source's own whitespace
       preserved), NOT the model's normalized string. Tolerates drift, never paraphrase.
    3. **No match:** a paraphrase/fabrication → ``None`` (DROP; never mint a SourcePoint).
    """
    if not span:
        return None
    if span in excerpt:
        return span
    straight_excerpt = _straighten_quotes(excerpt)
    tokens = _straighten_quotes(span).split()
    if not tokens:
        return None
    pattern = r"\s+".join(re.escape(tok) for tok in tokens)
    match = re.search(pattern, straight_excerpt)
    if match is None:
        return None
    # Length-preserving straighten → match offsets index the ORIGINAL excerpt directly.
    return excerpt[match.start() : match.end()]


def _anchor_spans(excerpt: str, spans: list[str]) -> tuple[list[str], list[str]]:
    """Partition model spans into (byte-exact accepted slices, dropped non-verbatim)."""
    accepted: list[str] = []
    dropped: list[str] = []
    for span in spans:
        anchored = reanchor_verbatim_span(span, excerpt)
        if anchored is None:
            dropped.append(span)
        else:
            accepted.append(anchored)
    return accepted, dropped


class NonVerbatimSpan(BaseModel):
    """A model assertion span DROPPED because it is neither a verbatim nor a
    whitespace/quote-normalized substring of its component's source excerpt (F-012).

    A paraphrase/fabrication must NEVER become a :class:`SourcePoint.verbatim_text`
    (the identity anchor, AC-OP2-DET). Mirrors the FIX-3 :class:`IncompleteSegment`
    marker: surfaced as an explicit, structured signal, never swallowed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    component_id: str = Field(..., min_length=1)
    slide_key: str = Field(..., min_length=1)
    span: str = Field(..., min_length=1, description="The dropped model-supplied span.")
    reason: str = Field(
        default=(
            "model span is not a verbatim or whitespace/quote-normalized substring of "
            "the source excerpt (AC-OP2-DET: identity keys on the verbatim source span)"
        )
    )


def detect_non_verbatim_spans(
    rows: list[dict[str, Any]],
    components: list[dict[str, Any]],
) -> tuple[NonVerbatimSpan, ...]:
    """Pure projection (no LLM, no I/O): which model spans WOULD be dropped as non-verbatim.

    The orchestrator-readable mirror of :func:`build_coverage_from_rows`' inline guard —
    re-runs the same anchor logic so a downstream (G3) caller can surface every dropped
    paraphrase/fabrication without re-reading the build's internals. A dropped span is a
    DIAGNOSTIC (the surviving verbatim spans still build), not by itself a halt condition;
    a component whose EVERY span drops is caught by the FIX-3 incomplete signal.
    """
    by_id = {_rec_id(rec): rec for rec in components if is_note_bearing(_rec_type(rec))}
    out: list[NonVerbatimSpan] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("component_id") or "").strip()
        rec = by_id.get(cid)
        if not cid or rec is None:
            continue
        raw = row.get("assertions")
        spans = [str(s).strip() for s in raw if str(s).strip()] if isinstance(raw, list) else []
        excerpt = _rec_excerpt(rec)
        slide_key = _rec_slide_key(rec)
        for span in spans:
            if reanchor_verbatim_span(span, excerpt) is None:
                out.append(NonVerbatimSpan(component_id=cid, slide_key=slide_key, span=span))
    return tuple(out)


# ---------------------------------------------------------------------------
# Front-matter accessors (mirror P3 — read the universal-md front matter)
# ---------------------------------------------------------------------------


def _rec_id(rec: dict[str, Any]) -> str | None:
    return rec.get("component_id")


def _rec_type(rec: dict[str, Any]) -> str | None:
    return rec.get("type") or rec.get("component_type") or rec.get("source_type")


def _rec_locator(rec: dict[str, Any]) -> str:
    return rec.get("locator") or ""


def _rec_excerpt(rec: dict[str, Any]) -> str:
    return rec.get("excerpt") or rec.get("notes_text") or ""


def _rec_slide_key(rec: dict[str, Any]) -> str:
    """The 'Slide N' locator key (trailing breadcrumb), else the whole locator."""
    locator = _rec_locator(rec)
    last = locator.split(">")[-1].strip()
    return last or locator


def is_note_bearing(component_type: str | None) -> bool:
    return component_type in NOTE_BEARING_TYPES


def _point_from_span(
    *,
    component_id: str,
    slide_key: str,
    ordinal: int,
    span: str,
    source_type: str | None,
    pedagogical_role: str | None,
    lo_load_bearing: bool,
    is_organizing_claim: bool,
    segmentation: SegmentationGrain,
    clinical_terms: frozenset[str] | None,
) -> SourcePoint:
    risk_flags = detect_risk_flags(span, clinical_terms=clinical_terms)
    intents = derive_coverage_intents(
        source_type=source_type,
        pedagogical_role=pedagogical_role,
        lo_load_bearing=lo_load_bearing,
        risk_flags=risk_flags,
        is_organizing_claim=is_organizing_claim,
    )
    return SourcePoint(
        source_point_id=make_source_point_id(component_id, ordinal),
        component_id=component_id,
        ordinal=ordinal,
        slide_key=slide_key,
        verbatim_text=span,
        risk_flags=risk_flags,
        coverage_intents=intents,
        segmentation=segmentation,
    )


def _annotation_from_spans(
    rec: dict[str, Any],
    spans: list[str],
    *,
    transform_model: str,
    when: datetime,
    clinical_terms: frozenset[str] | None,
) -> CoverageAnnotation | None:
    cid = _rec_id(rec)
    if not cid or not spans:
        return None
    slide_key = _rec_slide_key(rec)
    role = rec.get("pedagogical_role")
    lo_load_bearing = bool(rec.get("lo_load_bearing") or rec.get("lo_refs"))
    points: list[SourcePoint] = []
    for i, span in enumerate(spans, start=1):
        # The organizing claim heuristic: the first assertion of a block frames it.
        points.append(
            _point_from_span(
                component_id=str(cid),
                slide_key=slide_key,
                ordinal=i,
                span=span,
                source_type=_rec_type(rec),
                pedagogical_role=role,
                lo_load_bearing=lo_load_bearing,
                is_organizing_claim=(i == 1),
                segmentation="assertion_level",
                clinical_terms=clinical_terms,
            )
        )
    return CoverageAnnotation(
        component_id=str(cid),
        slide_key=slide_key,
        source_points=tuple(points),
        segmentation="assertion_level",
        transform_model=transform_model,
        transform_version=COVERAGE_TRANSFORM_VERSION,
        generated_at=when,
    )


# ---------------------------------------------------------------------------
# Offline pass (deterministic; the test surface)
# ---------------------------------------------------------------------------


def _offline_coverage_pass(
    components: list[dict[str, Any]],
    *,
    generated_at: datetime | None,
    clinical_terms: frozenset[str] | None,
) -> tuple[CoverageAnnotation, ...]:
    when = generated_at or datetime.now(tz=UTC)
    out: list[CoverageAnnotation] = []
    for rec in components:
        if not is_note_bearing(_rec_type(rec)):
            continue
        spans = _segment_block_offline(_rec_excerpt(rec))
        ann = _annotation_from_spans(
            rec, spans, transform_model=COVERAGE_OFFLINE_MODEL, when=when,
            clinical_terms=clinical_terms,
        )
        if ann is not None:
            out.append(ann)
    return tuple(out)


# ---------------------------------------------------------------------------
# Live pass (gpt-5 segmentation) — parse + build are offline-tested via fixture
# ---------------------------------------------------------------------------


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "".join(parts)
    return ""


def extract_coverage_rows(content: Any) -> list[dict[str, Any]]:
    """Tolerant parse of the live response into per-component segmentation rows.

    Contract: ``{"blocks":[{"component_id": "...", "assertions": ["<verbatim span>", …]}]}``.
    Strips ```json fences, extracts the first ``{...}`` span when wrapped in prose.
    DEGRADES to ``[]`` (no annotations) on any parse failure — coverage is additive
    on this side (the gate is the teeth), so a malformed response yields an empty
    overlay, not a crash (mirror P3 ``_extract_pedagogy_rows``).
    """
    text = _content_to_text(content).strip()
    if not text:
        logger.warning("coverage live: empty response content; emitting no annotations")
        return []
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    payload: Any = None
    # strict=False permits LITERAL control characters (unescaped newline/tab) inside a
    # string value — gpt-5 routinely emits them; a strict parse would silently empty this
    # additive overlay (same defect that CRASHED the keystone G0 pre-pass live 2026-06-29).
    # Coverage degrades to [] on a true failure (additive; the gate is the teeth).
    try:
        payload = json.loads(text, strict=False)
    except (ValueError, TypeError):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                payload = json.loads(text[start : end + 1], strict=False)
            except (ValueError, TypeError):
                payload = None
    if not isinstance(payload, dict):
        logger.warning("coverage live: response not a JSON object; emitting no annotations")
        return []
    rows = payload.get("blocks", [])
    if not isinstance(rows, list):
        logger.warning("coverage live: 'blocks' is not a list; emitting no annotations")
        return []
    return [r for r in rows if isinstance(r, dict)]


def build_coverage_from_rows(
    rows: list[dict[str, Any]],
    components: list[dict[str, Any]],
    *,
    generated_at: datetime | None,
    clinical_terms: frozenset[str] | None,
) -> tuple[CoverageAnnotation, ...]:
    """Build annotations from live segmentation rows (resilient per-row loop).

    The model ONLY supplies verbatim assertion spans; risk flags + intents are
    assigned DETERMINISTICALLY here (AC5/AC7 — the model's characterization is never
    trusted for the floor). Over-segmentation past :data:`MAX_ASSERTIONS_PER_BLOCK`
    is clamped + logged (AC-OP1 ceiling). One malformed row is skipped, never
    aborting the pass.

    F-012 GUARD: every model span is re-anchored against its component's source excerpt
    (:func:`reanchor_verbatim_span`) BEFORE it can become a :class:`SourcePoint`. A span
    that is neither a byte-exact nor a whitespace/quote-normalized substring is a model
    PARAPHRASE — it is DROPPED (never minted as an identity anchor, AC-OP2-DET) and
    surfaced as a structured :class:`NonVerbatimSpan` diagnostic + a ``logger.warning``.
    A normalized match RE-ANCHORS to the byte-exact source slice, not the model wording.
    """
    when = generated_at or datetime.now(tz=UTC)
    by_id = {_rec_id(rec): rec for rec in components if is_note_bearing(_rec_type(rec))}
    out: list[CoverageAnnotation] = []
    for row in rows:
        cid = str(row.get("component_id") or "").strip()
        rec = by_id.get(cid)
        if not cid or rec is None:
            logger.warning(
                "coverage live: skipping row for unknown component %r", cid or "<missing>"
            )
            continue
        raw = row.get("assertions")
        spans = [str(s).strip() for s in raw if str(s).strip()] if isinstance(raw, list) else []
        if len(spans) > MAX_ASSERTIONS_PER_BLOCK:
            logger.warning(
                "coverage live: component %r over-segmented (%d > %d); clamping (AC-OP1 ceiling)",
                cid, len(spans), MAX_ASSERTIONS_PER_BLOCK,
            )
            spans = spans[:MAX_ASSERTIONS_PER_BLOCK]
        # F-012: re-anchor each model span to a byte-exact source slice; DROP paraphrases
        # so a model wording can never become a SourcePoint identity anchor (AC-OP2-DET).
        spans, dropped = _anchor_spans(_rec_excerpt(rec), spans)
        for bad in dropped:
            logger.warning(
                "coverage live: DROPPING non-verbatim span for %r — not a verbatim or "
                "whitespace/quote-normalized substring of the source excerpt (would have "
                "become a SourcePoint identity anchor; AC-OP2-DET): %r",
                cid, bad,
            )
        try:
            ann = _annotation_from_spans(
                rec, spans, transform_model=COVERAGE_LIVE_MODEL, when=when,
                clinical_terms=clinical_terms,
            )
        except (ValueError, TypeError) as exc:
            logger.warning("coverage live: dropping malformed block for %r (%s)", cid, exc)
            continue
        if ann is not None:
            out.append(ann)
    annotations = tuple(out)
    # FIX 3: never silently empty the ledger — a non-empty note block that produced
    # zero assertions is a structured `coverage_incomplete` marker, logged here so the
    # signal survives even if the orchestrator does not call `assert_segmentation_complete`.
    for seg in detect_incomplete_segmentation(components, annotations):
        logger.warning(
            "coverage live: component %r produced ZERO assertions from a non-empty note block "
            "(coverage_incomplete) — surfaced, not swallowed (FIX 3)",
            seg.component_id,
        )
    return annotations


def render_live_segmentation_prompt(  # pragma: no cover - live leg
    components: list[dict[str, Any]],
) -> str:
    """Build the gpt-5 segmentation prompt (verbatim-span cutting only).

    The contract instructs the model to CUT each note block into atomic teaching
    assertions, copying VERBATIM spans (no paraphrase — identity keys on the span,
    AC-OP2-DET), and to echo the component_id the parser keys on.
    """
    blocks = [
        f'- component_id="{_rec_id(rec)}" slide_key="{_rec_slide_key(rec)}"\n'
        f"  NOTES: {_rec_excerpt(rec)}"
        for rec in components
        if is_note_bearing(_rec_type(rec))
    ]
    return (
        "You re-segment a slide's speaker-note block into ATOMIC teaching assertions "
        "(one claim / instruction / caution / framing each). Return ONLY JSON of this "
        'shape (no prose, no markdown fences):\n'
        '{"blocks": [{"component_id": "<copy VERBATIM>", "assertions": '
        '["<verbatim span cut from the NOTES, copied exactly>", ...]}]}\n'
        f"Rules: copy spans VERBATIM from the NOTES (no paraphrase); emit <= "
        f"{MAX_ASSERTIONS_PER_BLOCK} assertions per block; component_id MUST be copied "
        "verbatim.\nBlocks:\n" + "\n".join(blocks)
    )


def _live_coverage_pass(
    components: list[dict[str, Any]],
    chat_model_factory: Any | None,
    *,
    generated_at: datetime | None,
    clinical_terms: frozenset[str] | None,
    non_verbatim_out: list[NonVerbatimSpan] | None = None,
) -> tuple[CoverageAnnotation, ...]:  # pragma: no cover - live leg
    """REAL gpt-5 segmentation via the P3 chat-model seam (single pass, no resample).

    Reuses ``COVERAGE_LIVE_MODEL`` ("marcus" → gpt-5). Temperature is bound at
    construction (gpt-5 rejects a per-call temp). The MANDATORY per-request timeout +
    max_retries=0 + generous max_completion_tokens + reasoning_effort=low are bound by
    the chat-model factory the orchestrator supplies at T8 (see module docstring).
    """
    note_bearing = [rec for rec in components if is_note_bearing(_rec_type(rec))]
    if not note_bearing:
        return ()
    if chat_model_factory is None:
        from app.models.adapter import make_chat_model

        # FIX 6: the DEFAULT fallback path must bind the SAME hard per-request timeout
        # + max_retries=0 the injected T8 harness factory binds (AC-OP2). `make_chat_model`
        # does NOT bind a timeout by default (verified: request_timeout=None → the openai
        # SDK's ~600s default, which can hang a slow gpt-5 reasoning call). Pass them
        # explicitly so the default path can't hang.
        def chat_model_factory(model_id: str) -> Any:
            return make_chat_model(
                model_id,
                request_timeout=COVERAGE_REQUEST_TIMEOUT_S,
                max_retries=0,
            )

    handle = chat_model_factory(COVERAGE_LIVE_MODEL)
    prompt = render_live_segmentation_prompt(note_bearing)
    response = handle.chat.invoke([{"role": "user", "content": prompt}])
    rows = extract_coverage_rows(response.content)
    # R5-A8: surface the F-012 NonVerbatimSpan ledger here (rows + components in hand)
    # so the G0E build site can persist it additively into g0-enrichment.json; the G3
    # marshaller reads it back as a ledger-only diagnostic (never a hard missing).
    if non_verbatim_out is not None:
        non_verbatim_out.extend(detect_non_verbatim_spans(rows, components))
    return build_coverage_from_rows(
        rows, components, generated_at=generated_at, clinical_terms=clinical_terms
    )


def build_coverage_annotations(
    components: list[dict[str, Any]],
    *,
    dispatch_live: bool = False,
    chat_model_factory: Any | None = None,
    generated_at: datetime | None = None,
    clinical_terms: frozenset[str] | None = None,
    non_verbatim_out: list[NonVerbatimSpan] | None = None,
) -> tuple[CoverageAnnotation, ...]:
    """Build per-component coverage annotations over the universal-md front matter.

    OFFLINE deterministic pass (default; the test surface) or the LIVE gpt-5 pass
    (``dispatch_live=True``; gated exactly like the P3 resolver). Only note-bearing
    (``narration``) components are segmented. Freeze-once: the result rides
    ``G0EnrichmentResult`` via ``repin_additive`` (AC9).

    R5-A8: when ``non_verbatim_out`` is supplied AND the LIVE pass runs, the F-012
    dropped-paraphrase ledger is appended to it (the OFFLINE pass cuts spans verbatim
    from the excerpt by construction → none). Additive; ``None`` keeps every existing
    caller byte-identical.
    """
    if dispatch_live:
        return _live_coverage_pass(
            components, chat_model_factory, generated_at=generated_at,
            clinical_terms=clinical_terms, non_verbatim_out=non_verbatim_out,
        )
    return _offline_coverage_pass(
        components, generated_at=generated_at, clinical_terms=clinical_terms
    )


__all__ = [
    "COVERAGE_LIVE_MODEL",
    "COVERAGE_MAX_COMPLETION_TOKENS",
    "COVERAGE_OFFLINE_MODEL",
    "COVERAGE_REQUEST_TIMEOUT_S",
    "COVERAGE_TRANSFORM_VERSION",
    "MAX_ASSERTIONS_PER_BLOCK",
    "NOTE_BEARING_TYPES",
    "CoverageAnnotation",
    "CoverageIncompleteError",
    "CoverageNotShippableError",
    "IncompleteSegment",
    "NonVerbatimSpan",
    "assert_segmentation_complete",
    "assert_v1_shippable",
    "build_coverage_annotations",
    "build_coverage_from_rows",
    "coverage_annotation_json_schema",
    "detect_incomplete_segmentation",
    "detect_non_verbatim_spans",
    "detect_risk_flags",
    "extract_coverage_rows",
    "is_note_bearing",
    "load_coverage_annotation",
    "reanchor_verbatim_span",
    "render_live_segmentation_prompt",
]
