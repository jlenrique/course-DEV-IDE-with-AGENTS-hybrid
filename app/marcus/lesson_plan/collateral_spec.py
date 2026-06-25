"""CollateralSpec content-model family (Braid S1 — DP4).

The *spec* the client's workbook is built from. Emitted additively on the
Irene Pass-1 ``lesson_plan["collateral"]`` key alongside the slide brief /
plan-units. S2 (workbook producer) imports this family as the SINGLE source of
truth; S3 (thin research wiring) resolves the ``answer_key_source_ref`` /
research-goal slots to real source references.

Content-model discipline (binding from DP4):
    - Every workbook section binds a ``learning_objective_id`` (the asset-lesson
      pairing invariant extended to collateral). A section with no objective is
      a contract violation, not a soft warning.
    - Every section carries a ``depth_delta`` contract — the explicit
      declaration of what depth is deferred OFF the glance-slide INTO the
      workbook. This is the load-bearing field: it legitimizes the deck's tight
      voiceover (the glance-deck and the read-in-depth workbook are dual-coding
      partners).
    - Exercises carry a Bloom level (closed enum) + a source-grounded
      ``answer_key_source_ref`` slot (authored backward from sourced content,
      honesty-gate G3). S1 emits the structurally-valid reference + intent; the
      worked solution is the producer's job (S2).
    - Research-enrichment goals are expressed as pedagogical intent, NOT raw
      fetch queries. S3 translates intent -> fetch; S1 must not pre-empt that
      boundary (a conservative, false-positive-averse validator rejects obvious
      raw-query shapes).

Additive / no-regression invariant: the empty case is an explicit
``declaration="none"`` decision-on-record, NOT an absent key. It round-trips to
today's deck-only behavior with zero regression.

Pydantic-v2 idioms (see docs/dev-guide/pydantic-v2-schema-checklist.md):
    - ``ConfigDict(extra="forbid", validate_assignment=True)`` on every model;
      ``frozen=True`` on the ``DepthDeltaContract`` value-object.
    - Closed ``BloomLevel`` enum with three red-rejection surfaces (Pydantic
      validator via Literal, JSON-Schema ``enum`` array, ``TypeAdapter``
      round-trip).
    - Free-text verbatim fields carry NO ``min_length`` (empty / whitespace /
      emoji all accepted; stored verbatim). EXCEPTIONS (reject whitespace-only,
      same bar as ``answer_key_source_ref``): ``deferred_depth`` — the
      load-bearing dual-coding field; whitespace-only names no deferred depth
      (party-close ruling 2026-06-25). Non-whitespace content is still verbatim.
    - ``OPEN_ID_REGEX_PATTERN`` reused from the single-source registry (no
      regex fork) for every id / objective-binding field, matching the
      ``ProducedAsset`` open-id contract so S2 can bind asset -> objective.

Discipline note (R1 ruling amendment 17 / R2 rider S-3): Marcus is one voice;
no split-role terminology in descriptions, docstrings, or error messages.
"""

from __future__ import annotations

import re
from typing import Final, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

# Single-source open-id regex. Canonical home is event_type_registry (the same
# symbol ProducedAsset.source_plan_unit_id pins via produced_asset.py); reused
# here so objective-id binding cannot fork the regex.
from app.marcus.lesson_plan.event_type_registry import OPEN_ID_REGEX_PATTERN

SCHEMA_VERSION: Final[str] = "1.0"
"""CollateralSpec family schema version; bump on shape drift (per CHANGELOG)."""


_OPEN_ID_REGEX: Final[re.Pattern[str]] = re.compile(OPEN_ID_REGEX_PATTERN)


# ---------------------------------------------------------------------------
# Bloom level — closed enum (three red-rejection surfaces)
# ---------------------------------------------------------------------------

BloomLevel = Literal[
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
]
"""The six revised-Bloom cognitive levels. Closed set: a red value is rejected
at construction (Literal), in the emitted JSON Schema (``enum`` array), and via
a ``TypeAdapter`` round-trip."""


