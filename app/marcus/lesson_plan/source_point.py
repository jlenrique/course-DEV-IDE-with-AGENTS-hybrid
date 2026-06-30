"""Source-point coverage models (Story concierge-coverage-assurance-interlock, T3).

A ``SourcePoint`` is the atomic unit of the NEW coverage axis (source→deliverable):
one teaching ASSERTION (claim / instruction / caution / framing the instructor
intends a learner to take from a slide), produced by re-segmenting a slide's
presentation-note block. It is FINER than a :class:`~app.marcus.lesson_plan.
source_type.TypedComponent` (a notes block ≈ 2–4 assertions).

Identity (AC1, Winston caveat — BINDING + code-enforced):
    ``source_point_id = component_id + "#" + ordinal`` — a CHILD sub-locator of an
    EXISTING ``TypedComponent``. NO new id namespace; NO new ``source_type`` enum
    value. The ``#ordinal`` child-id is a sub-locator and is **NEVER a join key**:
    every downstream join keys on the parent ``component_id``. :func:`join_key`
    is the ONLY sanctioned join surface and it returns the PARENT id; a reviewer
    seeing a join on the child id is the design failing. ``assert_join_key`` makes
    the violation loud.

Determinism (AC-OP2-DET): identity keys on the VERBATIM SOURCE SPAN, never the
LLM paraphrase — the span the model cuts is far more stable than its wording. The
``segmentation`` provenance stamp (Irene caveat — load-bearing) keeps the grain
honest on the report's face and is never dropped.

Pydantic-v2 idioms (docs/dev-guide/pydantic-v2-schema-checklist.md):
    - ``ConfigDict(extra="forbid", validate_assignment=True, frozen=True)``.
    - every closed enum gets THREE red-rejection surfaces (Literal validator,
      JSON-Schema ``enum`` array, ``TypeAdapter`` round-trip) + an import-time
      exhaustiveness guard (mirror ``PedagogicalRole`` / ``SourceTypeLiteral``).
    - ``verbatim_required`` is a DERIVED floor (recomputed by the validator), so a
      hand-set value can never disagree with the deterministic risk taxonomy.
"""

from __future__ import annotations

import re
from typing import Any, Final, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)

# ---------------------------------------------------------------------------
# Closed enums (three red-rejection surfaces each)
# ---------------------------------------------------------------------------

CoverageIntentLiteral = Literal[
    "gist_on_slide",
    "detail_in_narration",
    "deliberately_excluded",
]
"""How a source point is INTENDED to be carried (AC3). A point carries a non-empty
SET of these (membership semantics; modelled as a unique, sorted tuple for stable
serialization). ``deliberately_excluded`` is ALWAYS operator-signed."""

RiskFlagLiteral = Literal[
    "clinical_claim",
    "numeric",
    "dosing",
    "negation",
    "comparator",
    "exemplary_language",
]
"""The risk taxonomy (AC5). Drives the deterministic ``verbatim_required`` floor +
where Vera-R7 binds hardest (token identity)."""

SegmentationGrain = Literal["assertion_level", "block_level_v1"]
"""Provenance stamp for HOW the point was segmented (AC2). ``block_level_v1`` is a
DIAGNOSTIC-only value (AC-OP1) — v1 ships ONLY at ``assertion_level``; it is never
a valid v1 ship state. The stamp is load-bearing (Irene) — declared on the report
face, never dropped."""

_COVERAGE_INTENT_ADAPTER: TypeAdapter[CoverageIntentLiteral] = TypeAdapter(CoverageIntentLiteral)
_RISK_FLAG_ADAPTER: TypeAdapter[RiskFlagLiteral] = TypeAdapter(RiskFlagLiteral)
_SEGMENTATION_ADAPTER: TypeAdapter[SegmentationGrain] = TypeAdapter(SegmentationGrain)

COVERAGE_INTENTS: Final[frozenset[str]] = frozenset(_COVERAGE_INTENT_ADAPTER.json_schema()["enum"])
RISK_FLAGS: Final[frozenset[str]] = frozenset(_RISK_FLAG_ADAPTER.json_schema()["enum"])
SEGMENTATION_GRAINS: Final[frozenset[str]] = frozenset(_SEGMENTATION_ADAPTER.json_schema()["enum"])

