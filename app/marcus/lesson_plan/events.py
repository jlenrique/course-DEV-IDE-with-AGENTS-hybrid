"""Event primitives for the Lesson Plan log (Story 31-1 AC-B.5 / AC-B.5a).

31-1 ships SHAPE only. The append-only log write-path + single-writer rule +
mandatory log event emission all live in 31-2 (R1 ruling amendment 13).

The generic :class:`EventEnvelope` (R2 rider W-1 / AC-B.5a) is the common
shape every event in the 31-2 log conforms to. The
:class:`ScopeDecisionTransition` is the first concrete payload pinned in
31-1; subsequent log events (``pre_packet_snapshot``, ``plan_unit.created``,
``scope_decision.set``, ``plan.locked``, ``fanout.envelope.emitted``) land
in 31-2 but inherit the envelope.

``ScopeDecisionTransition`` exposes a two-level actor surface (R2 rider
S-4):

    - ``actor`` (PUBLIC): ``Literal["system", "operator"]`` — this is what
      serializes to Maya-facing payloads.
    - ``_internal_actor`` (PRIVATE): the five-valued internal Marcus-duality
      taxonomy — ``Field(exclude=True)`` so default ``model_dump`` never
      leaks. The taxonomy values are defined in the model field declaration
      below.

:func:`to_internal_actor` maps the public actor plus an
``actor_hint`` to the internal taxonomy:

    - ``("system", None)`` -> ``"marcus"`` (generic system-side action)
    - ``("system", "irene")`` -> ``"irene"``
    - ``("operator", _)`` -> ``"maya"``
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.json_schema import SkipJsonSchema

from app.marcus.lesson_plan.event_type_registry import (
    OPEN_ID_REGEX_PATTERN as _OPEN_ID_REGEX,
)

# ---------------------------------------------------------------------------
# Generic envelope (R2 W-1 / AC-B.5a)
# ---------------------------------------------------------------------------


class EventEnvelope(BaseModel):
    """Generic envelope every event in the 31-2 append-only log conforms to.

    31-1 pins the shape; 31-2 emits.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        arbitrary_types_allowed=False,
    )

    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="UUID4 identifying this event uniquely in the log.",
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of event emission (timezone-aware required).",
    )
    plan_revision: int = Field(
        ...,
        ge=0,
        description="Lesson plan revision at emission time.",
    )
    event_type: str = Field(
        ...,
        pattern=_OPEN_ID_REGEX,
        min_length=1,
        description=(
            "Open-string event type; validated against the known-or-reserved "
            "registry via event_type_registry.validate_event_type."
        ),
    )
    payload: dict = Field(
        default_factory=dict,
        description="Event-type-specific body. For scope_decision_transition, "
        "the body matches ScopeDecisionTransition.model_dump().",
    )

    @field_validator("event_id", mode="after")
    @classmethod
    def _event_id_is_uuid4(cls, value: str) -> str:
        """SF-5: reject any ``event_id`` string that is not a UUID4.

        Accepts the hex-string form; UUID versions other than 4 are rejected.
        """
        try:
            parsed = UUID(value)
        except (ValueError, AttributeError, TypeError) as exc:
            raise ValueError(
                f"event_id {value!r} is not a valid UUID string"
            ) from exc
        if parsed.version != 4:
            raise ValueError(
                f"event_id {value!r} is UUID v{parsed.version}, expected v4"
            )
        return value

    @field_validator("timestamp", mode="after")
    @classmethod
    def _timestamp_must_be_aware(cls, value: datetime) -> datetime:
        """MF-4: reject naive datetime. Any timezone-aware datetime accepted.

        Design choice: accept any timezone-aware datetime (not just UTC) because
        Pydantic serializes to ISO 8601 with offset — deterministic across
        timezones. Naive datetimes are rejected because canonical-JSON digest
        (see :mod:`marcus.lesson_plan.digest`) requires deterministic timezone
        semantics on the wire.
        """
        if value.tzinfo is None:
            raise ValueError(
                "datetime field must be timezone-aware (UTC); "
                "got naive datetime"
            )
        return value


# ---------------------------------------------------------------------------
# ScopeDecisionTransition (AC-B.5)
# ---------------------------------------------------------------------------