# ---------------------------------------------------------------------------
# Raw-fetch-query heuristic (AC-5 boundary keeper)
# ---------------------------------------------------------------------------

# Conservative, false-positive-averse. A pedagogical-intent string is REJECTED
# only when it is *obviously* a raw fetch query rather than a learning goal:
#   - it contains a URL (http/https scheme), OR
#   - it is search-engine "boolean-operator soup": it uses bare boolean
#     operators (AND / OR / NOT as standalone uppercase tokens) AND carries a
#     query-syntax marker (a quoted phrase or parenthesized group).
# Plain prose that merely *mentions* a topic, a year, or a percentage is
# accepted — those are legitimate intent phrasings (near-boundary case).
_URL_REGEX: Final[re.Pattern[str]] = re.compile(r"https?://", flags=re.IGNORECASE)
_BOOLEAN_OP_REGEX: Final[re.Pattern[str]] = re.compile(r"\b(AND|OR|NOT)\b")
_QUERY_SYNTAX_REGEX: Final[re.Pattern[str]] = re.compile(r'".+?"|\(.+?\)')


def _looks_like_raw_fetch_query(text: str) -> bool:
    """Return True iff ``text`` is obviously a raw fetch query, not intent.

    Documented heuristic (AC-5): false-positive-averse. We reject a URL outright
    and reject boolean-operator soup only when paired with query syntax (quotes
    or parentheses). Everything else — including prose that mentions a number, a
    year, or a topic a researcher might later search — is accepted as intent so
    S1 never pre-empts S3's fetch translation.
    """
    if _URL_REGEX.search(text):
        return True
    has_boolean = bool(_BOOLEAN_OP_REGEX.search(text))
    has_query_syntax = bool(_QUERY_SYNTAX_REGEX.search(text))
    return has_boolean and has_query_syntax


def _validate_open_id(value: str, *, field_label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_label} must be a non-empty open-id string")
    if not _OPEN_ID_REGEX.match(value):
        raise ValueError(
            f"{field_label} {value!r} fails open-id regex {OPEN_ID_REGEX_PATTERN}"
        )
    return value


# ---------------------------------------------------------------------------
# DepthDeltaContract — frozen value-object (the load-bearing field)
# ---------------------------------------------------------------------------