# ---------------------------------------------------------------------------
# Deterministic verbatim-required floor (AC5)
# ---------------------------------------------------------------------------

VERBATIM_REQUIRED_RISK_FLOOR: Final[frozenset[str]] = frozenset(
    {"clinical_claim", "numeric", "dosing", "negation", "comparator"}
)
"""Risk flags that FORCE ``verbatim_required`` (numbers / doses / negations /
comparators / named clinical terms). LLM/operator may NOT downgrade this floor.
``exemplary_language`` is the only risk flag NOT in the floor (illustrative phrasing
is not token-identity-critical)."""

# Import-time exhaustiveness guard: the floor must be a clean SUBSET-partition of the
# closed risk taxonomy (every member classified floor-or-not; no phantom member). A
# future risk-flag addition fails here until it is dispositioned. A plain ``assert``
# would be stripped under ``python -O`` — raise explicitly.
_VERBATIM_FLOOR_NON_MEMBERS: Final[frozenset[str]] = RISK_FLAGS - VERBATIM_REQUIRED_RISK_FLOOR
if not VERBATIM_REQUIRED_RISK_FLOOR <= RISK_FLAGS:  # pragma: no cover - import-time invariant
    raise RuntimeError(
        "verbatim-required floor carries a phantom risk flag: "
        f"{VERBATIM_REQUIRED_RISK_FLOOR - RISK_FLAGS}"
    )
if (VERBATIM_REQUIRED_RISK_FLOOR | _VERBATIM_FLOOR_NON_MEMBERS) != RISK_FLAGS:  # pragma: no cover
    raise RuntimeError(
        "verbatim-required floor partition is non-exhaustive over the risk taxonomy: "
        f"unassigned={RISK_FLAGS - (VERBATIM_REQUIRED_RISK_FLOOR | _VERBATIM_FLOOR_NON_MEMBERS)}"
    )

# Risk flags that, when present, FORCE both-surface coverage (visible AND spoken):
# a safety/clinical caution or a negation must reach a screen AND the narration
# (AC3 "forced BOTH"). Comparator/numeric/dosing are verbatim-critical but not
# automatically dual-surface (a numeral may legitimately live on the slide alone).
_FORCE_BOTH_RISK: Final[frozenset[str]] = frozenset({"clinical_claim", "negation"})


def verbatim_required_for(risk_flags: tuple[str, ...] | frozenset[str]) -> bool:
    """Deterministic ``verbatim_required`` floor: True iff any floor risk flag present.

    Pure, no LLM (AC5/AC7). This is the SOLE authority for ``verbatim_required`` —
    the model validator recomputes the field from it so a stored value can never
    diverge.
    """
    return bool(set(risk_flags) & VERBATIM_REQUIRED_RISK_FLOOR)


# ---------------------------------------------------------------------------
# Child-id helpers (AC1 — id rides the existing component_id space)
# ---------------------------------------------------------------------------

_SOURCE_POINT_ID_RE: Final[re.Pattern[str]] = re.compile(r"^(?P<parent>.+)#(?P<ordinal>\d+)$")


def make_source_point_id(component_id: str, ordinal: int) -> str:
    """Mint a child sub-locator id ``component_id#ordinal`` (AC1).

    NOT a join key — see :func:`join_key`. ``ordinal`` is 1-based per the parent
    component's note block.
    """
    if not component_id or "#" in component_id:
        raise ValueError(
            f"component_id {component_id!r} must be non-empty and contain no '#' "
            "(the '#' delimits the child ordinal)"
        )
    if ordinal < 1:
        raise ValueError(f"ordinal must be >= 1 (1-based), got {ordinal}")
    return f"{component_id}#{ordinal}"


def parent_component_id_of(source_point_id: str) -> str:
    """The PARENT ``component_id`` of a child source-point id (the join authority)."""
    match = _SOURCE_POINT_ID_RE.match(source_point_id)
    if match is None:
        raise ValueError(
            f"source_point_id {source_point_id!r} is not a 'component_id#ordinal' child id"
        )
    return match.group("parent")


