"""Stub `PipelineRegistry` model for Slab 1 Story 1.1c.

This is intentionally minimal. Story 1.3 lands the full three-level model-cascade
schema (`PipelineRegistry` + `ModelSelectionPolicy`); this stub only provides the
shape needed by `app.models.registry_check` to validate `app/models/registry.yaml`
at AC-1.1c-A acceptance time.

Anti-pattern guard (story-cycle-efficiency §K-floor): keep this stub minimal.
Adding 1.3-scope fields here is scope creep into the next story.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PipelineRegistryEntry(BaseModel):
    """Single registry entry. 1.3 will tighten this with cascade rules + provider fields."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(min_length=1, description="Stable model identifier referenced by specialists.")
    default_model: str | None = Field(
        default=None,
        description="Optional default model alias; full cascade resolution lands in 1.3.",
    )


class PipelineRegistry(BaseModel):
    """Stub registry container. 1.3 will replace with the full three-level cascade schema."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    entries: list[PipelineRegistryEntry] = Field(default_factory=list)
