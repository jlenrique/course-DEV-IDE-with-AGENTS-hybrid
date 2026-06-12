"""Lesson Plan schema primitives (Story 31-1 AC-B.1 / .2 / .3 / .4 / .6 / .7 / .9).

All shapes in this module are the reviewable contract downstream stories read and
write against. Pydantic v2. Canonical-JSON serialization invariants live in
:mod:`app.marcus.lesson_plan.digest`; event primitives live in
:mod:`app.marcus.lesson_plan.events`; event-type registry lives in
:mod:`app.marcus.lesson_plan.event_type_registry`.

Discipline notes:
    - ``PlanUnit.rationale`` is free text, stored verbatim, surfaced verbatim
      (R1 ruling amendment 16). No normalization, no trim, no enum collapse.
    - ``ScopeDecision`` exposes a two-level actor surface (R2 rider S-4):
      public ``proposed_by`` on ``Literal["system", "operator"]`` versus private
      ``_internal_proposed_by`` on the five-valued internal taxonomy. Private
      field uses ``Field(exclude=True)`` so default ``model_dump`` stays clean.
    - ``ScopeDecision`` carries a Q-5 ``model_validator(mode="after")`` bypass
      guard rejecting any ``state == "locked"`` with ``ratified_by != "maya"``.
    - ``weather_band`` uses abundance framing (R2 rider S-1): no "insufficient",
      no "failed". Field docstrings mirror the operator-facing wording.
    - No user-facing string in this module may contain the Marcus-duality
      tokens forbidden by R1 ruling amendment 17 / R2 rider S-3. Internal
      module and field names (including the Literal taxonomy on the private
      audit surface) are exempt.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.json_schema import SkipJsonSchema

from app.marcus.lesson_plan.event_type_registry import (
    OPEN_ID_REGEX_PATTERN as _OPEN_ID_REGEX,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION: str = "1.0"
"""Root schema version string emitted on every ``LessonPlan`` (AC-C.2)."""


class StaleRevisionError(ValueError):
    """Raised when a plan mutation presents a stale revision number (AC-T.10)."""


# ---------------------------------------------------------------------------
# LearningModel + PlanRef (support shapes)
# ---------------------------------------------------------------------------


class LearningModel(BaseModel):
    """Hardcoded ``gagne-9`` / version 1 at MVP (John MVP Discipline)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(..., description="Learning model identifier; MVP is 'gagne-9'.")
    version: int = Field(..., ge=1, description="Learning model version; MVP is 1.")


