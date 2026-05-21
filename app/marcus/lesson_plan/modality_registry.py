"""Modality registry (Story 31-3 AC-B.1 / AC-B.6 / AC-B.8 / AC-B.9).

Audience: Marcus (30-3 consumer), Irene diagnostician (29-2), Tracy three-modes
(28-2) — registry consumers. Closed-set catalog of atomic producer targets; widening
requires schema-version bump + SCHEMA_CHANGELOG entry + explicit amendment (AC-C.4).

Five entries at MVP:
    - ``slides``              — ``ready``   (Gary/Gamma pre-MVP; backfilled by separate amendment)
    - ``blueprint``           — ``ready``   (31-4 backfills producer_class_path)
    - ``leader-guide``        — ``pending`` (post-MVP)
    - ``handout``             — ``pending`` (post-MVP)
    - ``classroom-exercise``  — ``pending`` (post-MVP)

Query API (AC-B.6):
    - :func:`get_modality_entry` — positive lookup or ``None`` (no warn, no raise).
    - :func:`list_ready_modalities` / :func:`list_pending_modalities` — frozensets.

Immutability (AC-B.8): ``MODALITY_REGISTRY`` is ``types.MappingProxyType`` wrapping
the underlying dict literal. Any mutation (``setitem``, ``delitem``, ``clear``,
``update``, ``pop``, ``popitem``, ``setdefault``, attribute set) raises
``TypeError``/``AttributeError``.

Discipline carry-forward (R1 amendment 17 / R2 rider S-3):
    Maya-facing descriptions MUST NOT contain the forbidden Marcus-duality tokens.
    Enforced at AC-T.8.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION: Final[str] = "1.0"
"""Modality Registry schema version (AC-B.9); bump on closed-set drift (AC-C.4)."""


# ---------------------------------------------------------------------------
# Closed ModalityRef set (AC-B.1; AC-C.4 widening requires amendment)
# ---------------------------------------------------------------------------

ModalityRef = Literal[
    "slides",
    "blueprint",
    "leader-guide",
    "handout",
    "classroom-exercise",
]
"""The five closed-set atomic producer targets at MVP.

Widening requires: (a) ruling amendment, (b) ``SCHEMA_VERSION`` bump,
(c) ``SCHEMA_CHANGELOG.md`` entry, (d) update to :data:`MODALITY_REGISTRY` +
tests. No backdoor, no runtime registration.
"""


# ---------------------------------------------------------------------------
# ModalityEntry Pydantic model (AC-B.1 + AC-C.6 invariant)
# ---------------------------------------------------------------------------


class ModalityEntry(BaseModel):
    """One entry in :data:`MODALITY_REGISTRY`.

    AC-C.6 invariant: ``pending`` modalities MUST have
    ``producer_class_path is None``; ``ready`` modalities MAY be ``None``
    (Gary/slides + 31-4/blueprint backfill later) OR a dotted-path string.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    modality_ref: ModalityRef = Field(
        ...,
        description="Stable identifier for the atomic producer target.",
    )
    status: Literal["ready", "pending"] = Field(
        ...,
        description=(
            "Readiness state for this modality. 'ready' means a producer exists "
            "(or will be backfilled imminently); 'pending' names a post-MVP target."
        ),
    )
    producer_class_path: str | None = Field(
        ...,
        description=(
            "Dotted Python path to the concrete producer class, or null if no "
            "producer is wired yet. Must be null whenever status == 'pending'."
        ),
    )
    description: str = Field(
        ...,
        description=(
            "Free-text human-readable summary of the modality. No min_length "
            "per R2 rider S-2 carry-forward (free-text discipline)."
        ),
    )

    @model_validator(mode="after")
    def _pending_implies_null_producer(self) -> ModalityEntry:
        """AC-C.6 invariant."""
        if self.status == "pending" and self.producer_class_path is not None:
            raise ValueError(
                f"ModalityEntry invariant violation: status='pending' requires "
                f"producer_class_path=None; got {self.producer_class_path!r} "
                f"on modality_ref={self.modality_ref!r}"
            )
        return self


# ---------------------------------------------------------------------------
# MODALITY_REGISTRY — the closed-set MappingProxyType (AC-B.1 + AC-B.8)
# ---------------------------------------------------------------------------


_MODALITY_REGISTRY_UNDERLYING: dict[str, ModalityEntry] = {
    "slides": ModalityEntry(
        modality_ref="slides",
        status="ready",
        producer_class_path=None,
        description=(
            "Slide deck modality. Pre-MVP producer (Gary / Gamma integration) exists "
            "as separate pipeline; adoption of ModalityProducer ABC is a separate "
            "amendment story. producer_class_path backfilled at that time."
        ),
    ),
    "blueprint": ModalityEntry(
        modality_ref="blueprint",
        status="ready",
        producer_class_path="marcus.lesson_plan.blueprint_producer.BlueprintProducer",
        description=(
            "Blueprint modality — authoring-ready lesson blueprint artifact. "
            "Producer landed in Story 31-4 (blueprint-producer); "
            "producer_class_path now points at the concrete producer."
        ),
    ),
    "leader-guide": ModalityEntry(
        modality_ref="leader-guide",
        status="pending",
        producer_class_path=None,
        description=(
            "Leader guide modality. Post-MVP; named here to pin the closed set."
        ),
    ),
    "handout": ModalityEntry(
        modality_ref="handout",
        status="pending",
        producer_class_path=None,
        description=(
            "Participant handout modality. Post-MVP; named here to pin the closed set."
        ),
    ),
    "classroom-exercise": ModalityEntry(
        modality_ref="classroom-exercise",
        status="pending",
        producer_class_path=None,
        description=(
            "Classroom-exercise modality. Post-MVP; named here to pin the closed set."
        ),
    ),
}


MODALITY_REGISTRY: Mapping[str, ModalityEntry] = MappingProxyType(
    _MODALITY_REGISTRY_UNDERLYING
)
"""Closed-set modality catalog wrapped in :class:`types.MappingProxyType`.

Any mutation (setitem, delitem, clear, update, pop, popitem, setdefault,
attribute assignment) raises at runtime. Widening requires amendment per
AC-C.4.
"""


# ---------------------------------------------------------------------------
# Query API (AC-B.6)
# ---------------------------------------------------------------------------


def get_modality_entry(modality_ref: str) -> ModalityEntry | None:
    """Return the :class:`ModalityEntry` for ``modality_ref`` or ``None``.

    Unlike :func:`marcus.lesson_plan.event_type_registry.validate_event_type`,
    this lookup does NOT warn on unknown values. Modality registry is a CLOSED
    SET (AC-B.8), not an extensibility surface. Consumers handle the ``None``
    return explicitly.
    """
    return MODALITY_REGISTRY.get(modality_ref)


def list_ready_modalities() -> frozenset[str]:
    """Return the frozenset of ``modality_ref`` values whose status is 'ready'."""
    return frozenset(
        ref for ref, entry in MODALITY_REGISTRY.items() if entry.status == "ready"
    )


def list_pending_modalities() -> frozenset[str]:
    """Return the frozenset of ``modality_ref`` values whose status is 'pending'."""
    return frozenset(
        ref for ref, entry in MODALITY_REGISTRY.items() if entry.status == "pending"
    )


__all__ = [
    "MODALITY_REGISTRY",
    "SCHEMA_VERSION",
    "ModalityEntry",
    "ModalityRef",
    "get_modality_entry",
    "list_pending_modalities",
    "list_ready_modalities",
]
