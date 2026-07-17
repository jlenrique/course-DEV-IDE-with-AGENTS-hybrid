"""Gate G_SETTINGS DecisionCard — pre-walk settings confirm-or-change gate (Story 42.5).

Emitted when the runner PAUSES at the very BEGINNING of a real, operator-steered
run — before G0 / the first spend — on the pre-walk settings-confirmation surface.
It projects the full 16-toggle run-settings readout (Story 42.3's ``run_settings``
section) and lets the operator CONFIRM the resolved settings, or CHANGE one before
the walk proceeds.

Design note (Story 42.5, option A — a real manifest HEAD gate, operator-authorized):
this gate IS wired into ``pipeline-manifest.yaml`` as a content-free gate node
(``pre-walk-settings-gate``, ``gate_code: G0S``) at the HEAD of the walk (before
G0 / the first spend), edge-chained from ``__start__`` — mirroring the G0E/G0R
content-free confirm gates (``specialist_id: null``, ``is_content_free_gate`` ⇒
pack/HUD-invisible). It follows the "Adding a new gate" convention: step 1 (this
real DecisionCard subclass + shape-pin), step 2 (manifest gate node), step 4
(shape-pin). Step 3 is satisfied ORCHESTRATOR-side, not via a specialist
``gate_decision`` 9-node scaffold node: a pre-pipeline settings gate has NO
specialist, so — exactly like G0E/G0R — it is emitted marcus/runner-side at the
gate node using the canonical gate pause -> ``OperatorVerdict`` ->
``resume_from_verdict`` machinery. See ``docs/dev-guide.md`` §"Adding a new gate"
and ``docs/dev-guide/gate-decision-binding-semantics.md``.

Verb mapping (neutral; no preselected verdict — honors Story 42.1 finding G):
``approve`` == CONFIRM (proceed unchanged) and ``edit`` == CHANGE (alter a toggle
then re-present the updated readout). ``allowed_verbs`` threads the neutral
confirm/change pair onto the next-action surface so no verdict is pre-filled.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class GSettingsCard(DecisionCardBase):
    """Pre-walk settings confirm-or-change DecisionCard (Story 42.5, gate G_SETTINGS)."""

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
    gate_id: Literal["G0S"] = Field(
        default="G0S",
        description="Discriminator for the pre-walk settings confirm-or-change gate.",
    )
    gate_focus: Literal["pre_walk_settings_confirm"] = Field(
        default="pre_walk_settings_confirm",
        description="Closed one-value marker for the pre-walk settings gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    run_settings: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "The resolved 16-toggle run-settings readout (Story 42.3 RunSettingsSection "
            "dump) the operator confirms or changes — field -> resolved display value, "
            "in RUN_SETTINGS_TOGGLES order."
        ),
    )
    allowed_verbs: list[str] = Field(
        default_factory=lambda: ["approve", "edit"],
        description=(
            "Neutral verb menu threaded onto the next-action surface: approve==confirm, "
            "edit==change. No verb is preselected (Story 42.1 finding G)."
        ),
    )
    operator_prompt: str = Field(
        ...,
        min_length=1,
        description="Operator-facing prompt for the pre-walk settings confirmation.",
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

    @field_validator("allowed_verbs")
    @classmethod
    def _reject_empty_allowed_verbs(cls, value: list[str]) -> list[str]:
        if not value or any(not verb.strip() for verb in value):
            raise ValueError("allowed_verbs must be a non-empty list of non-empty verbs")
        return value


__all__ = ["GSettingsCard"]