def ordinal_of(source_point_id: str) -> int:
    """The 1-based ordinal of a child source-point id."""
    match = _SOURCE_POINT_ID_RE.match(source_point_id)
    if match is None:
        raise ValueError(
            f"source_point_id {source_point_id!r} is not a 'component_id#ordinal' child id"
        )
    return int(match.group("ordinal"))


def join_key(point: SourcePoint) -> str:
    """The ONLY sanctioned join surface for a source point: its PARENT component_id.

    Winston caveat (BINDING): the ``#ordinal`` child id is NEVER a join key. Every
    downstream join (component→slide locator, LO→section, narration role-seed) keys
    on this parent id; source points are projection rows under it.
    """
    return point.component_id


def assert_join_key(candidate: str) -> str:
    """Guard: REFUSE a child ``#ordinal`` id used as a join key (Winston caveat).

    Raises if ``candidate`` is a child sub-locator (contains the ``#ordinal``
    suffix). Use at any join site that accepts an id, so a child id smuggled into a
    join fails loud rather than silently fanning out a projection row into a key.
    """
    if _SOURCE_POINT_ID_RE.match(candidate) is not None:
        raise ValueError(
            f"join key {candidate!r} is a source-point CHILD id (#ordinal) — joins MUST "
            "key on the parent component_id (Winston caveat, AC1). Use join_key(point)."
        )
    return candidate


# ---------------------------------------------------------------------------
# Derived-first coverage-intent assignment (AC3)
# ---------------------------------------------------------------------------


def derive_coverage_intents(
    *,
    source_type: str | None,
    pedagogical_role: str | None,
    lo_load_bearing: bool,
    risk_flags: tuple[str, ...] | frozenset[str],
    is_organizing_claim: bool = False,
) -> tuple[CoverageIntentLiteral, ...]:
    """Derived-first coverage-intent SET (AC3) — no LLM on the deterministic path.

    Default **slides=gist, narration=detail**. Forced **BOTH** (gist_on_slide AND
    detail_in_narration) when the point is LO-load-bearing OR a safety/clinical
    caution/negation OR the slide's organizing claim. ``deliberately_excluded`` is
    NEVER auto-derived — it is operator-signed only (AC3, no silent exclusion).

    The LLM refines only at AMBIGUITY (and only at a resolved anchor — Murat); this
    deterministic seed is the default the refinement may widen, never silently drop.
    """
    flags = set(risk_flags)
    force_both = lo_load_bearing or is_organizing_claim or bool(flags & _FORCE_BOTH_RISK)
    intents: set[CoverageIntentLiteral] = set()
    if force_both:
        intents.update(("gist_on_slide", "detail_in_narration"))
    elif source_type == "narration":
        intents.add("detail_in_narration")
    else:  # slide / default visible surface
        intents.add("gist_on_slide")
    return tuple(sorted(intents))


# ---------------------------------------------------------------------------
# The source-point model
# ---------------------------------------------------------------------------