class PlanRef(BaseModel):
    """Lightweight plan reference carried on emitted artifacts (fit-report, events)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    lesson_plan_revision: int = Field(..., ge=0)
    lesson_plan_digest: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Dials + IdentifiedGap
# ---------------------------------------------------------------------------


class Dials(BaseModel):
    """Operator-set dials for enrichment + corroboration (AC-B.3).

    Both dials accept ``None`` (dial unset) or a float in ``[0.0, 1.0]``.
    Interaction rules + operator-facing wording documented in ``dials-spec.md``.
    """

    model_config = ConfigDict(extra="forbid")

    enrichment: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description=(
            "Aspirational enrichment dial: operator-requested depth beyond what the "
            "source materials alone could carry. Null = unset."
        ),
    )
    corroboration: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description=(
            "Evidence-bolster dial: operator-requested cross-validation of existing "
            "source claims. Null = unset."
        ),
    )


class IdentifiedGap(BaseModel):
    """Single gap surfaced by Irene on an in-scope unit (AC-B.3)."""

    model_config = ConfigDict(extra="forbid")

    gap_id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    suggested_posture: Literal["embellish", "corroborate", "gap_fill"] = Field(
        ...,
        description=(
            "Recommended research posture for this gap, aligned to the three operator-"
            "memory parameter families: embellish (aspirational enrichment), corroborate "
            "(evidence-bolster), gap_fill (derivative-artifact gap-filling)."
        ),
    )


# ---------------------------------------------------------------------------
# ScopeDecision (value-object + state machine + two-level actor surface + Q-5 guard)
# ---------------------------------------------------------------------------


class ScopeDecision(BaseModel):
    """Jurisdictional primitive. Maya is the SOLE signatory (AC-C.5 / AC-C.8).

    Two-level actor surface (R2 rider S-4):
        - ``proposed_by``: PUBLIC; Literal["system", "operator"]; serializes to
          Maya-facing payloads.
        - ``_internal_proposed_by``: PRIVATE; Literal over the five-valued
          internal taxonomy; ``Field(exclude=True)`` so it DOES NOT appear in
          default ``model_dump`` / ``model_dump_json``. Private-audit tooling
          can opt in by overriding ``exclude``.

    State machine:
        - ``proposed -> ratified`` requires ``ratified_by == "maya"``.
        - ``ratified -> locked`` requires the plan-lock trigger (30-3a).
        - ``proposed -> proposed`` permitted (re-propose with different scope).
        - ``locked -> *`` forbidden (terminal).
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
    )

    state: Literal["proposed", "ratified", "locked"] = Field(
        ...,
        description="Lifecycle state of this scope decision.",
    )
    scope: Literal["in-scope", "out-of-scope", "delegated", "blueprint"] = Field(
        ...,
        description="Jurisdictional verdict for this plan unit.",
    )
    proposed_by: Literal["system", "operator"] = Field(
        ...,
        description=(
            "Public actor surface: 'system' when generated by the platform, "
            "'operator' when supplied by the course author."
        ),
    )
    internal_proposed_by: SkipJsonSchema[
        Literal[
            "marcus",
            "marcus-intake",
            "marcus-orchestrator",
            "irene",
            "maya",
        ]
    ] = Field(
        default="marcus",
        alias="_internal_proposed_by",
        serialization_alias="_internal_proposed_by",
        exclude=True,
        description=(
            "Internal audit field. Never present in default serialization output "
            "nor in the published JSON Schema. Downstream audit tooling opts in. "
            "Defaults to the generic 'marcus' value so that round-tripping a "
            "Maya-facing payload (which excludes the field) back through "
            "model_validate_json is successful; private-audit tooling that needs "
            "the exact internal actor provenance must carry it via to_audit_dump(). "
            "Dropping Field(exclude=True) leaks Marcus-duality internals to "
            "Maya-facing payloads — R2 rider S-4 anti-leak discipline. "
            "AC-T.15 guards against this in CI."
        ),
    )
    ratified_by: Literal["maya"] | None = Field(
        None,
        description="Signatory; Literal['maya'] or None. Maya is the sole signatory.",
    )
    locked_at: datetime | None = Field(
        None,
        description="Timestamp at which this decision entered the terminal locked state.",
    )

    @field_validator("locked_at", mode="after")
    @classmethod
    def _locked_at_must_be_aware(cls, value: datetime | None) -> datetime | None:
        """MF-4: reject naive datetime; any timezone-aware datetime accepted."""
        if value is not None and value.tzinfo is None:
            raise ValueError(
                "datetime field must be timezone-aware (UTC); "
                "got naive datetime"
            )
        return value

    @model_validator(mode="after")
    def _guard_locked_without_maya(self) -> ScopeDecision:
        """Q-5 bypass guard (AC-C.8): locked state requires ``ratified_by == 'maya'``.

        Also enforces the construction-time invariants closed by 31-1 follow-on
        consensus (party-mode 2026-04-19, Edge#5 + Edge#6):
            - ``state == 'proposed'`` MUST NOT carry a non-null ``ratified_by``.
            - ``state != 'locked'`` MUST NOT carry a non-null ``locked_at``.

        Without these invariants, direct Pydantic construction (e.g. JSON
        deserialization, factory fixtures) could materialize state objects
        that bypass the ``transition_to`` state-machine and leak through the
        31-2 log writer into the 30-3a plan-lock fanout.
        """
        if self.state == "locked" and self.ratified_by != "maya":
            raise ValueError(
                "ScopeDecision locked state requires ratified_by='maya' "
                "(tri-phasic contract: Maya is sole signatory; see R1 ruling amendment 5)"
            )
        if self.state == "proposed" and self.ratified_by is not None:
            raise ValueError(
                "ScopeDecision state='proposed' must not carry ratified_by "
                "(tri-phasic contract: ratification belongs to the ratified state)"
            )
        if self.state != "locked" and self.locked_at is not None:
            raise ValueError(
                f"ScopeDecision state={self.state!r} must not carry locked_at "
                "(locked_at is set only when state == 'locked')"
            )
        return self

    def to_audit_dump(self) -> dict:
        """Audit-surface serialization that INCLUDES the internal actor field.

        Default ``model_dump`` / ``model_dump_json`` keep the Maya-facing surface
        clean by ``Field(exclude=True)`` on ``internal_proposed_by`` — this
        helper is the explicit opt-in for private-audit tooling (30-1 golden
        trace, 30-4 fanout, bmad-code-review) that needs the granular actor
        provenance. Reads internal fields at call time; ``validate_assignment=True``
        on the containing model ensures mutations cannot produce invalid values.
        """
        payload = self.model_dump()
        payload["_internal_proposed_by"] = self.internal_proposed_by
        return payload

    @classmethod
    def transition_to(
        cls,
        current: ScopeDecision,
        *,
        state: Literal["proposed", "ratified", "locked"],
        scope: Literal["in-scope", "out-of-scope", "delegated", "blueprint"] | None = None,
        proposed_by: Literal["system", "operator"] | None = None,
        internal_proposed_by: (
            Literal[
                "marcus",
                "marcus-intake",
                "marcus-orchestrator",
                "irene",
                "maya",
            ]
            | None
        ) = None,
        ratified_by: Literal["maya"] | None = None,
        locked_at: datetime | None = None,
    ) -> ScopeDecision:
        """Emit a new ``ScopeDecision`` reflecting a legal transition from ``current``.

        External code constructs new ``ScopeDecision`` values via this classmethod —
        direct mutation is re-validated and will fail on bypass attempts (the
        Q-5 guard is re-run on assignment thanks to ``validate_assignment=True``).
        """
        # Terminal check first.
        if current.state == "locked":
            raise ValueError(
                f"ScopeDecision locked -> {state} forbidden (locked is terminal)"
            )

        # Disallow revert ratified -> proposed.
        if current.state == "ratified" and state == "proposed":
            raise ValueError("ScopeDecision ratified -> proposed forbidden (no revert)")

        # Disallow direct proposed -> locked (must go through ratified).
        if current.state == "proposed" and state == "locked":
            raise ValueError(
                "ScopeDecision proposed -> locked forbidden "
                "(must traverse ratified first)"
            )

        # Proposed -> ratified requires Maya signatory.
        if (
            current.state == "proposed"
            and state == "ratified"
            and ratified_by != "maya"
        ):
            raise ValueError(
                "ScopeDecision proposed -> ratified requires ratified_by='maya' "
                "(Maya is the sole signatory)"
            )

        return cls(
            state=state,
            scope=scope if scope is not None else current.scope,
            proposed_by=proposed_by if proposed_by is not None else current.proposed_by,
            _internal_proposed_by=(
                internal_proposed_by
                if internal_proposed_by is not None
                else current.internal_proposed_by
            ),
            ratified_by=(
                ratified_by if ratified_by is not None else current.ratified_by
            ),
            locked_at=(
                locked_at
                if locked_at is not None
                else (
                    current.locked_at
                    if state != "locked"
                    else datetime.now(tz=UTC)
                )
            ),
        )


