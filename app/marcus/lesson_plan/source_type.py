"""Closed source-TYPE taxonomy for the G0-enrichment brick (Story G0-S2).

The TYPE of a source span is recorded INDEPENDENTLY of its
:class:`~app.composers.section_02a.directive_model.DirectiveRole` (the operator
PRIMARY/SUPPORTING/IGNORED binding). A ``discussion_forum`` or ``quiz`` span may
still carry role ``supporting`` — TYPE answers "what kind of artifact is this?",
role answers "how should the deck pipeline treat it?". They are orthogonal and
must never be overloaded onto one field (charter D1; ratification §4 A6).

Authority: ``g0-enrichment-cycle-charter-2026-06-26.md`` D1 (10-type closed enum
+ ``other:<label>`` escape hatch) and ``lo-schema-ratification-2026-06-26.md``
§4 A10 (classification-only types are surfaced FLAGGED — no generator consumes
them today).

Pydantic-v2 idioms (docs/dev-guide/pydantic-v2-schema-checklist.md):
    - ``ConfigDict(extra="forbid", validate_assignment=True)`` on every model.
    - The closed enum gets THREE red-rejection surfaces: a Pydantic ``Literal``
      validator (``mode="before"`` adapter), the JSON-Schema ``enum`` array, and
      a ``TypeAdapter`` round-trip — a value outside the set is rejected at all
      three (checklist §4).
"""

from __future__ import annotations

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

# ---------------------------------------------------------------------------
# Closed 10-type enum (three red-rejection surfaces)
# ---------------------------------------------------------------------------

SourceTypeLiteral = Literal[
    "slide",
    "quiz",
    "workbook",
    "narration",
    "reference_citation",
    "rubric",
    "exercise_lab",
    "motion_script_storyboard",
    "discussion_forum",
    "assignment_instructions",
]
"""The closed 10-type source taxonomy (charter D1). ``other:<label>`` is NOT a
member — an ad-hoc type rides the structured escape-hatch shape below, never a
free string folded into this enum (that would silently widen the closed set)."""

SOURCE_TYPE_ADAPTER: TypeAdapter[SourceTypeLiteral] = TypeAdapter(SourceTypeLiteral)

# The closed 10-type set widened by the structured ``other`` escape-hatch
# discriminator — the value space for an assigned TYPE on a span/component. Shared
# by :class:`TypedSource` and :class:`TypedComponent` so the assignable taxonomy
# is single-sourced (a member added to the closed enum widens both by construction).
SourceTypeOrOtherLiteral = Literal[
    "slide",
    "quiz",
    "workbook",
    "narration",
    "reference_citation",
    "rubric",
    "exercise_lab",
    "motion_script_storyboard",
    "discussion_forum",
    "assignment_instructions",
    "other",
]

SOURCE_TYPES: Final[frozenset[str]] = frozenset(SOURCE_TYPE_ADAPTER.json_schema()["enum"])
"""Surface 2: the JSON-Schema ``enum`` array (derived, not hand-maintained — a
drift between the Literal and this set is impossible by construction)."""

# Types with NO generator that consumes them today (ratification §4 A10): they
# are CLASSIFICATION-ONLY and surfaced FLAGGED so the operator knows the typing
# is recorded but never routed into generation in v1. ``slide`` /
# ``motion_script_storyboard`` / ``workbook`` / ``narration`` DO have producers.
CLASSIFICATION_ONLY_TYPES: Final[frozenset[str]] = frozenset(
    {
        "quiz",
        "rubric",
        "exercise_lab",
        "reference_citation",
        "discussion_forum",
        "assignment_instructions",
    }
)

# The complement: types a generator consumes today (advisory consumer-map view).
CONSUMED_TYPES: Final[frozenset[str]] = SOURCE_TYPES - CLASSIFICATION_ONLY_TYPES


def is_classification_only(source_type: str) -> bool:
    """True iff ``source_type`` has no generator consumer today (A10 flag)."""
    return source_type in CLASSIFICATION_ONLY_TYPES


