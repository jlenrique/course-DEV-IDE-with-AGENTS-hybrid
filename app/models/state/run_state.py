"""`RunState` — top-level run state encoding the five reproducibility invariants.

Per NFR-X1–X5 the migration runtime must encode:
- **X1** byte-for-byte replay (round-trip serialization)
- **X2** frozen graph version (closed-enum-style validation)
- **X3** sanctum snapshot identity (`SanctumFingerprint`)
- **X4** model selection trail (`ModelResolutionEntry` list)
- **X5** documented temperature variance (constrained float)

Slab 4 Story 4.5 wires the full frozen-graph-version registry; 1.2 ships
a stub allow-list (`ALLOWED_GRAPH_VERSIONS`) that 4.5 will replace.

# RetryPolicy integration deferred to Slab 4 Story 4.7 per LangGraph state
# idiom #6 — do NOT silently work around it (e.g., arbitrary_types_allowed=True
# to make langgraph.RetryPolicy fit) here in 1.2.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version
from app.models.state.cache_state import CacheState
from app.models.state.component_selection import ComponentSelection
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.sanctum_fingerprint import SanctumFingerprint
from app.models.state.story_state import StoryState
from app.models.state.validators.run_state_validators import (
    enforce_complete_requires_completed_at as _enforce_run_complete_invariant,
)

RunStatus = Literal["pending", "running", "complete", "failed"]
"""Closed enum: top-level run status."""

ALLOWED_GRAPH_VERSIONS: frozenset[str] = frozenset({"v0.1-stub", "v42"})
"""Stub frozen-graph-version allowlist; Slab 4 Story 4.5 wires the real registry."""


class RunState(BaseModel):
    """Top-level run state. Encodes NFR-X1–X5 reproducibility invariants."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: UUID = Field(
        default_factory=uuid4,
        description="UUID4 identity for this run.",
    )
    status: RunStatus = Field(
        default="pending",
        description="Closed enum: pending | running | complete | failed.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware run-start timestamp.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="REQUIRED iff status == 'complete'; timezone-aware.",
    )
    graph_version: str = Field(
        ...,
        description=(
            "Frozen graph version identifier; 1.2 stub-validated against "
            "ALLOWED_GRAPH_VERSIONS (Slab 4 Story 4.5 wires the real registry)."
        ),
    )
    temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="NFR-X5: documented temperature variance bound to [0.0, 2.0].",
    )
    model_resolution_trail: list[ModelResolutionEntry] = Field(
        default_factory=list,
        description=(
            "NFR-X4: append-only resolution trail. ModelResolutionEntry is a "
            "STUB shape in 1.2; Story 1.3 replaces it with the full cascade entry."
        ),
    )
    model_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Runtime node_id -> model_id override map (Story 3.5).",
    )
    sanctum_fingerprint: SanctumFingerprint | None = Field(
        default=None,
        description="NFR-X3: content-addressable sanctum snapshot identity at run-start.",
    )
    marcus_fingerprint: tuple[str, UUID] | None = Field(
        default=None,
        description=(
            "Story 3.1 Marcus cold-read fingerprint: "
            "(sanctum_sha256, session_uuid4)."
        ),
    )
    story_states: list[StoryState] = Field(
        default_factory=list,
        description="Per-story execution slices captured under this run.",
    )
    cache_state: CacheState | None = Field(
        default=None,
        description="Optional cache-prefix tracking; populated by D5 cold-read flow.",
    )
    production_envelope: ProductionEnvelope | None = Field(
        default=None,
        description=(
            "Production composition accumulator. Distinct from cache_state, "
            "which remains per-specialist scratch."
        ),
    )
    component_selection: ComponentSelection | None = Field(
        default=None,
        description=(
            "Compile-time component selection this run composed + froze (S2). "
            "Persisted in the run record so the resume/recover walk REHYDRATES it "
            "and recomposes the SAME graph — never re-defaults (two-walk trap). "
            "None on legacy runs predating composition."
        ),
    )

    @field_validator("run_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_created_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("completed_at")
    @classmethod
    def _enforce_completed_tz(cls, value: datetime | None) -> datetime | None:
        return enforce_tz_aware(value) if value is not None else None

    @field_validator("marcus_fingerprint")
    @classmethod
    def _enforce_marcus_fingerprint(
        cls,
        value: tuple[str, UUID] | None,
    ) -> tuple[str, UUID] | None:
        if value is None:
            return None
        digest, session_id = value
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("marcus_fingerprint digest must be lowercase hex sha256")
        enforce_uuid4_version(session_id)
        return value

    @field_validator("graph_version")
    @classmethod
    def _enforce_allowed_graph_version(cls, value: str) -> str:
        if value not in ALLOWED_GRAPH_VERSIONS:
            raise ValueError(
                f"graph_version {value!r} not in ALLOWED_GRAPH_VERSIONS "
                f"({sorted(ALLOWED_GRAPH_VERSIONS)}); Slab 4 Story 4.5 wires the real registry."
            )
        return value

    @model_validator(mode="after")
    def _check_invariants(self) -> RunState:
        _enforce_run_complete_invariant(status=self.status, completed_at=self.completed_at)
        return self


__all__ = ["ALLOWED_GRAPH_VERSIONS", "ComponentSelection", "RunState", "RunStatus"]
