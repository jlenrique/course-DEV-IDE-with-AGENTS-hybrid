"""Gate G0E DecisionCard — operator confirm-gate #1 (Story G0-S2).

Emitted when the runner pauses at the ``g0-enrichment-gate`` (``G0E``), AFTER the
``g0-enrichment`` orchestration node has produced the frozen typed-manifest +
provisional-LO pre-pass. Carries the typed source manifest, the candidate
provisional LOs, the A10 enumeration-provenance + traversal roots, the
reconcilable count view, and the A3 dissent ledger the operator confirms.

Deterministic guard (S5 SPOC pattern): the model's typing/LO PROPOSAL never
auto-advances — the operator verdict is final. This card is the surface the
operator confirms; advancing is the runner's job on the operator verdict, never
the model's.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G0ECard(DecisionCardBase):
    """Operator confirm-gate #1 DecisionCard (G0 source-enrichment manifest)."""

    schema_version: Literal["v1"] = Field(
        default="v1",
        description="DecisionCard schema version.",
    )
    card_id: UUID4 = Field(
        ...,
        description="UUID4 identity for this DecisionCard instance.",
    )
    trial_id: UUID4 = Field(
        ...,
        description="UUID4 identity for the enclosing trial run.",
    )
    gate_id: Literal["G0E"] = Field(
        default="G0E",
        description="Discriminator for the G0E source-enrichment confirm gate.",
    )
    gate_focus: Literal["source_enrichment"] = Field(
        default="source_enrichment",
        description="Closed one-value marker for the G0E gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    typed_components: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Per-COMPONENT TYPE assignments (N per file; orthogonal to directive role).",
    )
    provisional_los: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Candidate LOs at status=provisional (adequacy=None until S3).",
    )
    traversal_roots: list[dict[str, Any]] = Field(
        default_factory=list,
        description="A10 enumeration roots the operator pointed the run at.",
    )
    enumeration_provenance: list[dict[str, Any]] = Field(
        default_factory=list,
        description="A10 per-source 'how it entered the set' records.",
    )
    reconcile: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "File-coverage reconcile view "
            "(n_files_in == n_files_covered + n_files_ignored)."
        ),
    )
    dissents: list[dict[str, Any]] = Field(
        default_factory=list,
        description="A3 dissent ledger surfaced for operator confirmation.",
    )
    coverage_plan: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Source-note COVERAGE PLAN view (pre-authoring, AC10): per source point's "
            "intent-set + must-cover + verbatim floor, declaring its segmentation grain. "
            "Empty {} when no coverage pass ran (byte-identical firewall)."
        ),
    )
    operator_prompt: str = Field(
        ...,
        min_length=1,
        description="Operator-facing prompt for the source-enrichment confirmation.",
    )
    verb: DecisionCardVerb = Field(
        ...,
        description="Closed decision verb set: approve | edit | reject.",
    )

    @field_validator("card_id", "trial_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID4) -> UUID4:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_created_at_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("operator_prompt")
    @classmethod
    def _reject_blank_operator_prompt(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("operator_prompt must be non-empty (excluding whitespace)")
        return value


__all__ = ["G0ECard"]
