"""G0-enrichment artifact models (Story G0-S2).

The frozen, operator-confirmable result of the Marcus-SPOC G0 pre-pass: the
typed source manifest, the candidate provisional Learning Objectives, the A10
enumeration-provenance + traversal roots, and the Marcus-side anti-anchoring
artifacts (A4 independent-parse-first sidecar + A3 dissent ledger).

Authority: ``lo-schema-ratification-2026-06-26.md`` §4 (A3/A4/A10) and
``g0-enrichment-cycle-charter-2026-06-26.md`` (A1/A6/A10/D2). Adequacy is NOT
produced here (that is S3, ratification §3.1) — every provisional LO emitted by
this brick carries ``adequacy=None``.

Pydantic-v2 idioms (docs/dev-guide/pydantic-v2-schema-checklist.md):
    - ``ConfigDict(extra="forbid", validate_assignment=True)``; timezone-aware
      datetimes; closed enums via ``Literal``.
    - Internal audit fields (the independent-parse / operator-merge sidecar) use
      ``SkipJsonSchema[...] + Field(exclude=True)`` (checklist §5) so they never
      appear in default serialization nor the published JSON Schema.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.json_schema import SkipJsonSchema

from app.marcus.lesson_plan.learning_objective import LearningObjective
from app.marcus.lesson_plan.source_type import TypedComponent
from app.models.state._base import enforce_tz_aware

# ---------------------------------------------------------------------------
# A10 — enumeration provenance + traversal roots
# ---------------------------------------------------------------------------

TraversalRootKind = Literal["corpus_dir", "notion_page", "box_folder", "url_list"]
"""Closed kinds of enumeration root the deterministic composer may walk."""


class TraversalRoot(BaseModel):
    """One root the deterministic enumeration walked (A10).

    The decision card surfaces the ROOTS the operator pointed the run at — "these
    were the 3 roots," not just the leaf-file list — so a silently-pruned branch
    under D2-without-inventory is the cheapest thing to catch.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    root_id: str = Field(
        ...,
        min_length=1,
        description="Root identifier (path / page id / folder id / url-list name).",
    )
    kind: TraversalRootKind = Field(..., description="Closed traversal-root kind.")


class EnumerationProvenance(BaseModel):
    """Per-source record of HOW it entered the enumerated set (A10)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    source_id: str = Field(..., min_length=1, description="Enumerated source id.")
    root_id: str = Field(..., min_length=1, description="Which traversal root yielded this source.")
    connector: str = Field(
        default="local_file",
        min_length=1,
        description="Connector/traversal that surfaced it (local_file / notion / box / url).",
    )
    locator: str = Field(..., min_length=1, description="Leaf locator within the root (verbatim).")


# ---------------------------------------------------------------------------
# A4 — independent-parse-first sidecar + A3 dissent
# ---------------------------------------------------------------------------


class IndependentParse(BaseModel):
    """Marcus's own typing/LO analysis, written BEFORE any operator suggestion (A4)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    proposal: dict[str, Any] = Field(
        ...,
        description="Marcus's independent typing/LO proposal (the anti-anchoring baseline).",
    )
    ts: datetime = Field(..., description="Timezone-aware write time of the independent parse.")

    @field_validator("ts")
    @classmethod
    def _tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


class OperatorMerge(BaseModel):
    """An operator suggestion merged AFTER the independent parse (A4)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    suggestion: dict[str, Any] = Field(..., description="Operator-supplied typing/LO suggestion.")
    ts: datetime = Field(
        ..., description="Timezone-aware merge time (MUST be > independent_parse.ts)."
    )

    @field_validator("ts")
    @classmethod
    def _tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


DissentDisposition = Literal[
    "upheld",
    "overruled-by-operator",
    "folded-into-adequacy",
]


class Dissent(BaseModel):
    """A recorded Marcus-vs-operator disagreement on a typing or LO (A3, A11-hardened).

    Must be independent-parse-sourced (Marcus's position comes from the A4
    sidecar, not from an operator anchor) and is REAL (carries a concrete
    ``against`` target + both positions). Run-to-run variance is a run-level
    property the wiring derives from corpus content — a never-varying dissent is
    theater (A11).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    against: str = Field(
        ..., min_length=1, description="The source_id or objective_id the dissent is about."
    )
    marcus_position: str = Field(
        ..., min_length=1, description="Marcus's independent-parse position."
    )
    operator_position: str = Field(
        default="",
        description="Operator's position (empty until the operator weighs in at the gate).",
    )
    disposition: DissentDisposition = Field(
        default="upheld",
        description=(
            "How the dissent resolved: upheld | overruled-by-operator | folded-into-adequacy."
        ),
    )

    @field_validator("marcus_position", "against")
    @classmethod
    def _reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("dissent against/marcus_position must be non-empty")
        return value


