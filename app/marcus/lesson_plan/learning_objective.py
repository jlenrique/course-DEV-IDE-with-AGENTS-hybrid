"""Canonical Learning Objective (LO) entity + transition guard (Story G0-S1).

This module is the SINGLE source of truth for a provenance-anchored,
lifecycle-aware learning objective. It REPLACES (additively, bridged by the
adapter functions in ``learning_objective_adapters.py``) the three legacy
in-code LO representations:

    1. Irene Pass-1's bare ``learning_objective`` string;
    2. the ``LearningObjectiveBrief`` dataclass (workbook producer);
    3. the open-id content carried on ``WorkbookSection.learning_objective_id``.

The ``learning_objective_map`` DB table keys to ``objective_id`` (role
unchanged = alignment tracking).

Authority: ``_bmad-output/planning-artifacts/lo-schema-ratification-2026-06-26.md``
sections 1-5 + the adequacy-advisory rule (section 3.1).

Architectural note (placement / dependency direction):
    The entity lives at ``app/marcus/lesson_plan/learning_objective.py`` so the
    workbook producer can import it. Import-linter Contract M3 narrowly fences
    only the Maya-facing routing modules from ``app.specialists``; the
    ``app.marcus.lesson_plan`` package is import-legal from
    ``app.specialists.irene_pass1`` (verified ``lint-imports`` clean). To keep the
    dependency graph acyclic for the S3 rewire (when ``collateral_spec`` /
    ``workbook_producer`` will consume this entity), this module depends only on
    the LOW-LEVEL ``event_type_registry`` (the canonical single-source home of
    ``OPEN_ID_REGEX_PATTERN``) and NOT on ``collateral_spec``. No regex fork.

Pydantic-v2 idioms (docs/dev-guide/pydantic-v2-schema-checklist.md):
    - ``ConfigDict(extra="forbid", validate_assignment=True)`` on every model.
    - ``frozen=True`` on the ``SourceRef`` value-object (a provenance locator is
      immutable). ``objective_id`` is per-field ``frozen`` (immutable once
      minted at G0 per ratification 1 / 3 (+e)).
    - Closed enums get three red-rejection surfaces (Pydantic ``Literal``
      validator, JSON-Schema ``enum`` array, ``TypeAdapter`` round-trip).
    - Free-text fields (``statement``, ``rationale``) carry NO ``min_length``.
    - Status state-machine guarded by a ``model_validator(mode="after")``.

Discipline note (R1 ruling amendment 17 / R2 rider S-3): Marcus is one voice; no
split-role terminology in descriptions, docstrings, or error messages.
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
# symbol collateral_spec / produced_asset pin); reused here so objective-id
# binding cannot fork the regex. We import the PATTERN constant (not collateral's
# private helper) to keep this entity module independent of collateral_spec and
# thereby acyclic for the S3 consumer rewire.
from app.marcus.lesson_plan.event_type_registry import OPEN_ID_REGEX_PATTERN

SCHEMA_VERSION: Final[str] = "1.0"
"""LearningObjective family schema version; bump on shape drift (per CHANGELOG).

