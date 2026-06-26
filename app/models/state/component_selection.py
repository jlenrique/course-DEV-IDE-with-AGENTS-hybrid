"""`ComponentSelection` — the canonical record of which components a run composes.

Composition is a COMPILE-TIME act, before the freeze (composition-catalog
ratification 2026-06-25): the settled lesson plan selects components; a
deterministic composer assembles ONLY the selected components' nodes into ONE
graph; that assembled graph is frozen per run. This model is the minimal
canonical record of that selection — it lives on :class:`RunState` so the
resume/recover walk REHYDRATES it from the frozen run record and never
re-defaults (the two-walk trap, ``project_production_runner_two_walks``).

Canonical-JSON serialization (sorted keys, stable encoding) makes the selection
hashable into the two-part content-addressed digest in a hashseed-independent
way.
"""

from __future__ import annotations

import json
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class ComponentSelection(BaseModel):
    """Which lesson components are selected for this run.

    The closed component set at S2 is ``deck`` / ``motion`` / ``workbook``.
    ``deck`` is the base; ``motion`` and ``workbook`` are consumers of the deck
    (a typed producer->consumer DAG resolved by the composer). Widening the set
    (podcast / quiz) is a later governance act, not a runtime flag.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    deck: bool = Field(default=True, description="The base narrated-deck component.")
    motion: bool = Field(default=False, description="The motion/video component (consumes deck).")
    workbook: bool = Field(default=False, description="The workbook companion (consumes deck).")

    COMPONENTS: ClassVar[tuple[str, ...]] = ("deck", "motion", "workbook")

    @classmethod
    def production_default(cls) -> ComponentSelection:
        """The default production selection: deck + motion (today's full graph).

        Reproduces the current pipeline byte-identically (the motion nodes are
        present in the live manifest), so the conditional composer is a no-op
        for the default until the front door (S5) sets a narrower selection.
        """
        return cls(deck=True, motion=True, workbook=False)

    def as_map(self) -> dict[str, bool]:
        """Return the selection as a plain ``{component: bool}`` mapping."""
        return {name: bool(getattr(self, name)) for name in self.COMPONENTS}

    def selected_components(self) -> tuple[str, ...]:
        """Return the sorted tuple of selected component names."""
        return tuple(name for name in self.COMPONENTS if getattr(self, name))

    def canonical_bytes(self) -> bytes:
        """Return the canonical-JSON encoding (sorted keys, stable, hashseed-independent)."""
        return json.dumps(
            self.as_map(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")


__all__ = ["ComponentSelection"]