class SourcePoint(BaseModel):
    """One teaching assertion re-segmented from a slide's presentation-note block.

    Frozen value object. ``source_point_id`` MUST equal ``component_id#ordinal``
    (AC1); ``verbatim_required`` is DERIVED from ``risk_flags`` (AC5);
    ``coverage_intents`` is a non-empty unique set (AC3); a ``deliberately_excluded``
    intent REQUIRES ``operator_signed_exclusion`` (no silent exclusion).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    source_point_id: str = Field(
        ..., min_length=1, description="Child sub-locator 'component_id#ordinal' (AC1)."
    )
    component_id: str = Field(
        ..., min_length=1, description="Parent TypedComponent id (the JOIN authority)."
    )
    ordinal: int = Field(..., ge=1, description="1-based assertion ordinal within the note block.")
    slide_key: str = Field(
        ..., min_length=1, description="The parent's existing 'Slide N' locator key."
    )
    verbatim_text: str = Field(
        ...,
        min_length=1,
        description="VERBATIM source span the assertion was cut from (identity anchor).",
    )
    risk_flags: tuple[RiskFlagLiteral, ...] = Field(
        default=(),
        description="Risk taxonomy membership (AC5); unique + sorted; drives verbatim floor.",
    )
    coverage_intents: tuple[CoverageIntentLiteral, ...] = Field(
        ...,
        description="Non-empty unique intent SET (AC3); sorted for stable serialization.",
    )
    segmentation: SegmentationGrain = Field(
        ...,
        description="Provenance grain (AC2, load-bearing). v1 ships only 'assertion_level'.",
    )
    verbatim_required: bool = Field(
        default=False,
        description="DERIVED floor (AC5): recomputed from risk_flags; cannot be overridden.",
    )
    operator_signed_exclusion: bool = Field(
        default=False,
        description="True iff an operator signed a 'deliberately_excluded' intent (AC3).",
    )

    @field_validator("risk_flags", mode="before")
    @classmethod
    def _round_trip_risk(cls, value: object) -> object:
        if value is None:
            return ()
        items = list(value) if isinstance(value, (list, tuple, set, frozenset)) else [value]
        # Surface 3: TypeAdapter round-trip on each member; dedupe + sort for stability.
        validated = {_RISK_FLAG_ADAPTER.validate_python(v) for v in items}
        return tuple(sorted(validated))

    @field_validator("coverage_intents", mode="before")
    @classmethod
    def _round_trip_intents(cls, value: object) -> object:
        if value is None or (isinstance(value, (list, tuple, set, frozenset)) and not value):
            raise ValueError("coverage_intents must be a NON-EMPTY set (AC3)")
        items = list(value) if isinstance(value, (list, tuple, set, frozenset)) else [value]
        validated = {_COVERAGE_INTENT_ADAPTER.validate_python(v) for v in items}
        return tuple(sorted(validated))

    @field_validator("segmentation", mode="before")
    @classmethod
    def _round_trip_segmentation(cls, value: object) -> object:
        return _SEGMENTATION_ADAPTER.validate_python(value)

    @model_validator(mode="after")
    def _enforce_invariants(self) -> SourcePoint:
        # AC1: the child id is exactly component_id#ordinal (no parallel registry).
        expected_id = f"{self.component_id}#{self.ordinal}"
        if self.source_point_id != expected_id:
            raise ValueError(
                f"source_point_id {self.source_point_id!r} must equal "
                f"'component_id#ordinal' = {expected_id!r} (AC1 child-id identity)"
            )
        if "#" in self.component_id:
            raise ValueError(
                f"component_id {self.component_id!r} must not contain '#' (it is the parent "
                "join key, not a child sub-locator)"
            )
        # AC5: verbatim_required is DERIVED — recompute so a stored value can never diverge.
        derived = verbatim_required_for(self.risk_flags)
        if self.verbatim_required != derived:
            object.__setattr__(self, "verbatim_required", derived)
        # AC3: a deliberately_excluded intent is ALWAYS operator-signed (no silent exclusion).
        if "deliberately_excluded" in self.coverage_intents and not self.operator_signed_exclusion:
            raise ValueError(
                "a 'deliberately_excluded' coverage intent REQUIRES operator_signed_exclusion=True "
                "(AC3: no silent exclusion)"
            )
        return self

    def parent_join_key(self) -> str:
        """Convenience: the parent component_id (NEVER the child id) for joins."""
        return self.component_id


def source_point_json_schema() -> dict[str, Any]:
    """Emit the canonical JSON Schema for the :class:`SourcePoint` family."""
    return SourcePoint.model_json_schema()


def load_source_point(payload: dict[str, Any]) -> SourcePoint:
    """Re-hydrate a :class:`SourcePoint` from a dict (closed-enum violations rejected)."""
    return SourcePoint.model_validate(payload)


__all__ = [
    "COVERAGE_INTENTS",
    "RISK_FLAGS",
    "SEGMENTATION_GRAINS",
    "VERBATIM_REQUIRED_RISK_FLOOR",
    "CoverageIntentLiteral",
    "RiskFlagLiteral",
    "SegmentationGrain",
    "SourcePoint",
    "assert_join_key",
    "derive_coverage_intents",
    "join_key",
    "load_source_point",
    "make_source_point_id",
    "ordinal_of",
    "parent_component_id_of",
    "source_point_json_schema",
    "verbatim_required_for",
]
