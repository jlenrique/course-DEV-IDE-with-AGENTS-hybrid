"""Adapter FUNCTIONS bridging the canonical LO entity to the 3 legacy reps.

Story G0-S1, AC-S1-5. These are PURE functions (no persisted shim class). They
are the back-compat bridge that lets existing producers/consumers keep working
unchanged while S1 is additive; per ratification 5 each is DELETED when its last
native consumer is rewired in S2/S3.

This module -- unlike ``learning_objective.py`` -- intentionally depends on both
the canonical entity AND the legacy reps (``LearningObjectiveBrief`` from the
workbook producer, ``WorkbookSection`` from the collateral spec). Keeping the
bridge here preserves the entity module's acyclic, consumer-free dependency
graph for the S3 rewire.

Discipline note (R1 ruling amendment 17 / R2 rider S-3): Marcus is one voice.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import get_args

from app.marcus.lesson_plan.collateral_spec import WorkbookSection
from app.marcus.lesson_plan.learning_objective import (
    BloomLevel,
    Confidence,
    LearningObjective,
    SourceRef,
)
from app.marcus.lesson_plan.workbook_producer import LearningObjectiveBrief

_BLOOM_LEVELS: frozenset[str] = frozenset(get_args(BloomLevel))


def _coerce_bloom(raw: str | None) -> BloomLevel | None:
    """Coerce a legacy brief's bare-``str`` bloom_level to the canonical enum.

    ``LearningObjectiveBrief.bloom_level`` is an unconstrained ``str`` while the
    canonical entity uses the closed six-level ``BloomLevel``. The realistic
    legacy variance is CASE (``"Analyze"`` vs ``"analyze"``), which we normalize
    so a brief that the legacy rep accepted keeps round-tripping. An empty/blank
    bloom maps to ``None`` (optional at provisional). A non-empty string that is
    still not a Bloom level after case-folding (e.g. ``"synthesize"``) is
    genuinely bad data and is surfaced LOUDLY with a clear message rather than a
    cryptic Pydantic error or a silent drop (T11 back-compat finding).
    """
    if raw is None:
        return None
    folded = raw.strip().lower()
    if not folded:
        return None
    if folded not in _BLOOM_LEVELS:
        raise ValueError(
            f"workbook brief bloom_level {raw!r} is not a canonical Bloom level "
            f"(expected one of {sorted(_BLOOM_LEVELS)}, case-insensitive)"
        )
    return folded  # type: ignore[return-value]


def from_irene_statement(
    statement: str,
    *,
    objective_id: str,
    source_refs: Sequence[SourceRef] | None = None,
    bloom_level: BloomLevel | None = None,
    confidence: Confidence = "medium",
) -> LearningObjective:
    """Lift an Irene Pass-1 bare ``learning_objective`` string into a canonical LO.

    Irene Pass-1 emits a bare statement string with no provenance; the lifted LO
    is ``status="provisional"`` (the mint state). ``source_refs`` defaults to
    empty (provisional allows >=0). ``bloom_level`` is optional at provisional
    and carried through when supplied (the workbook-brief bridge supplies it).
    """
    return LearningObjective(
        objective_id=objective_id,
        statement=statement,
        status="provisional",
        confidence=confidence,
        bloom_level=bloom_level,
        source_refs=list(source_refs) if source_refs is not None else [],
        adequacy=None,
    )


def from_workbook_brief(brief: LearningObjectiveBrief) -> LearningObjective:
    """Lift a legacy ``LearningObjectiveBrief`` into a canonical provisional LO.

    The brief carries only {objective_id, bloom_level, statement}; the lifted LO
    is ``provisional`` with those three fields populated and no provenance yet.
    """
    return from_irene_statement(
        brief.statement,
        objective_id=brief.objective_id,
        bloom_level=_coerce_bloom(brief.bloom_level),
    )


def to_workbook_brief(lo: LearningObjective) -> LearningObjectiveBrief:
    """Project a canonical LO back down to the legacy ``LearningObjectiveBrief``.

    Back-compat bridge so ``assert_learning_objective_bindings`` and
    ``produce_tejal_workbook.py`` keep working unchanged. The brief requires a
    Bloom level, so an LO with ``bloom_level=None`` cannot be projected.
    """
    if lo.bloom_level is None:
        raise ValueError(
            f"learning objective {lo.objective_id!r} has no bloom_level; cannot "
            "project to a workbook brief"
        )
    return LearningObjectiveBrief(
        objective_id=lo.objective_id,
        bloom_level=lo.bloom_level,
        statement=lo.statement,
    )


def section_binds_objective(
    section: WorkbookSection,
    lo: LearningObjective,
) -> bool:
    """Resolve the ``WorkbookSection.learning_objective_id`` <-> ``LO.objective_id``
    binding: True iff the section's open-id binding points at this LO."""
    return section.learning_objective_id == lo.objective_id


__all__ = [
    "from_irene_statement",
    "from_workbook_brief",
    "section_binds_objective",
    "to_workbook_brief",
]