# ---------------------------------------------------------------------------
# BlueprintSignoff
# ---------------------------------------------------------------------------


class BlueprintSignoff(BaseModel):
    """Typed pointer for 29-3's Irene + writer blueprint sign-off seam.

    This is intentionally additive and minimal: one pointer to the original
    blueprint draft, one pointer to the sign-off sidecar artifact, two explicit
    approval booleans, and one timezone-aware timestamp for when the sign-off
    record was captured.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    blueprint_asset_path: str = Field(
        ...,
        min_length=1,
        description=(
            "Repo-relative path to the 31-4 blueprint draft artifact that this "
            "sign-off record approves."
        ),
    )
    signoff_artifact_path: str = Field(
        ...,
        min_length=1,
        description=(
            "Repo-relative path to the deterministic Irene+writer sign-off "
            "sidecar artifact emitted by Story 29-3."
        ),
    )
    irene_review_complete: bool = Field(
        ...,
        description="True once Irene's blueprint review has been recorded.",
    )
    writer_signoff_complete: bool = Field(
        ...,
        description="True once the human writer has approved the blueprint draft.",
    )
    signed_at: datetime = Field(
        ...,
        description="Timezone-aware timestamp at which the sign-off pointer was emitted.",
    )

    @field_validator("blueprint_asset_path", "signoff_artifact_path")
    @classmethod
    def _validate_repo_relative_path(cls, value: str) -> str:
        path = PurePosixPath(value)
        if path.is_absolute():
            raise ValueError("blueprint signoff paths must be repo-relative")
        if ".." in path.parts:
            raise ValueError("blueprint signoff paths must not traverse upward")
        return value

    @field_validator("signed_at", mode="after")
    @classmethod
    def _signed_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError(
                "datetime field must be timezone-aware (UTC); "
                "got naive datetime"
            )
        return value


# ---------------------------------------------------------------------------
# PlanUnit
# ---------------------------------------------------------------------------


class PlanUnit(BaseModel):
    """Single plan unit inside the lesson plan (AC-B.2).

    ``rationale`` is stored verbatim — no parsing, no coercion, no trim
    (R1 ruling amendment 16). Empty string is valid (R2 rider S-2).
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        arbitrary_types_allowed=False,
    )

    unit_id: str = Field(..., pattern=_OPEN_ID_REGEX, min_length=1)
    event_type: str = Field(..., pattern=_OPEN_ID_REGEX, min_length=1)
    source_fitness_diagnosis: str = Field(..., min_length=1)
    scope_decision: ScopeDecision | None = Field(
        None,
        description=(
            "Jurisdictional verdict carried by this plan unit. None is permitted "
            "during plan drafting before Maya has weighed in on this unit."
        ),
    )
    weather_band: Literal["gold", "green", "amber", "gray"] = Field(
        ...,
        description=(
            "Abundance-framed source-fitness band. "
            "gold = you've got this cold; "
            "green = we're in step; "
            "amber = your call; "
            "gray = Marcus leans in more (proposes additional support, "
            "delegation or blueprint, for this unit). "
            "Red is forbidden (AC-B.7)."
        ),
    )
    modality_ref: str | None = Field(
        None,
        description=(
            "Target modality (e.g. 'slides', 'leader-guide', 'blueprint'). "
            "Null unless the scope decision is 'delegated' or 'blueprint'."
        ),
    )
    rationale: str = Field(
        default="",
        description=(
            "Free text, stored verbatim, surfaced verbatim (R1 ruling amendment 16). "
            "Accepts any content including the empty string; no min_length; "
            "no trimming. R2 rider S-2."
        ),
    )
    blueprint_signoff: BlueprintSignoff | None = Field(
        None,
        description=(
            "Optional typed pointer emitted by Story 29-3 when a blueprint draft "
            "has been co-authored and signed off by Irene plus the human writer."
        ),
    )
    gaps: list[IdentifiedGap] = Field(default_factory=list)
    dials: Dials | None = Field(None)

    @field_validator("weather_band", mode="before")
    @classmethod
    def _reject_red(cls, value: object) -> object:
        """Triple-layer no-red rejection (AC-B.7): direct, JSON deser, and schema path."""
        if isinstance(value, str) and value.lower() == "red":
            raise ValueError(
                "weather_band 'red' is forbidden; the course author did not fail "
                "(see lesson-planner-mvp-plan.md Sally's UX Primitives)"
            )
        return value

    @model_validator(mode="after")
    def _validate_scope_state_consistency(self) -> PlanUnit:
        """AC-T.12: gaps only valid when scope == in-scope; dials only valid on in|delegated."""
        sd = self.scope_decision
        if sd is not None:
            if self.gaps and sd.scope != "in-scope":
                raise ValueError(
                    f"gaps only valid on in-scope units; unit has scope={sd.scope!r}"
                )
            if self.dials is not None and sd.scope not in {"in-scope", "delegated"}:
                raise ValueError(
                    "dials only valid on in|delegated units; "
                    f"unit has scope={sd.scope!r}"
                )
        return self


