"""Curated bundle catalog (S4) — the ratified 3 blessed bundles as declarative
records, with a per-component capability TIER so Marcus can gate HONESTLY.

A *bundle* is a named, blessed :class:`ComponentSelection` plus display metadata
and required inputs. The catalog sits ON TOP of S2's ``ComponentSelection`` /
``compose_manifest``: a bundle is just a curated selection the composer already
knows how to assemble. This module adds NO new composition mechanism — it is a
pure additive model + frozen registry, mirroring the ``modality_registry`` /
``component_type_registry`` idioms (Pydantic-v2 closed-enum models wrapped in
``types.MappingProxyType``).

Honesty layer (the reason this is a catalog and not a hardcoded dropdown):
each component carries a :data:`CapabilityTier` seeded from CURRENT REALITY —
``deck`` is proven_wired, ``motion`` is proven_regressed_repairable (fail-loud
landed, real producer pending), ``workbook`` is mechanism_only_never_produced
(design done, build pending). A bundle's readiness is the MIN tier across its
selected components (worst-wins). The S5 front door reads
:func:`bundle_readiness` to grey out / flag bundles that are not yet fully
proven, rather than offering an honest-looking choice that silently can't deliver.

Closed sets (widening is a governance act, not a runtime flag):
  * :data:`BundleId`        — the 3 ratified bundle ids.
  * :data:`CapabilityTier`  — the 4 honesty tiers.
  * :data:`BundleReadiness` — the 3 front-door verdicts.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.state.component_selection import ComponentSelection

SCHEMA_VERSION: Final[str] = "1.0"
"""Bundle-catalog schema version; bump on closed-set drift (new bundle / tier)."""


# ---------------------------------------------------------------------------
# Closed enums (AC: closed-enum red-rejection on bundle ids + tier values)
# ---------------------------------------------------------------------------

BundleId = Literal[
    "narrated-deck",
    "narrated-deck-with-motion",
    "narrated-deck-with-workbook",
]
"""The 3 ratified bundle ids. Widening requires a SCHEMA_VERSION bump + amendment."""

ComponentName = Literal["deck", "motion", "workbook"]
"""The closed component set (mirrors :data:`ComponentSelection.COMPONENTS`)."""

CapabilityTier = Literal[
    "proven_wired",
    "proven_regressed_repairable",
    "mechanism_only_never_produced",
    "shelf",
]
"""Per-component honesty tier, best -> worst. Drives the front-door readiness verdict.

  * ``proven_wired``                  — produces real artifacts live today.
  * ``proven_regressed_repairable``   — once proven, currently fails-loud; repair is wiring only.
  * ``mechanism_only_never_produced`` — design/mechanism landed, never produced a real artifact.
  * ``shelf``                         — named but not built (placeholder).
"""

BundleReadiness = Literal["fully_proven", "partial", "not_yet"]
"""Front-door verdict derived from a bundle's MIN component tier."""


# Worst-wins ordering: lower rank == better. Used to take the MIN tier (worst) of
# a bundle's components.
_TIER_RANK: Final[dict[str, int]] = {
    "proven_wired": 0,
    "proven_regressed_repairable": 1,
    "mechanism_only_never_produced": 2,
    "shelf": 3,
}

# Map the worst tier in a bundle to the front-door verdict.
_TIER_TO_READINESS: Final[dict[str, BundleReadiness]] = {
    "proven_wired": "fully_proven",
    "proven_regressed_repairable": "partial",
    "mechanism_only_never_produced": "not_yet",
    "shelf": "not_yet",
}


# ---------------------------------------------------------------------------
# ComponentCapability — the per-component honesty record
# ---------------------------------------------------------------------------


class ComponentCapability(BaseModel):
    """One component's honesty tier. ``component`` and ``tier`` are closed enums."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    component: ComponentName = Field(
        ...,
        description="The component this capability tier describes.",
    )
    tier: CapabilityTier = Field(
        ...,
        description="Honesty tier (best->worst) seeded from current production reality.",
    )
    note: str = Field(
        ...,
        description="Free-text rationale for the tier (what 'proven'/'regressed' means here).",
    )


# ---------------------------------------------------------------------------
# BundleRecord — a named blessed selection + display metadata
# ---------------------------------------------------------------------------


class BundleRecord(BaseModel):
    """One curated bundle: a blessed :class:`ComponentSelection` + display metadata.

    ``required_inputs`` is ADDITIVE across the catalog (B1 subset B2 subset B3):
    every bundle needs ``corpus_path``; richer bundles never need fewer inputs.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    id: BundleId = Field(..., description="Closed-set bundle id.")
    display_name: str = Field(
        ..., min_length=1, description="Operator-facing bundle name."
    )
    selection: ComponentSelection = Field(
        ..., description="The blessed component selection the composer assembles."
    )
    required_inputs: tuple[str, ...] = Field(
        ...,
        min_length=1,
        description="Inputs the operator must supply (additive across the catalog).",
    )
    description: str = Field(..., min_length=1, description="Short bundle description.")

    @model_validator(mode="after")
    def _selected_components_have_capability_tiers(self) -> BundleRecord:
        """Defense in depth: every selected component must have a seeded tier, so
        :func:`bundle_readiness` can never silently skip an ungraded component."""
        for name in self.selection.selected_components():
            if name not in _CAPABILITY_TIERS_UNDERLYING:
                raise ValueError(
                    f"BundleRecord {self.id!r} selects component {name!r} which has "
                    "no capability tier in CAPABILITY_TIERS (honesty gap)"
                )
        return self


# ---------------------------------------------------------------------------
# CAPABILITY_TIERS — per-component honesty registry (MappingProxyType)
# ---------------------------------------------------------------------------


