"""Production context + produced asset payload shapes (Story 31-3 AC-B.4 / AC-B.5 / AC-B.7).

Audience: consumer agents reading fanout events (30-4, 32-2) + Quinn-R two-branch
gate (31-5). Also the twin input/output contract for :class:`ModalityProducer`.

Shapes:
    - :class:`ProductionContext` — minimal input to ``produce()``. W-2 extensibility
      seam (Winston R2): 31-4 MAY subclass for blueprint-specific fields without a
      schema version bump, preserving ``lesson_plan_revision`` + ``lesson_plan_digest``.
    - :class:`ProducedAsset` — output of ``produce()``. Carries ``fulfills:
      {plan_unit_id}@{plan_revision}`` per Quinn's Tri-Phasic Contract. AC-T.5b
      Q-R2-A cross-field validator rejects counterfeit where
      ``source_plan_unit_id != parse(fulfills).unit_id``.

Regex pin (AC-B.7):
    ``_FULFILLS_REGEX = re.compile(r"^[a-z0-9._-]+@(?:0|[1-9]\\d*)$")``
    - unit_id side reuses 31-1 :data:`_OPEN_ID_REGEX` family (lowercase + digits + ``._-``).
    - revision side rejects negative, leading-zero, non-integer, and float
      (per M-AM-3 R2: ``"unit@007"`` REJECT for strict-monotonic integer discipline).
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.marcus.lesson_plan.event_type_registry import OPEN_ID_REGEX_PATTERN
from app.marcus.lesson_plan.modality_registry import ModalityRef

SCHEMA_VERSION: Final[str] = "1.0"
"""Shared schema version for ProductionContext + ProducedAsset (AC-B.9)."""


# ---------------------------------------------------------------------------
# fulfills regex (AC-B.7)
# ---------------------------------------------------------------------------

# unit_id ::= [a-z0-9._-]+
# revision ::= 0 | [1-9][0-9]*   (rejects leading zeros per M-AM-3)
_FULFILLS_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^[a-z0-9._-]+@(?:0|[1-9]\d*)$"
)
"""Regex pinning the ``{plan_unit_id}@{plan_revision}`` format.

Accepts: ``"unit-foo@0"``, ``"gagne-event-3@5"``, ``"u@0"``.
Rejects: ``"unit@007"`` (leading zero), ``"unit@-1"`` (negative), ``"UPPER@1"``
(uppercase), ``"unit@abc"`` (non-integer), multi-``@``, whitespace, empty.
"""


# ---------------------------------------------------------------------------
# ProductionContext (AC-B.4)
# ---------------------------------------------------------------------------


class ProductionContext(BaseModel):
    """Minimal input to :meth:`ModalityProducer.produce`.

    W-2 (Winston R2) extensibility seam: 31-4 (blueprint-producer) MAY subclass
    :class:`ProductionContext` for blueprint-specific fields WITHOUT a schema
    version bump. Sub-classes MUST preserve ``lesson_plan_revision`` +
    ``lesson_plan_digest`` as the staleness-gate primitives. Pydantic BaseModel
    inheritance is the intended extensibility seam — not a new schema version.
    Downstream subclass stories document the extension in their own
    SCHEMA_CHANGELOG entry.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    lesson_plan_revision: int = Field(
        ...,
        ge=0,
        description="Revision of the source lesson plan; staleness-gate primitive.",
    )
    lesson_plan_digest: str = Field(
        ...,
        min_length=1,
        description=(
            "Digest of the source lesson plan at this revision; "
            "staleness-gate primitive."
        ),
    )


# ---------------------------------------------------------------------------
# ProducedAsset (AC-B.5 + AC-B.7 + Q-R2-A)
# ---------------------------------------------------------------------------


class ProducedAsset(BaseModel):
    """Output of :meth:`ModalityProducer.produce`.

    Pins the tri-phasic contract execution-phase artifact (Quinn): every
    produced asset carries ``fulfills: {plan_unit_id}@{plan_revision}``.

    Q-R2-A cross-field invariant: ``source_plan_unit_id ==
    parse(fulfills).unit_id`` — a counterfeit asset declaring mismatched
    ``source_plan_unit_id`` and ``fulfills`` is rejected.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    asset_ref: str = Field(
        ...,
        min_length=1,
        description="Stable identifier for the produced asset.",
    )
    modality_ref: ModalityRef = Field(
        ...,
        description="The atomic modality this asset serves; must match producer class attr.",
    )
    source_plan_unit_id: str = Field(
        ...,
        min_length=1,
        pattern=OPEN_ID_REGEX_PATTERN,
        description=(
            "The plan unit identifier this asset serves. Must conform to the "
            "open-id regex (lowercase + digits + ``._-``). Party-mode 2026-04-19 "
            "follow-on: pinned to single-source `OPEN_ID_REGEX_PATTERN` in "
            "event_type_registry so non-PlanUnit producers cannot construct "
            "asset rows with malformed identifiers (was 31-3 SHOULD-FIX#1 deferred)."
        ),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Creation timestamp; timezone-aware UTC enforced.",
    )
    asset_path: str = Field(
        ...,
        min_length=1,
        description="Filesystem path (repo-relative) where the producer wrote this asset.",
    )
    fulfills: str = Field(
        ...,
        description=(
            "Tri-phasic-contract pin in the format "
            "'{plan_unit_id}@{plan_revision}'. Regex-validated; revision must "
            "be a non-negative integer without leading zeros."
        ),
    )

    @field_validator("created_at")
    @classmethod
    def _enforce_tz_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError(
                "ProducedAsset.created_at must be timezone-aware (UTC); "
                "got naive datetime"
            )
        return value

    @field_validator("fulfills")
    @classmethod
    def _fulfills_regex(cls, value: str) -> str:
        # Type-strict: only str is acceptable. Pydantic v2 will typically coerce
        # before the validator runs, but we guard explicitly for int/None/list.
        if not isinstance(value, str):
            raise ValueError(
                f"ProducedAsset.fulfills must be a string; "
                f"got {type(value).__name__!r}"
            )
        if not _FULFILLS_REGEX.match(value):
            raise ValueError(
                f"ProducedAsset.fulfills {value!r} fails regex "
                r"^[a-z0-9._-]+@(?:0|[1-9]\d*)$ — expected "
                "'{plan_unit_id}@{plan_revision}' with lowercase unit_id and "
                "non-negative integer revision (no leading zeros)"
            )
        return value

    @model_validator(mode="after")
    def _fulfills_matches_source_plan_unit_id(self) -> ProducedAsset:
        """Q-R2-A: counterfeit-fulfillment seam check.

        ``source_plan_unit_id`` MUST equal the unit_id portion of ``fulfills``
        (i.e., ``fulfills.split("@", 1)[0]``). A mismatch is a tri-phasic
        contract violation.
        """
        fulfills_uid = self.fulfills.split("@", 1)[0]
        if self.source_plan_unit_id != fulfills_uid:
            raise ValueError(
                f"ProducedAsset: source_plan_unit_id ({self.source_plan_unit_id!r}) "
                f"does not match fulfills unit_id ({fulfills_uid!r}); "
                f"counterfeit-fulfillment seam; tri-phasic contract violation."
            )
        return self


__all__ = [
    "SCHEMA_VERSION",
    "ProducedAsset",
    "ProductionContext",
]