class DepthDeltaContract(BaseModel):
    """What depth is deferred OFF the glance-slide INTO the workbook.

    The dual-coding anchor: the deck's tight voiceover stays tight precisely
    because the workbook carries the deferred depth named here. Frozen
    value-object — its identity is its content.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    deferred_from_slide: str = Field(
        ...,
        description=(
            "Open-id of the glance-slide / plan-unit whose depth is deferred "
            "into the workbook (the dual-coding anchor)."
        ),
    )
    deferred_depth: str = Field(
        ...,
        description=(
            "Free-text, verbatim: what depth moves off the glance-slide into "
            "the workbook. The legitimization of the tight slide voiceover."
        ),
    )
    retained_on_slide: str | None = Field(
        default=None,
        description=(
            "Free-text, verbatim: what stays at glance altitude on the slide "
            "(helps the producer avoid re-stating it). Optional."
        ),
    )

    @field_validator("deferred_from_slide")
    @classmethod
    def _slide_is_open_id(cls, value: str) -> str:
        return _validate_open_id(value, field_label="deferred_from_slide")

    @field_validator("deferred_depth")
    @classmethod
    def _deferred_depth_non_empty(cls, value: str) -> str:
        # The load-bearing dual-coding field: an empty / whitespace-only
        # deferred_depth names no deferred depth (silent absence of the thing the
        # contract exists to carry). Reject whitespace-only, mirroring
        # answer_key_source_ref (party-close ruling 2026-06-25). Non-whitespace
        # content is still stored verbatim (free-text; surrounding space kept).
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                "deferred_depth must name the depth deferred off the glance-slide "
                "(whitespace-only is malformed; it is the load-bearing dual-coding "
                "field)"
            )
        return value


# ---------------------------------------------------------------------------
# Exercise — Bloom level + source-grounded answer-key reference (G3)
# ---------------------------------------------------------------------------


class Exercise(BaseModel):
    """A workbook exercise carrying a Bloom level + a source-grounded
    answer-key reference slot.

    Honesty-gate G3: ``answer_key_source_ref`` is a structurally-valid
    reference slot authored backward from sourced content — not a fabricated
    citation, and not the worked solution (the producer composes prose under
    G1; S3 resolves the reference to a real source).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    exercise_id: str = Field(
        ...,
        description="Open-id stable identifier for this exercise.",
    )
    bloom_level: BloomLevel = Field(
        ...,
        description=(
            "Revised-Bloom cognitive level (closed set). Red values rejected at "
            "construction, in the JSON Schema enum, and via TypeAdapter."
        ),
    )
    prompt_intent: str = Field(
        ...,
        description=(
            "Free-text, verbatim: the exercise's pedagogical intent. The worked "
            "prompt prose is composed by the producer, not here."
        ),
    )
    answer_key_source_ref: str = Field(
        ...,
        description=(
            "Source-grounded answer-key reference slot (source_ref shape). A "
            "structurally-valid reference the research wiring resolves to a real "
            "source; never a fabricated citation."
        ),
    )

    @field_validator("exercise_id")
    @classmethod
    def _exercise_id_open_id(cls, value: str) -> str:
        return _validate_open_id(value, field_label="exercise_id")

    @field_validator("answer_key_source_ref")
    @classmethod
    def _answer_key_source_ref_shape(cls, value: str) -> str:
        # source_ref shape: a non-empty, non-whitespace traceable reference.
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                "answer_key_source_ref must be a non-empty source_ref-shaped "
                "string (whitespace-only is malformed)"
            )
        return value


# ---------------------------------------------------------------------------
# WorkbookSection — the content-model heart
# ---------------------------------------------------------------------------


class WorkbookSection(BaseModel):
    """One workbook section, bound to a learning objective.

    The asset-lesson pairing invariant extended to collateral: every section
    binds a ``learning_objective_id`` and carries a required ``depth_delta``.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    section_id: str = Field(
        ...,
        description="Open-id stable identifier for this workbook section.",
    )
    learning_objective_id: str = Field(
        ...,
        description=(
            "Open-id of the learning objective this section serves (the "
            "asset-lesson pairing invariant; required, never empty). Reuses the "
            "single-source open-id regex so the producer can bind "
            "asset -> objective without a regex fork."
        ),
    )
    title: str = Field(
        ...,
        description="Free-text, verbatim: the section title.",
    )
    depth_delta: DepthDeltaContract = Field(
        ...,
        description=(
            "Required: the depth-delta contract naming what depth is deferred "
            "off the glance-slide into this section (the load-bearing field)."
        ),
    )
    exercises: list[Exercise] = Field(
        default_factory=list,
        description=(
            "Exercises for this section (may be empty for a pure-narrative "
            "section). Each carries a Bloom level + answer-key reference."
        ),
    )
    narrative_intent: str = Field(
        default="",
        description=(
            "Free-text, verbatim: the fuller-narrative brief for this section. "
            "Prose is composed by the producer under G1, not here."
        ),
    )

    @field_validator("section_id")
    @classmethod
    def _section_id_open_id(cls, value: str) -> str:
        return _validate_open_id(value, field_label="section_id")

    @field_validator("learning_objective_id")
    @classmethod
    def _objective_id_open_id(cls, value: str) -> str:
        return _validate_open_id(value, field_label="learning_objective_id")


# ---------------------------------------------------------------------------
# WorkbookSpec
# ---------------------------------------------------------------------------


class WorkbookSpec(BaseModel):
    """The workbook content model — a non-empty list of bound sections."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    sections: list[WorkbookSection] = Field(
        ...,
        description="Workbook sections; non-empty when collateral is present.",
    )


