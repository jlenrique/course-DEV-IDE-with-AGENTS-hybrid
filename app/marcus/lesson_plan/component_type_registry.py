"""Component-type registry (Story 31-3 AC-B.2 / AC-B.6 / AC-B.8 / AC-B.9).

Audience: prompt-pack authors + future component-type consumers. Closed-set N=2
catalog of composite packages built from atomic modalities at MVP. Widening
requires schema-version bump + SCHEMA_CHANGELOG entry + explicit amendment
(AC-C.5).

Two entries at MVP (AC-B.2):
    - ``narrated-deck``                — composes ``("slides",)``
    - ``motion-enabled-narrated-lesson`` — composes ``("slides", "blueprint")``

Composition constraint (AC-T.3): every element of ``modality_refs`` MUST be a
key in :data:`app.marcus.lesson_plan.modality_registry.MODALITY_REGISTRY`. Enforced
both by :class:`ComponentTypeEntry`'s ``@model_validator(mode="after")`` AND at
module import time via an assertion over the seeded dict literal (defense in
depth).

Query API (AC-B.6): :func:`get_component_type_entry`.

Immutability (AC-B.8): ``COMPONENT_TYPE_REGISTRY`` is ``types.MappingProxyType``.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.marcus.lesson_plan.modality_registry import MODALITY_REGISTRY, ModalityRef

SCHEMA_VERSION: Final[str] = "1.0"
"""Component Type Registry schema version (AC-B.9)."""


# ---------------------------------------------------------------------------
# ComponentTypeEntry Pydantic model (AC-B.2 + composition-validity validator)
# ---------------------------------------------------------------------------


class ComponentTypeEntry(BaseModel):
    """One entry in :data:`COMPONENT_TYPE_REGISTRY`.

    ``modality_refs`` is a ``tuple`` (frozen-by-value); every element MUST be a
    valid key in :data:`MODALITY_REGISTRY`. Recursive composites (composite of
    composites) are out-of-scope at MVP (AC-C.7).
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    component_type_ref: str = Field(
        ...,
        min_length=1,
        description="Stable identifier for this composite-package shape.",
    )
    modality_refs: tuple[ModalityRef, ...] = Field(
        ...,
        description=(
            "Flat tuple of modality_ref values this component type composes. "
            "Every element must be a key in the modality registry."
        ),
    )
    description: str = Field(
        ...,
        description=(
            "Free-text human-readable summary of the composite. No min_length "
            "per R2 rider S-2 carry-forward (free-text discipline)."
        ),
    )
    prompt_pack_version: str | None = Field(
        ...,
        description=(
            "Optional pointer to the prompt-pack revision that composes this "
            "component type, or null if unset. Null at MVP."
        ),
    )

    @model_validator(mode="after")
    def _every_modality_ref_must_be_registered(self) -> ComponentTypeEntry:
        for ref in self.modality_refs:
            if ref not in MODALITY_REGISTRY:
                raise ValueError(
                    f"ComponentTypeEntry composition invalid: "
                    f"component_type_ref={self.component_type_ref!r} references "
                    f"modality_ref={ref!r} which is not a key in MODALITY_REGISTRY"
                )
        return self


# ---------------------------------------------------------------------------
# COMPONENT_TYPE_REGISTRY — the closed N=2 MappingProxyType (AC-B.2 + AC-B.8)
# ---------------------------------------------------------------------------


_COMPONENT_TYPE_REGISTRY_UNDERLYING: dict[str, ComponentTypeEntry] = {
    "narrated-deck": ComponentTypeEntry(
        component_type_ref="narrated-deck",
        modality_refs=("slides",),
        description=(
            "Minimal single-modality composite: slide deck packaged for "
            "downstream narration binding (narration itself is post-MVP). "
            "Names the most common MVP output shape."
        ),
        prompt_pack_version=None,
    ),
    "motion-enabled-narrated-lesson": ComponentTypeEntry(
        component_type_ref="motion-enabled-narrated-lesson",
        modality_refs=("slides", "blueprint"),
        description=(
            "Two-modality composite: slides plus blueprint. Motion and "
            "narration are bound at the production site per prompt-pack "
            "v4.2; the composite declares only the package-level shape."
        ),
        prompt_pack_version=None,
    ),
}


# Defense in depth: assert composition validity at module import time over the
# seeded dict. Catches any typo in the literal before first consumer call.
for _ct_ref, _entry in _COMPONENT_TYPE_REGISTRY_UNDERLYING.items():
    for _mref in _entry.modality_refs:
        assert _mref in MODALITY_REGISTRY, (  # noqa: S101 — import-time invariant
            f"COMPONENT_TYPE_REGISTRY seed error: {_ct_ref!r} references "
            f"unknown modality {_mref!r}"
        )
del _ct_ref, _entry, _mref


COMPONENT_TYPE_REGISTRY: Mapping[str, ComponentTypeEntry] = MappingProxyType(
    _COMPONENT_TYPE_REGISTRY_UNDERLYING
)
"""Closed-set composite-package catalog wrapped in :class:`types.MappingProxyType`."""


# ---------------------------------------------------------------------------
# Query API (AC-B.6)
# ---------------------------------------------------------------------------


def get_component_type_entry(component_type_ref: str) -> ComponentTypeEntry | None:
    """Return the :class:`ComponentTypeEntry` for ``component_type_ref`` or ``None``.

    No warn on unknown — closed set per AC-B.8. Consumers handle ``None``
    explicitly.
    """
    return COMPONENT_TYPE_REGISTRY.get(component_type_ref)


__all__ = [
    "COMPONENT_TYPE_REGISTRY",
    "SCHEMA_VERSION",
    "ComponentTypeEntry",
    "get_component_type_entry",
]