# ---------------------------------------------------------------------------
# Escape-hatch shape: a structured {kind:"other", label} (never a bare string)
# ---------------------------------------------------------------------------


class OtherSourceType(BaseModel):
    """The ``other:<label>`` escape hatch as a STRUCTURED object.

    An ad-hoc source kind the closed enum does not cover is recorded as a
    structured ``{kind:"other", label:"..."}`` value with mandatory provenance,
    surfaced FLAGGED as unconsumed/ad-hoc — never silently routed to a generator
    (charter D1). ``kind`` is a closed one-value literal so the escape hatch
    cannot itself drift into a second open taxonomy.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    kind: Literal["other"] = Field(
        default="other",
        description="Closed one-value discriminator marking the escape-hatch shape.",
    )
    label: str = Field(
        ...,
        description="Free-text ad-hoc type label (verbatim, operator-readable).",
    )
    provenance: str = Field(
        ...,
        description="Why this span fell outside the closed 10-type set (mandatory).",
    )

    @field_validator("label", "provenance")
    @classmethod
    def _reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("other-source-type label/provenance must be non-empty")
        return value


# ---------------------------------------------------------------------------
# A typed source span (TYPE recorded independently of DirectiveRole)
# ---------------------------------------------------------------------------


class TypedSource(BaseModel):
    """One source span's TYPE assignment, orthogonal to its directive role.

    ``source_type`` is exactly one of the closed 10 types OR ``"other"`` paired
    with a populated ``other_type`` escape-hatch object. ``flagged_unconsumed``
    is True whenever the assigned type has no generator today (A10) OR the type
    is the ``other`` escape hatch — so the operator always sees which typings are
    classification-only.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    source_id: str = Field(
        ...,
        min_length=1,
        description="Enumerated corpus source id this typing applies to (A6 set).",
    )
    source_type: Literal[
        "slide",
        "quiz",
        "workbook",
        "narration",
        "reference_citation",
        "rubric",
        "exercise_lab",
        "motion_script_storyboard",
        "discussion_forum",
        "assignment_instructions",
        "other",
    ] = Field(
        ...,
        description="Closed 10-type assignment, or 'other' (escape hatch).",
    )
    other_type: OtherSourceType | None = Field(
        default=None,
        description="Populated escape-hatch object iff source_type == 'other'.",
    )
    flagged_unconsumed: bool = Field(
        default=False,
        description="True iff this type has no generator today (A10) or is 'other'.",
    )

    @field_validator("source_type", mode="before")
    @classmethod
    def _reject_unknown_type(cls, value: object) -> object:
        # Surface 3: TypeAdapter round-trip. 'other' is the only non-enum value
        # accepted; everything else must validate against the closed Literal.
        if value == "other":
            return value
        return SOURCE_TYPE_ADAPTER.validate_python(value)

    @model_validator(mode="after")
    def _enforce_escape_hatch_and_flag(self) -> TypedSource:
        if self.source_type == "other":
            if self.other_type is None:
                raise ValueError(
                    "source_type='other' requires a populated other_type "
                    "(structured {kind:'other', label, provenance})"
                )
        elif self.other_type is not None:
            raise ValueError(
                "other_type is only valid when source_type=='other' "
                f"(got source_type={self.source_type!r})"
            )
        # A10: the flag is a DERIVED truth — recompute it so a hand-set flag can
        # never disagree with the consumer-map (no silently-mis-flagged typing).
        should_flag = self.source_type == "other" or is_classification_only(self.source_type)
        if self.flagged_unconsumed != should_flag:
            object.__setattr__(self, "flagged_unconsumed", should_flag)
        return self


# ---------------------------------------------------------------------------
# A typed intra-document COMPONENT (the unit a file is segmented INTO)
# ---------------------------------------------------------------------------