# ---------------------------------------------------------------------------
# Reconcilable count view (file-coverage — every FILE covered by >=1 component)
# ---------------------------------------------------------------------------


class ReconcileView(BaseModel):
    """The operator-facing reconciliation: every enumerated FILE is accounted for.

    Component extraction (charter P1) makes FILES the A6 enumeration unit and
    COMPONENTS the typed deliverables (a file yields N components). The
    reconciliation is therefore FILE-COVERAGE, not a 1:1 typed-per-source count:
    ``n_files_in`` (the A6 deterministic file-enumeration count) MUST equal
    ``n_files_covered + n_files_ignored`` — every enumerated file is either
    covered by >=1 extracted component or operator-confirmed ``ignored``. No file
    is silently dropped. ``n_components`` is the total typed deliverable count
    (>= n_files_covered, since one file → many components); ``n_flagged`` is a
    NON-PARTITION view (a subset of ``n_components``: the classification-only /
    escape-hatch components) so the operator sees how many have no generator today.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    n_files_in: int = Field(
        ..., ge=0, description="Deterministically-enumerated FILE count (A6 unit)."
    )
    n_files_covered: int = Field(
        ..., ge=0, description="Enumerated files covered by >=1 extracted component."
    )
    n_files_ignored: int = Field(
        ..., ge=0, description="Operator-confirmed ignored files (no component extracted)."
    )
    n_components: int = Field(
        ..., ge=0, description="Total typed components extracted across all covered files."
    )
    n_flagged: int = Field(
        ...,
        ge=0,
        description="Classification-only/escape-hatch components (subset of n_components).",
    )

    @model_validator(mode="after")
    def _enforce_reconciliation(self) -> ReconcileView:
        if self.n_files_in != self.n_files_covered + self.n_files_ignored:
            raise ValueError(
                f"reconcile mismatch: n_files_in={self.n_files_in} != "
                f"n_files_covered={self.n_files_covered} + "
                f"n_files_ignored={self.n_files_ignored} (a file vanished from coverage)"
            )
        if self.n_files_covered > self.n_components:
            raise ValueError(
                f"n_files_covered={self.n_files_covered} cannot exceed "
                f"n_components={self.n_components} (a covered file owes >=1 component)"
            )
        if self.n_flagged > self.n_components:
            raise ValueError(
                f"n_flagged={self.n_flagged} cannot exceed n_components={self.n_components} "
                "(flagged is a subset of the components)"
            )
        return self


# ---------------------------------------------------------------------------
# The frozen enrichment result
# ---------------------------------------------------------------------------

SCHEMA_VERSION: Final[str] = "1.0"


class G0EnrichmentResult(BaseModel):
    """The frozen, operator-confirmable G0-enrichment artifact.

    Keyed to a corpus fingerprint so a graph replay with an unchanged corpus
    reads the frozen result (determinism). The A4 independent-parse sidecar +
    optional operator-merge are INTERNAL AUDIT fields (excluded from default
    serialization + JSON Schema); the deterministic A4 guard enforces
    ``independent_parse.ts < operator_merge.ts`` whenever a merge is present.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    corpus_fingerprint: str = Field(
        ...,
        description="sha256(concatenated per-file content hashes + model id) — the cache key.",
    )
    model_id: str = Field(
        ...,
        min_length=1,
        description="LLM model id that produced the typing/LO pre-pass (or the offline marker).",
    )
    typed_components: list[TypedComponent] = Field(
        default_factory=list,
        description="Per-COMPONENT TYPE assignments (N per file; orthogonal to directive role).",
    )
    provisional_los: list[LearningObjective] = Field(
        default_factory=list,
        description="Candidate LOs at status=provisional (adequacy=None — S3 produces adequacy).",
    )
    traversal_roots: list[TraversalRoot] = Field(
        default_factory=list,
        description="A10 enumeration roots the operator pointed the run at.",
    )
    enumeration_provenance: list[EnumerationProvenance] = Field(
        default_factory=list,
        description="A10 per-source 'how it entered the set' records.",
    )
    reconcile: ReconcileView = Field(..., description="D2 reconcilable count view.")
    dissents: list[Dissent] = Field(
        default_factory=list,
        description="A3 dissent ledger; the run-level invariant requires >=1 real dissent.",
    )

    # --- Internal audit sidecar (A4) — excluded from default dump + JSON Schema ---
    independent_parse: SkipJsonSchema[IndependentParse] = Field(
        ...,
        exclude=True,
        description="A4 anti-anchoring baseline; internal audit only.",
    )
    operator_merge: SkipJsonSchema[OperatorMerge | None] = Field(
        default=None,
        exclude=True,
        description=(
            "A4 operator-merge sidecar; internal audit only. ts MUST exceed independent_parse.ts."
        ),
    )

    @model_validator(mode="after")
    def _enforce_a4_ts_order(self) -> G0EnrichmentResult:
        if self.operator_merge is not None and not (
            self.independent_parse.ts < self.operator_merge.ts
        ):
            raise ValueError(
                "A4 violation: independent_parse.ts must precede operator_merge.ts "
                f"(independent={self.independent_parse.ts.isoformat()} "
                f">= merge={self.operator_merge.ts.isoformat()}); reject pre-surface"
            )
        return self

    @model_validator(mode="after")
    def _enforce_provisional_only(self) -> G0EnrichmentResult:
        for lo in self.provisional_los:
            if lo.status != "provisional":
                raise ValueError(
                    f"G0 brick emits only provisional LOs; got {lo.objective_id!r} "
                    f"at status {lo.status!r} (refine/ratify is S3+)"
                )
            if lo.adequacy is not None:
                raise ValueError(
                    f"G0 provisional LO {lo.objective_id!r} must carry adequacy=None "
                    "(adequacy is an S3 advisory output, ratification §3.1)"
                )
        return self

    def to_card_payload(self) -> dict[str, Any]:
        """Project the public (audit-excluded) shape for the decision card."""
        return self.model_dump(mode="json")


