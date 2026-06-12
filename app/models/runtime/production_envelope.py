"""Strict cross-specialist accumulator for production composition."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def compute_output_digest(output: dict[str, Any]) -> str:
    """Return a stable SHA-256 digest for a specialist output payload."""
    canonical = json.dumps(
        output,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _enforce_tz_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return value


def _enforce_uuid4(value: UUID) -> UUID:
    if value.version != 4:
        raise ValueError("trial_id must be a UUID4")
    return value


class SpecialistContribution(BaseModel):
    """One immutable specialist output appended to a production envelope.

    S2 (SCP 2026-06-11 segment-data-plane, per-node keying): ``node_id``
    identifies the manifest node that produced this contribution — the unit
    of contribution is the node, not the specialist (Winston A-ruling).
    ``None`` only on legacy v1 envelopes deserialized from disk. ``attempt``
    records same-node retry provenance (Murat regression shape: retry
    overwrites, never duplicate-appends).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True, frozen=True)

    specialist_id: str = Field(..., min_length=1)
    contributed_at: datetime
    output: dict[str, Any]
    cost_usd: float = Field(..., ge=0.0)
    model_used: str = Field(..., min_length=1)
    output_digest: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    node_id: str | None = None
    attempt: int = Field(default=1, ge=1)

    @classmethod
    def from_output(
        cls,
        *,
        specialist_id: str,
        output: dict[str, Any],
        model_used: str,
        cost_usd: float = 0.0,
        contributed_at: datetime | None = None,
        node_id: str | None = None,
    ) -> SpecialistContribution:
        return cls(
            specialist_id=specialist_id,
            contributed_at=contributed_at or datetime.now(UTC),
            output=output,
            cost_usd=cost_usd,
            model_used=model_used,
            output_digest=compute_output_digest(output),
            node_id=node_id,
        )

    @field_validator("contributed_at")
    @classmethod
    def _enforce_contributed_tz(cls, value: datetime) -> datetime:
        return _enforce_tz_aware(value)

    @model_validator(mode="after")
    def _enforce_output_digest(self) -> SpecialistContribution:
        expected = compute_output_digest(self.output)
        if self.output_digest != expected:
            raise ValueError("output_digest must equal sha256 of output")
        return self


class ProductionEnvelope(BaseModel):
    """Canonical cross-specialist accumulator for production composition.

    This is distinct from ``RunState.cache_state.cache_prefix``, which remains
    per-specialist scratch for isolated scaffold execution.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    # v2 = per-node contribution keying (S2, SCP 2026-06-11). v1 accepted on
    # read for frozen legacy run dirs; the resume path REJECTS v1 loudly
    # (relaunch-as-cycle-2 operator ruling) so it is never half-read.
    schema_version: Literal["production-envelope.v1", "production-envelope.v2"] = (
        "production-envelope.v2"
    )
    trial_id: UUID
    contributions: tuple[SpecialistContribution, ...] = Field(default_factory=tuple)

    @field_validator("trial_id")
    @classmethod
    def _enforce_trial_uuid4(cls, value: UUID) -> UUID:
        return _enforce_uuid4(value)

    def get_contribution(
        self, specialist_id: str, node_id: str | None = None
    ) -> SpecialistContribution | None:
        """Lookup a contribution by specialist id, optionally pinned to a node.

        ``node_id=None`` preserves legacy any-node first-match semantics for
        consumers that genuinely mean "did this specialist contribute at all".
        Walkers and the dispatch adapter pass the manifest node id explicitly.
        """
        for contribution in self.contributions:
            if contribution.specialist_id != specialist_id:
                continue
            if node_id is None or contribution.node_id == node_id:
                return contribution
        return None

    def latest_for_specialist(self, specialist_id: str) -> SpecialistContribution | None:
        """Most recent contribution for a specialist (dependency consumers)."""
        for contribution in reversed(self.contributions):
            if contribution.specialist_id == specialist_id:
                return contribution
        return None

    def add_contribution(self, contribution: SpecialistContribution) -> None:
        """Append one contribution per (specialist, node); same-node retry overwrites.

        Multi-node specialists accumulate one entry per manifest node (the
        Path-Z first-contribution-wins rule was specialist-keyed and silently
        skipped irene_pass1's two later jobs in Trial-3 attempt-4). A retry of
        the SAME node replaces the prior entry with ``attempt`` incremented —
        never a duplicate append, never a silent skip.
        """
        for index, existing in enumerate(self.contributions):
            if (
                existing.specialist_id == contribution.specialist_id
                and existing.node_id == contribution.node_id
            ):
                replacement = contribution.model_copy(
                    update={"attempt": existing.attempt + 1}
                )
                self.contributions = (
                    *self.contributions[:index],
                    replacement,
                    *self.contributions[index + 1 :],
                )
                return
        self.contributions = (*self.contributions, contribution)


__all__ = [
    "ProductionEnvelope",
    "SpecialistContribution",
    "compute_output_digest",
]