# ---------------------------------------------------------------------------
# ResearchEnrichmentGoal — pedagogical intent, NOT a fetch query
# ---------------------------------------------------------------------------


class ResearchEnrichmentGoal(BaseModel):
    """A research-enrichment goal expressed as pedagogical intent.

    The boundary keeper: a conservative, false-positive-averse validator
    rejects obvious raw fetch-query shapes (URLs, boolean-operator soup) so S1
    emits *intent* and the research wiring (S3) owns intent -> fetch.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    goal_id: str = Field(
        ...,
        description="Open-id stable identifier for this research-enrichment goal.",
    )
    pedagogical_intent: str = Field(
        ...,
        description=(
            "Free-text, verbatim: the pedagogical reason the learner needs "
            "enrichment (e.g. 'learner needs the primary-source basis for the "
            "23% figure'). Must be intent, not a raw fetch query."
        ),
    )
    binds_to_objective_id: str | None = Field(
        default=None,
        description=(
            "Optional open-id linkage to a workbook section's learning "
            "objective; null when the goal is not section-scoped."
        ),
    )

    @field_validator("goal_id")
    @classmethod
    def _goal_id_open_id(cls, value: str) -> str:
        return _validate_open_id(value, field_label="goal_id")

    @field_validator("binds_to_objective_id")
    @classmethod
    def _binds_open_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_open_id(value, field_label="binds_to_objective_id")

    @field_validator("pedagogical_intent")
    @classmethod
    def _intent_not_raw_query(cls, value: str) -> str:
        if _looks_like_raw_fetch_query(value):
            raise ValueError(
                "pedagogical_intent must express a learning goal, not a raw "
                "fetch query (URL / boolean-operator query rejected); express "
                "the intent and let the research wiring translate it to a fetch"
            )
        return value


# ---------------------------------------------------------------------------
# CollateralSpec — top-level (carried on lesson_plan["collateral"])
# ---------------------------------------------------------------------------


class CollateralSpec(BaseModel):
    """The DP4 collateral content model carried on ``lesson_plan["collateral"]``.

    ``declaration`` is the explicit empty-case discriminant: ``"none"`` is the
    on-record decision that this lesson ships deck-only (degenerate-empty),
    NOT an absent key; ``"present"`` requires a workbook with >=1 section.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: str = Field(
        default=SCHEMA_VERSION,
        description="Pinned to SCHEMA_VERSION; changes drive CHANGELOG entries.",
    )
    declaration: Literal["present", "none"] = Field(
        ...,
        description=(
            "Explicit empty-case discriminant. 'none' = on-record decision to "
            "ship deck-only; 'present' requires a workbook with >=1 section."
        ),
    )
    workbook: WorkbookSpec | None = Field(
        default=None,
        description=(
            "The workbook content model; present iff declaration == 'present'."
        ),
    )
    research_goals: list[ResearchEnrichmentGoal] = Field(
        default_factory=list,
        description=(
            "Research-enrichment goals (pedagogical intent). May be empty even "
            "when declaration == 'present'; research is enrichment, not "
            "mandatory for a workbook section."
        ),
    )

    @model_validator(mode="after")
    def _discriminant_matches_payload(self) -> CollateralSpec:
        """Bypass-guard: the discriminant must match the payload (checklist §13)."""
        if self.declaration == "present":
            if self.workbook is None or not self.workbook.sections:
                raise ValueError(
                    "declaration == 'present' requires a workbook with at least "
                    "one section"
                )
        else:  # declaration == "none"
            if self.workbook is not None:
                raise ValueError(
                    "declaration == 'none' requires workbook is None (the "
                    "deck-only decision carries no workbook payload)"
                )
        return self


__all__ = [
    "SCHEMA_VERSION",
    "BloomLevel",
    "CollateralSpec",
    "DepthDeltaContract",
    "Exercise",
    "ResearchEnrichmentGoal",
    "WorkbookSection",
    "WorkbookSpec",
]
