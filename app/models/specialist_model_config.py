"""`SpecialistModelConfig` — per-specialist `model_config.yaml` shape (Story 1.3).

Each Slab 2 specialist subpackage carries one `model_config.yaml` declaring
its preferred model, optional per-node overrides, and default temperature.
The selector reads this at the per_specialist cascade level (D2).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SpecialistModelConfig(BaseModel):
    """Per-specialist model preferences. Read by the selector cascade."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    specialist_id: str = Field(
        ...,
        min_length=1,
        description="Stable specialist identifier (matches the directory name).",
    )
    default_model: str = Field(
        ...,
        min_length=1,
        description="model_id the specialist prefers when no per-call override is provided.",
    )
    per_node_overrides: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Optional per-node-name model_id overrides; node names are "
            "specialist-internal. Empty by default."
        ),
    )
    temperature_default: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Default temperature for this specialist; bounded [0.0, 2.0].",
    )


__all__ = ["SpecialistModelConfig"]