# ---------------------------------------------------------------------------
# LessonPlan root
# ---------------------------------------------------------------------------


class LessonPlan(BaseModel):
    """Root lesson plan artifact (AC-B.1)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default=SCHEMA_VERSION, pattern=r"^\d+\.\d+$")
    learning_model: LearningModel
    structure: dict = Field(default_factory=dict)
    plan_units: list[PlanUnit] = Field(default_factory=list)
    revision: int = Field(..., ge=0, description="Monotonic revision counter.")
    updated_at: datetime
    digest: str = Field(default="", description="sha256 of canonical JSON serialization.")

    @field_validator("updated_at", mode="after")
    @classmethod
    def _updated_at_must_be_aware(cls, value: datetime) -> datetime:
        """MF-4: reject naive datetime; any timezone-aware datetime accepted."""
        if value.tzinfo is None:
            raise ValueError(
                "datetime field must be timezone-aware (UTC); "
                "got naive datetime"
            )
        return value

    def bump_revision(self) -> LessonPlan:
        """Return a new ``LessonPlan`` with ``revision`` incremented by 1 and digest recomputed.

        Does not guard against concurrent writers — use
        :meth:`apply_revision` when enforcing monotonicity against an external
        plan. This helper is for local in-process bumps where the caller holds
        the latest plan.
        """
        from app.marcus.lesson_plan.digest import compute_digest

        bumped = self.model_copy(update={"revision": self.revision + 1})
        return bumped.model_copy(update={"digest": compute_digest(bumped)})

    def apply_revision(self, new_plan: LessonPlan) -> LessonPlan:
        """Apply a new plan version. Raises :class:`StaleRevisionError` on stale input.

        Contract: callers must increment revision by at least 1 before
        submitting. Raises :class:`StaleRevisionError` when
        ``new_plan.revision <= self.revision``. Digest is recomputed on the
        returned plan so writers can submit un-digested drafts without
        duplicating digest logic at every call-site (AC-T.10).
        """
        from app.marcus.lesson_plan.digest import compute_digest

        if new_plan.revision <= self.revision:
            raise StaleRevisionError(
                f"New plan revision {new_plan.revision} is not greater than "
                f"current {self.revision}"
            )
        return new_plan.model_copy(update={"digest": compute_digest(new_plan)})


# ---------------------------------------------------------------------------
# FitReport + FitDiagnosis (AC-B.9)
# ---------------------------------------------------------------------------


class FitDiagnosis(BaseModel):
    """Single diagnostic verdict produced by the attestor (AC-B.9)."""

    model_config = ConfigDict(extra="forbid")

    unit_id: str = Field(..., min_length=1)
    fitness: Literal["sufficient", "partial", "absent"]
    commentary: str = Field(..., min_length=1)
    recommended_scope_decision: (
        Literal["in-scope", "out-of-scope", "delegated", "blueprint"] | None
    ) = None
    recommended_weather_band: Literal["gold", "green", "amber", "gray"] | None = None

    @field_validator("recommended_weather_band", mode="before")
    @classmethod
    def _reject_red_recommended(cls, value: object) -> object:
        if isinstance(value, str) and value.lower() == "red":
            raise ValueError(
                "recommended_weather_band 'red' is forbidden; no deficit framing"
            )
        return value


class FitReport(BaseModel):
    """Fit-report-v1 artifact class (AC-B.9)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default="1.0", pattern=r"^\d+\.\d+$")
    source_ref: str = Field(..., min_length=1)
    plan_ref: PlanRef
    diagnoses: list[FitDiagnosis] = Field(default_factory=list)
    generated_at: datetime
    irene_budget_ms: int = Field(..., ge=0, description="Observed diagnostic latency.")

    @field_validator("generated_at", mode="after")
    @classmethod
    def _generated_at_must_be_aware(cls, value: datetime) -> datetime:
        """MF-4: reject naive datetime; any timezone-aware datetime accepted."""
        if value.tzinfo is None:
            raise ValueError(
                "datetime field must be timezone-aware (UTC); "
                "got naive datetime"
            )
        return value


# ---------------------------------------------------------------------------
# Re-export helpers
# ---------------------------------------------------------------------------

__all__ = [
    "BlueprintSignoff",
    "Dials",
    "FitDiagnosis",
    "FitReport",
    "IdentifiedGap",
    "LearningModel",
    "LessonPlan",
    "PlanRef",
    "PlanUnit",
    "SCHEMA_VERSION",
    "ScopeDecision",
    "StaleRevisionError",
]