NOTE: deliberately a MODULE constant, not a model field. The ratified section-1
shape is exact (``extra="forbid"`` + a pinned field-set); adding a
``schema_version`` field would violate "implement exactly the ratified shapes".
The constant keys the committed JSON-Schema witness filename (``.v1.``)."""


_OPEN_ID_REGEX: Final[re.Pattern[str]] = re.compile(OPEN_ID_REGEX_PATTERN)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class IllegalTransition(ValueError):  # noqa: N818  # spec-mandated name (ratification 2)
    """Raised by :func:`advance_lo` for any edge outside the closed allow-map."""


# ---------------------------------------------------------------------------
# Closed enums (three red-rejection surfaces each)
# ---------------------------------------------------------------------------

BloomLevel = Literal[
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
]
"""The six revised-Bloom cognitive levels (closed set)."""

LOStatus = Literal["provisional", "refined", "ratified"]
"""LO lifecycle status (closed set). Status transitions are authority-gated by
:func:`advance_lo`. The VALUE invariants (the status-conditional table) are
enforced at construction and on direct assignment (``validate_assignment=True``).
Note the one Pydantic-v2 escape hatch: ``model_copy(update={...})`` does NOT
re-run validators, so callers MUST route transitions through :func:`advance_lo`
(which re-validates) rather than ``model_copy`` -- the guard owns authority, the
model owns values, and ``model_copy(update=)`` bypasses both by design of
Pydantic. ``source_refs`` is a tuple so the >=1 floor cannot be silently emptied
by in-place list mutation."""

Confidence = Literal["high", "medium", "low"]
"""First-class but ADVISORY confidence band (gates nothing)."""

AdequacyVerdict = Literal["adequate", "thin", "gap"]
"""Source-adequacy verdict. ALERT ONLY: thin/gap NEVER halts the pipeline,
forces a drop, or gates a status transition (ratification 3.1)."""

AdequacyFollowup = Literal[
    "research-run",
    "external-content-expected",
    "special-artifact-guidance",
]
"""Advisory follow-up hint a thin/gap adequacy verdict MAY suggest. Not an
action; the operator decides (ratification 3.1)."""


# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------


class SourceRef(BaseModel):
    """A structured provenance locator (NOT a bare string).

    The ``source_id`` MUST belong to the deterministically-enumerated source set
    at runtime (a fabricated id is a RED at the G0 enumeration boundary, S2); at
    the schema layer it is a non-empty reference string. ``quoted_span`` is a
    VERBATIM substring of the resolved source text (the deterministic
    containment check is an S2 runtime concern).
    """

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    source_id: str = Field(
        ...,
        description="Identifier of the resolved source this reference points at.",
    )
    locator: str = Field(
        ...,
        description="Page / heading / char-span within the source. Verbatim.",
    )
    quoted_span: str = Field(
        ...,
        description="Verbatim substring of the resolved source text.",
    )

    @field_validator("source_id", "locator", "quoted_span")
    @classmethod
    def _reject_empty(cls, value: str) -> str:
        # A provenance locator must be a real reference: a whitespace-only or
        # empty field would satisfy the LearningObjective refined+ "source_refs
        # >= 1" floor with zero real provenance (the hollow-invariant gap T11
        # Edge-Case-Hunter caught). The verbatim-substring containment check
        # stays an S2 runtime concern; non-emptiness is a schema-layer guarantee.
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                "SourceRef fields (source_id/locator/quoted_span) must be "
                "non-empty (whitespace-only is malformed)"
            )
        return value


class SourceAdequacy(BaseModel):
    """Irene's source-adequacy assessment for one LO. ADVISORY (ratification 3.1).

    The ``verdict`` is an ALERT, never a gate: a ``thin``/``gap`` verdict does
    not halt the pipeline, force a drop, or block a status transition. Final
    adequacy determination is the operator + off-world SME, not this app.

    Internal well-formedness (ratification 1, distinct from any pipeline gate):
    ``missing`` must NAME a concrete gap whenever the verdict is ``thin`` or
    ``gap`` (you cannot flag a gap without saying what is missing); it may be
    empty only on ``adequate``. This is data integrity of the adequacy object,
    NOT a verdict-driven pipeline gate, and is wholly independent of the
    :class:`LearningObjective` status invariants (which assert adequacy PRESENCE
    only, never its verdict value).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    verdict: AdequacyVerdict = Field(
        ...,
        description="Adequacy alert: adequate | thin | gap. Advisory, never gating.",
    )
    rationale: str = Field(
        ...,
        description="Free text, verbatim: quotes the supporting or missing span.",
    )
    missing: list[str] = Field(
        default_factory=list,
        description=(
            "Concrete named gaps. Non-empty on a thin/gap verdict; may be empty "
            "only on adequate. Object well-formedness, not a pipeline gate."
        ),
    )
    suggested_followups: list[AdequacyFollowup] = Field(
        default_factory=list,
        description=(
            "Advisory hint a thin/gap flag MAY suggest (e.g. a research run or "
            "special artifact-creation guidance). Never an action."
        ),
    )

    @model_validator(mode="after")
    def _enforce_missing_cardinality(self) -> SourceAdequacy:
        if self.verdict in ("thin", "gap"):
            concrete = [m for m in self.missing if m and m.strip()]
            if not concrete:
                raise ValueError(
                    f"adequacy verdict {self.verdict!r} requires a non-empty, "
                    "concrete 'missing' (name the specific gap)"
                )
        return self