class TypedComponent(BaseModel):
    """One typed instructional COMPONENT extracted from WITHIN a source file.

    A single enumerated FILE (the A6 unit) yields N ``TypedComponent`` rows — the
    LLM Instructional-Designer pass segments the document into the typed
    components embedded inline (slides, narration, quiz, motion, discussion,
    learning objectives, ...), each anchored by a document-hierarchy ``locator``
    (``Course > Module > Part > Page/Slide`` path) and a VERBATIM ``excerpt``.
    This REPLACES the prior file-level typing (one whole file → one type); a
    150KB outline that is all 'other' under file-typing becomes 188 typed
    components under component extraction (charter P1).

    ``source_type`` is exactly one of the closed 10 types OR ``"other"`` paired
    with a populated ``other_type`` escape-hatch object (orthogonal to the
    operator PRIMARY/SUPPORTING/IGNORED directive role, charter D1).
    ``flagged_unconsumed`` is DERIVED (A10): True whenever the assigned type has
    no generator today OR is the ``other`` escape hatch.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    component_id: str = Field(
        ...,
        min_length=1,
        description="Stable component id, unique within a run (e.g. 'src-001-c003').",
    )
    parent_source_id: str = Field(
        ...,
        min_length=1,
        description="Enumerated FILE id (A6 set) this component was extracted from.",
    )
    source_type: SourceTypeOrOtherLiteral = Field(
        ...,
        description="Closed 10-type assignment, or 'other' (escape hatch).",
    )
    other_type: OtherSourceType | None = Field(
        default=None,
        description="Populated escape-hatch object iff source_type == 'other'.",
    )
    label: str = Field(
        ...,
        min_length=1,
        description="Short, human-readable label for the component (verbatim heading/intent).",
    )
    locator: str = Field(
        ...,
        min_length=1,
        description="Document-hierarchy path (Course > Module > Part > Page/Slide).",
    )
    excerpt: str = Field(
        ...,
        min_length=1,
        description="VERBATIM excerpt of the component drawn from the parent document.",
    )
    flagged_unconsumed: bool = Field(
        default=False,
        description="True iff this type has no generator today (A10) or is 'other'.",
    )
    flagged_ungrounded: bool = Field(
        default=False,
        description=(
            "ADVISORY (P1): True iff the excerpt could NOT be found in the parent "
            "source after markdown normalization (a possible fabrication). Set by "
            "the post-extraction groundedness check, never gating — the operator "
            "confirms at gate #1. Distinct from the DERIVED flagged_unconsumed: "
            "this flag is set externally and is NOT recomputed by the validator."
        ),
    )

    @field_validator("source_type", mode="before")
    @classmethod
    def _reject_unknown_type(cls, value: object) -> object:
        # 'other' is the only non-enum value accepted; everything else validates
        # against the closed Literal (TypeAdapter round-trip, surface 3).
        if value == "other":
            return value
        return SOURCE_TYPE_ADAPTER.validate_python(value)

    @model_validator(mode="after")
    def _enforce_escape_hatch_and_flag(self) -> TypedComponent:
        if self.source_type == "other":
            if self.other_type is None:
                raise ValueError(
                    "source_type='other' requires a populated other_type "
                    "(structured {kind:'other', label, provenance})"
                )
        elif self.other_type is not None:
            raise ValueError(
                "other_type is only valid when source_type=='other' "
                f"(got source_type={self.source_type!r})"
            )
        # A10: the flag is a DERIVED truth — recompute so a hand-set flag can never
        # disagree with the consumer-map (no silently-mis-flagged component).
        should_flag = self.source_type == "other" or is_classification_only(self.source_type)
        if self.flagged_unconsumed != should_flag:
            object.__setattr__(self, "flagged_unconsumed", should_flag)
        return self


__all__ = [
    "CLASSIFICATION_ONLY_TYPES",
    "CONSUMED_TYPES",
    "SOURCE_TYPES",
    "SOURCE_TYPE_ADAPTER",
    "OtherSourceType",
    "SourceTypeLiteral",
    "SourceTypeOrOtherLiteral",
    "TypedComponent",
    "TypedSource",
    "is_classification_only",
]