def assert_run_dissent_invariant(result: G0EnrichmentResult) -> None:
    """Run-level A3 invariant: >=1 REAL dissent across the corpus.

    A real dissent is independent-parse-sourced and names a concrete target with
    a non-empty Marcus position. Raises ``ValueError`` when no real dissent is
    present — a confirm-gate with zero dissent is anti-anchoring theater (A3/A11).
    """
    real = [d for d in result.dissents if d.against.strip() and d.marcus_position.strip()]
    if not real:
        raise ValueError(
            "A3 run-level invariant violated: the corpus produced no real dissent "
            "(>=1 independent-parse-sourced dissent is required; a never-dissenting "
            "run is theater)"
        )


def corpus_fingerprint(per_file_hashes: list[str], model_id: str) -> str:
    """sha256 of the concatenated per-file content hashes + model id (the cache key).

    Deterministic and order-stable: callers pass per-file hashes in a stable
    (sorted-path) order so an unchanged corpus + model yields an identical
    fingerprint across replays.
    """
    joined = "\n".join(per_file_hashes) + f"\nmodel:{model_id}"
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def file_content_hash(path: Path) -> str:
    """sha256 of one file's raw bytes (the per-file content hash)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


__all__ = [
    "SCHEMA_VERSION",
    "Dissent",
    "DissentDisposition",
    "EnumerationProvenance",
    "G0EnrichmentResult",
    "IndependentParse",
    "OperatorMerge",
    "ReconcileView",
    "TraversalRoot",
    "TraversalRootKind",
    "assert_run_dissent_invariant",
    "corpus_fingerprint",
    "file_content_hash",
]
