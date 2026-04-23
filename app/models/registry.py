"""`PipelineRegistry` — model catalog (Story 1.3 full schema, replaces 1.1c stub).

Per architecture §D2 + §D13 the registry is the source of truth for the
LLM model catalog the runtime can resolve to. Each entry carries identity,
provider, capacity (context window), tier (reasoning/code/fast), pricing,
and an availability flag the operator can flip without removing the entry.

Per D13 registry-bump policy:
- Tier-1 (additive): adding a new model is dev-agent authority.
- Tier-2 (subtractive / version-pin change): party-mode round required.
- Tier-3 (provider family change): party-mode + version bump in this module.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.state._base import enforce_uuid4_version

ProviderId = Literal["openai"]
"""Closed enum: providers the migration runtime supports in Slab 1."""

ModelTier = Literal["reasoning", "code", "fast"]
"""Closed enum: capability tier classification for cascade auto-select policy."""


class RegistryEntry(BaseModel):
    """One model entry in the catalog."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    id: UUID = Field(
        default_factory=uuid4,
        description="UUID4 stable identity for this catalog entry.",
    )
    model_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Provider-side model identifier (e.g. 'gpt-5.4', 'gpt-5-haiku'); "
            "the string the runtime passes to the provider's chat-completions API."
        ),
    )
    display_name: str = Field(
        ...,
        min_length=1,
        description="Operator-facing human label.",
    )
    provider: ProviderId = Field(
        ...,
        description="Closed enum: openai (extended in later slabs as new providers land).",
    )
    context_window: int = Field(
        ...,
        gt=0,
        description="Maximum prompt+completion tokens this model accepts.",
    )
    cost_per_million_input_tokens: Decimal = Field(
        ...,
        ge=Decimal("0"),
        description="USD per 1,000,000 input tokens (pricing snapshot, refresh per D13).",
    )
    cost_per_million_output_tokens: Decimal = Field(
        ...,
        ge=Decimal("0"),
        description="USD per 1,000,000 output tokens (pricing snapshot, refresh per D13).",
    )
    tier: ModelTier = Field(
        ...,
        description="Closed enum: reasoning | code | fast (drives auto-select policy).",
    )
    available: bool = Field(
        default=True,
        description=(
            "Operator availability flag; toggling False removes the entry from "
            "selector resolution without deleting the catalog row (D13 Tier-1)."
        ),
    )

    @field_validator("id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)


class PipelineRegistry(BaseModel):
    """Catalog container with cascade-default + auto-select-enable flag."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: UUID = Field(
        default_factory=uuid4,
        description="UUID4 identity for this registry instance (snapshot of catalog state).",
    )
    entries: list[RegistryEntry] = Field(
        default_factory=list,
        description="Model catalog entries.",
    )
    default_model_id: str = Field(
        ...,
        min_length=1,
        description=(
            "model_id of the entry the registry falls back to as `registry_default` "
            "in the cascade. Cross-field-validated to match an existing entry."
        ),
    )
    auto_select_enabled: bool = Field(
        default=True,
        description=(
            "When True, cascade falls through to ModelSelectionPolicy auto-select "
            "rules after registry default is exhausted. False disables auto-select "
            "(per-call + per-specialist + registry default only)."
        ),
    )

    @field_validator("id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @model_validator(mode="after")
    def _check_default_model_id_in_entries(self) -> PipelineRegistry:
        if not self.entries:
            # Empty registry is a deployment error but does not violate the model;
            # selector raises when asked to resolve. This validator only gates the
            # default-model invariant when entries exist.
            return self
        known = {e.model_id for e in self.entries if e.available}
        if self.default_model_id not in known:
            raise ValueError(
                f"default_model_id={self.default_model_id!r} not in registry's available "
                f"entries (got {sorted(known)})"
            )
        return self


__all__ = ["ModelTier", "PipelineRegistry", "ProviderId", "RegistryEntry"]