_CAPABILITY_TIERS_UNDERLYING: dict[str, ComponentCapability] = {
    "deck": ComponentCapability(
        component="deck",
        tier="proven_wired",
        note=(
            "The narrated deck is the proven base: it produces real published "
            "artifacts live today (Gamma/Gary -> Descript)."
        ),
    ),
    "motion": ComponentCapability(
        component="motion",
        tier="proven_regressed_repairable",
        note=(
            "Motion was proven in earlier trials; the current graph fails-loud "
            "(fail-loud guard landed). Restoring it is wiring the real producer, "
            "not redesign."
        ),
    ),
    "workbook": ComponentCapability(
        component="workbook",
        tier="mechanism_only_never_produced",
        note=(
            "The workbook companion has design + a composer stub node (S2) but no "
            "real producer has emitted a workbook artifact yet (build pending, S3)."
        ),
    ),
}


CAPABILITY_TIERS: Mapping[str, ComponentCapability] = MappingProxyType(
    _CAPABILITY_TIERS_UNDERLYING
)
"""Closed per-component honesty registry wrapped in :class:`types.MappingProxyType`."""


# ---------------------------------------------------------------------------
# BUNDLE_CATALOG — the ratified 3 bundles (MappingProxyType)
# ---------------------------------------------------------------------------


_BUNDLE_CATALOG_UNDERLYING: dict[str, BundleRecord] = {
    "narrated-deck": BundleRecord(
        id="narrated-deck",
        display_name="Narrated Deck",
        selection=ComponentSelection(deck=True, motion=False, workbook=False),
        required_inputs=("corpus_path",),
        description=(
            "The proven base bundle: a narrated slide deck produced from the corpus."
        ),
    ),
    "narrated-deck-with-motion": BundleRecord(
        id="narrated-deck-with-motion",
        display_name="Narrated Deck + Motion",
        selection=ComponentSelection(deck=True, motion=True, workbook=False),
        required_inputs=("corpus_path",),
        description=(
            "The narrated deck plus motion/video segments (motion consumes the deck)."
        ),
    ),
    "narrated-deck-with-workbook": BundleRecord(
        id="narrated-deck-with-workbook",
        display_name="Narrated Deck + Motion + Workbook",
        selection=ComponentSelection(deck=True, motion=True, workbook=True),
        required_inputs=("corpus_path",),
        description=(
            "The full bundle: narrated deck, motion, and the read-in-depth workbook "
            "companion (workbook consumes the deck)."
        ),
    ),
}


# Defense in depth: assert every selected component has a tier over the seeded
# literal at import time (catches a typo before the first consumer call).
for _bundle_id, _record in _BUNDLE_CATALOG_UNDERLYING.items():
    assert _record.id == _bundle_id, (  # noqa: S101 — import-time invariant
        f"BUNDLE_CATALOG key {_bundle_id!r} != record id {_record.id!r}"
    )
    for _comp in _record.selection.selected_components():
        assert _comp in _CAPABILITY_TIERS_UNDERLYING, (  # noqa: S101
            f"BUNDLE_CATALOG seed error: {_bundle_id!r} selects ungraded {_comp!r}"
        )
del _bundle_id, _record, _comp


BUNDLE_CATALOG: Mapping[str, BundleRecord] = MappingProxyType(
    _BUNDLE_CATALOG_UNDERLYING
)
"""Closed curated-bundle catalog wrapped in :class:`types.MappingProxyType`."""


# ---------------------------------------------------------------------------
# Query API (the honesty layer the S5 front door reads)
# ---------------------------------------------------------------------------


def get_bundle(bundle_id: str) -> BundleRecord | None:
    """Return the :class:`BundleRecord` for ``bundle_id`` or ``None`` (closed set,
    no warn — consumers handle ``None`` explicitly)."""
    return BUNDLE_CATALOG.get(bundle_id)


def component_capability(component: str) -> ComponentCapability | None:
    """Return the :class:`ComponentCapability` for ``component`` or ``None``."""
    return CAPABILITY_TIERS.get(component)


def _resolve(bundle: BundleRecord | str) -> BundleRecord:
    if isinstance(bundle, BundleRecord):
        return bundle
    record = BUNDLE_CATALOG.get(bundle)
    if record is None:
        raise KeyError(f"unknown bundle id {bundle!r} (closed catalog)")
    return record


def min_capability_tier(bundle: BundleRecord | str) -> CapabilityTier:
    """Return the WORST (min) capability tier across the bundle's selected components.

    Raises :class:`KeyError` on an unknown bundle id (closed catalog)."""
    record = _resolve(bundle)
    selected = record.selection.selected_components()
    worst = max(
        selected,
        key=lambda name: _TIER_RANK[CAPABILITY_TIERS[name].tier],
    )
    return CAPABILITY_TIERS[worst].tier


def bundle_readiness(bundle: BundleRecord | str) -> BundleReadiness:
    """Return the front-door verdict (``fully_proven`` / ``partial`` / ``not_yet``)
    derived from the bundle's worst component tier.

    Raises :class:`KeyError` on an unknown bundle id (closed catalog)."""
    return _TIER_TO_READINESS[min_capability_tier(bundle)]


__all__ = [
    "BUNDLE_CATALOG",
    "CAPABILITY_TIERS",
    "SCHEMA_VERSION",
    "BundleId",
    "BundleReadiness",
    "BundleRecord",
    "CapabilityTier",
    "ComponentCapability",
    "ComponentName",
    "bundle_readiness",
    "component_capability",
    "get_bundle",
    "min_capability_tier",
]