class ScopeDecisionTransition(BaseModel):
    """Temporal-audit event primitive (Quinn).

    Emitted by the Marcus-side log writer in 31-2. 31-1 pins the shape only.
    Two-level actor surface (R2 rider S-4): public ``actor`` serializes to
    Maya-facing payloads; ``_internal_actor`` is ``Field(exclude=True)`` and
    reserved for audit surfaces.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        arbitrary_types_allowed=False,
    )

    event_type: Literal["scope_decision_transition"] = "scope_decision_transition"
    unit_id: str = Field(..., pattern=_OPEN_ID_REGEX, min_length=1)
    plan_revision: int = Field(..., ge=0, description="Plan revision at transition.")
    from_state: Literal["proposed", "ratified"]
    to_state: Literal["proposed", "ratified", "locked"]
    from_scope: (
        Literal["in-scope", "out-of-scope", "delegated", "blueprint"] | None
    ) = None
    to_scope: Literal["in-scope", "out-of-scope", "delegated", "blueprint"]
    actor: Literal["system", "operator"] = Field(
        ...,
        description=(
            "Public actor surface: 'system' when the platform emitted the "
            "transition, 'operator' when the course author did."
        ),
    )
    internal_actor: SkipJsonSchema[
        Literal[
            "marcus",
            "marcus-intake",
            "marcus-orchestrator",
            "irene",
            "maya",
        ]
    ] = Field(
        default="marcus",
        alias="_internal_actor",
        serialization_alias="_internal_actor",
        exclude=True,
        description=(
            "Internal audit field. Never present in default serialization "
            "nor in the published JSON Schema. Audit tooling opts in. "
            "Defaults to 'marcus' for round-trip safety; audit callers must "
            "provide the precise value via the to_audit_dump() surface. "
            "Dropping Field(exclude=True) leaks Marcus-duality internals to "
            "Maya-facing payloads — R2 rider S-4 anti-leak discipline. "
            "AC-T.15 guards against this in CI."
        ),
    )
    timestamp: datetime
    rationale_snapshot: str = Field(
        default="",
        description=(
            "Verbatim rationale at transition time; may differ from the current "
            "PlanUnit.rationale. R1 ruling amendment 16 surface."
        ),
    )

    @field_validator("timestamp", mode="after")
    @classmethod
    def _timestamp_must_be_aware(cls, value: datetime) -> datetime:
        """MF-4: reject naive datetime; any timezone-aware datetime accepted."""
        if value.tzinfo is None:
            raise ValueError(
                "datetime field must be timezone-aware (UTC); "
                "got naive datetime"
            )
        return value

    def to_audit_dump(self) -> dict:
        """Audit-surface serialization that INCLUDES ``_internal_actor`` (R2 S-4).

        Default ``model_dump`` / ``model_dump_json`` keep the Maya-facing
        surface clean by ``Field(exclude=True)`` on ``internal_actor``. This
        helper is the explicit opt-in for private-audit tooling. Reads
        internal fields at call time; ``validate_assignment=True`` on the
        containing model ensures mutations cannot produce invalid values.
        """
        payload = self.model_dump()
        payload["_internal_actor"] = self.internal_actor
        return payload


# ---------------------------------------------------------------------------
# to_internal_actor helper (R2 S-4)
# ---------------------------------------------------------------------------


def to_internal_actor(
    actor: Literal["system", "operator"],
    actor_hint: (
        Literal["marcus", "marcus-intake", "marcus-orchestrator", "irene"] | None
    ) = None,
) -> Literal[
    "marcus",
    "marcus-intake",
    "marcus-orchestrator",
    "irene",
    "maya",
]:
    """Map the public actor surface to the internal audit taxonomy (R2 S-4).

    - ``operator`` always maps to ``"maya"`` (sole operator actor).
    - ``system`` with no hint maps to generic ``"marcus"``.
    - ``system`` with hint maps to the hint value verbatim, permitting
      internal modules to express granular audit provenance.
    """
    if actor == "operator":
        return "maya"
    if actor == "system":
        if actor_hint is None:
            return "marcus"
        return actor_hint
    raise ValueError(f"Unknown actor {actor!r}")  # pragma: no cover - Literal guards this


__all__ = [
    "EventEnvelope",
    "ScopeDecisionTransition",
    "to_internal_actor",
]