# ---------------------------------------------------------------------------
# Canonical entity
# ---------------------------------------------------------------------------


class LearningObjective(BaseModel):
    """The canonical, provenance-anchored, lifecycle-aware learning objective.

    Status-conditional invariant table (ratification 1), enforced by
    :meth:`_enforce_status_invariants`:

    | field         | provisional | refined        | ratified |
    |---------------|-------------|----------------|----------|
    | ``statement`` | required    | required       | required |
    | ``source_refs``| >=0        | **>=1**        | >=1      |
    | ``bloom_level``| optional   | optional       | **required** |
    | ``adequacy``  | optional*   | **present**    | present  |
    | ``confidence``| required    | required       | required |

    (*) ``provisional`` places NO positive requirement on ``adequacy``: it may
    be absent (the common case) OR present (the recommend-drop channel holds an
    LO at ``provisional`` with ``adequacy.verdict="gap"`` +
    ``recommendation="drop"`` per ratification 3). The advisory rule (3.1) means
    only adequacy PRESENCE is asserted at refined+; its verdict VALUE is never
    part of any LO invariant.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    objective_id: str = Field(
        ...,
        frozen=True,
        description=(
            "Canonical open-id; immutable once minted at G0. Reuses the "
            "single-source open-id regex (no fork)."
        ),
    )
    statement: str = Field(
        ...,
        description="Free text, verbatim: the objective statement.",
    )
    status: LOStatus = Field(
        ...,
        description="Lifecycle status; transitions are gated by advance_lo only.",
    )
    confidence: Confidence = Field(
        ...,
        description="Advisory confidence band; gates nothing.",
    )
    bloom_level: BloomLevel | None = Field(
        default=None,
        description="Revised-Bloom level; populated at refine, required at ratified.",
    )
    source_refs: tuple[SourceRef, ...] = Field(
        default_factory=tuple,
        description="Provenance locators; >=1 required at refined+.",
    )
    adequacy: SourceAdequacy | None = Field(
        default=None,
        description="Advisory source-adequacy alert; present (any verdict) at refined+.",
    )
    origin: Literal["g0", "irene-proposed"] = Field(
        default="g0",
        description="Provenance marker: g0-minted or an Irene-proposed new LO.",
    )
    recommendation: Literal["keep", "drop"] = Field(
        default="keep",
        description="Advice only: Irene may recommend a drop; she never deletes.",
    )

    @field_validator("objective_id")
    @classmethod
    def _validate_objective_id(cls, value: str) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("objective_id must be a non-empty open-id string")
        # fullmatch (not match): `^...$` under re.match accepts a trailing
        # newline ("obj-1\n") because `$` matches before a terminal \n -- and
        # this id becomes the learning_objective_map DB key. fullmatch anchors
        # the WHOLE string (T11 key-integrity finding).
        if not _OPEN_ID_REGEX.fullmatch(value):
            raise ValueError(
                f"objective_id {value!r} fails open-id regex {OPEN_ID_REGEX_PATTERN}"
            )
        return value

    @model_validator(mode="after")
    def _enforce_status_invariants(self) -> LearningObjective:
        """Status-conditional invariant table (ratification 1).

        Only LOWER BOUNDS are enforced; ``provisional`` carries no positive
        requirement (so the recommend-drop channel's provisional+adequacy LO is
        valid). Adequacy is asserted by PRESENCE only -- the verdict value is
        never inspected here (advisory, ratification 3.1).
        """
        if self.status in ("refined", "ratified"):
            if len(self.source_refs) < 1:
                raise ValueError(
                    f"a {self.status!r} learning objective requires >=1 source_ref"
                )
            if self.adequacy is None:
                raise ValueError(
                    f"a {self.status!r} learning objective requires a populated "
                    "adequacy (presence only; the verdict value is advisory and "
                    "never gates)"
                )
        if self.status == "ratified" and self.bloom_level is None:
            raise ValueError("a 'ratified' learning objective requires a bloom_level")
        return self


# ---------------------------------------------------------------------------
# Transition guard (authority lives HERE, not on the model)
# ---------------------------------------------------------------------------

_TransitionActor = Literal["g0", "irene", "operator"]

# Canonical producing actor for each status (used for idempotent-replay checks):
# provisional is minted by g0, refined by irene, ratified by operator.
_PRODUCING_ACTOR: Final[dict[str, str]] = {
    "provisional": "g0",
    "refined": "irene",
    "ratified": "operator",
}

# Closed forward-edge allow-map keyed by (from_status, to_status, actor).
# The mint -> provisional edge (g0) is construction, surfaced via advance_lo as
# the idempotent (provisional, provisional, g0) replay (see below).
_ALLOWED_EDGES: Final[frozenset[tuple[str, str, str]]] = frozenset(
    {
        ("provisional", "refined", "irene"),
        ("refined", "ratified", "operator"),
    }
)


def advance_lo(
    lo: LearningObjective,
    target: LOStatus,
    *,
    actor: _TransitionActor,
) -> LearningObjective:
    """Advance ``lo`` to ``target`` under ``actor``, or raise ``IllegalTransition``.

    Deterministic + total; no LLM. ``content_entity_manager`` calls this
    exclusively -- nobody hand-mutates ``.status``.

    Closed allow-map (everything else raises ``IllegalTransition``):
        - (mint) -> provisional  : ``g0``   (surfaced as the idempotent replay)
        - provisional -> refined : ``irene``
        - refined -> ratified    : ``operator``

    ``irene`` may never produce ``ratified``: this GUARD rejects every
    ``*->ratified`` edge whose actor is not ``operator`` (and every same-status
    replay whose actor is not the canonical producer). The model itself
    validates VALUES not actor-authority -- direct construction at any status is
    possible (needed for DB deserialization); authority is enforced HERE, which
    is why ``content_entity_manager`` must route every transition through this
    function and never through ``model_copy``/hand-assignment.

    Idempotent replay: advancing an LO to the status it already holds is a
    no-op (returns the same object) ONLY when ``actor`` is that status's
    canonical producing actor (g0/provisional, irene/refined, operator/ratified);
    any other same-status call raises (never a silent re-run under a wrong actor).

    A legal forward edge still re-runs the full model validation, so advancing a
    ``provisional`` LO that lacks the refined+ substrate (source_refs / adequacy)
    raises ``pydantic.ValidationError`` -- the edge is legal but the data is not
    ready. That is distinct from ``IllegalTransition`` (an illegal edge).
    """
    from_status = lo.status

    # Idempotent replay: same status, canonical actor -> no-op.
    if target == from_status:
        if _PRODUCING_ACTOR.get(target) == actor:
            return lo
        raise IllegalTransition(
            f"idempotent replay of {target!r} requires actor "
            f"{_PRODUCING_ACTOR.get(target)!r}, got {actor!r}"
        )

    if (from_status, target, actor) not in _ALLOWED_EDGES:
        raise IllegalTransition(
            f"transition {from_status!r} -> {target!r} by actor {actor!r} is not "
            "an allowed edge"
        )

    # Re-validate the whole entity at the new status (invariant table re-checks).
    return LearningObjective.model_validate({**lo.model_dump(), "status": target})


# ---------------------------------------------------------------------------
# JSON Schema emission
# ---------------------------------------------------------------------------


def learning_objective_json_schema() -> dict:
    """Return the canonical JSON Schema for the LearningObjective family.

    The committed witness lives at
    ``app/marcus/lesson_plan/schema/learning_objective.v1.schema.json``; a test
    asserts the witness equals this live output (regen discipline).
    """
    return LearningObjective.model_json_schema()


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------

__all__ = [
    "SCHEMA_VERSION",
    "AdequacyFollowup",
    "AdequacyVerdict",
    "BloomLevel",
    "Confidence",
    "IllegalTransition",
    "LOStatus",
    "LearningObjective",
    "SourceAdequacy",
    "SourceRef",
    "advance_lo",
    "learning_objective_json_schema",
]
