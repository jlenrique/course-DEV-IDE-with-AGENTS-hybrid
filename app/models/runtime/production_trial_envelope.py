"""Strict envelope for production-graph trial lifecycle state."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

LOGGER = logging.getLogger(__name__)

ProductionTrialStatus = Literal[
    "registered",
    "in-flight",
    "paused-at-gate",
    "paused-at-error",
    "waiting_for_provider_batch",
    "completed",
    "failed",
]
ProductionPreset = Literal["production", "explore"]
# G2B (variant pick) + G4A (voice pick) woken at Arc 2 (2026-06-18) — they are
# surfaced production pause points (in production_gate_ids), so the envelope's
# paused_gate must accept them. Runtime pause-order (by node index): G0E → G1 →
# G2B → G2C → G3 → G4 → G4A (G4 = the mid-pipeline fidelity gate at node "10"
# pauses BEFORE the voice pick G4A at node "11-gate"). G0E (G0-S2 source-
# enrichment confirm-gate #1) is the front-door pause when the brick is woken
# (MARCUS_G0_ENRICHMENT_ACTIVE); asleep by default so it is traversed. G0R (G0-S3
# Irene LO ratify-gate #2) follows G0E under the SAME wake flag. Literal member
# order is validation-irrelevant; this is the node-walk order, for the reader.
ProductionGateId = Literal["G0E", "G0R", "G1", "G2B", "G2C", "G3", "G4", "G4A"]


class ProductionTrialEnvelope(BaseModel):
    """Production trial registry record.

    `production_clone_launch_evidence` is deliberately required by callers. The
    runner can only set it true after a real graph step and at least one live
    specialist call have both happened.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    schema_version: Literal["production-trial-envelope.v1"] = (
        "production-trial-envelope.v1"
    )
    trial_id: UUID
    preset: ProductionPreset
    corpus_path: str
    operator_id: str
    started_at: datetime
    completed_at: datetime | None = None
    status: ProductionTrialStatus
    paused_gate: ProductionGateId | None = None
    # S4 part 2 (SCP 2026-06-11): set with status "paused-at-error" — the
    # stable machine tag of the SpecialistDispatchError that paused the run
    # (recoverable via `trial recover`, no operator verdict required).
    paused_error_tag: str | None = None
    # B3: set with status "waiting_for_provider_batch" — LiteLLM Batch id
    # being polled via `trial resume-batch` (not gate resume / not recover).
    waiting_batch_id: str | None = None
    langsmith_trace_id: str | None = None
    production_clone_launch_evidence: bool
    production_clone_launch_evidence_reason: str | None = None
    production_envelope: ProductionEnvelope
    cost_report_path: Path | None = None
    artifact_paths: list[Path] = Field(default_factory=list)

    @field_validator("trial_id")
    @classmethod
    def _enforce_trial_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("started_at")
    @classmethod
    def _enforce_started_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("completed_at")
    @classmethod
    def _enforce_completed_tz(cls, value: datetime | None) -> datetime | None:
        return enforce_tz_aware(value) if value is not None else None

    @model_validator(mode="after")
    def _lifecycle_invariants(self, info: ValidationInfo) -> ProductionTrialEnvelope:
        """Two-mode lifecycle-invariant check (drift micro-batch 2026-06-12).

        "Witness, don't gate" (Dr. Quinn synthesis, 4-voice party consensus):
        inside the S5 acceptance window a new guard must add ZERO abort paths
        on the live trial path. Default mode is **witness** — violations are
        logged and, when the validation context provides an ``anomaly_sink``
        path, appended to that JSONL sidecar (never a field; persisted
        envelope bytes stay untouched). ``invariant_mode: "strict"`` in the
        context raises instead — used by tests/CI. The witness→strict default
        flip is a post-S5 ceremony gated on a clean anomaly log
        (deferred-inventory: trial-envelope-validator-witness-to-strict-flip;
        closes composition-spec §12 limitation #9 / DFR-6.1-5).
        """
        violations: list[str] = []
        if self.status == "paused-at-gate" and self.paused_gate is None:
            violations.append("status=paused-at-gate requires paused_gate")
        if self.status == "paused-at-error" and self.paused_error_tag is None:
            violations.append("status=paused-at-error requires paused_error_tag")
        if self.status == "waiting_for_provider_batch" and not self.waiting_batch_id:
            violations.append(
                "status=waiting_for_provider_batch requires waiting_batch_id"
            )
        if self.status == "completed" and self.completed_at is None:
            violations.append("status=completed requires completed_at")
        if not violations:
            return self
        context = info.context or {}
        if context.get("invariant_mode") == "strict":
            raise ValueError(
                f"trial {self.trial_id} lifecycle invariant violation(s): "
                + "; ".join(violations)
            )
        LOGGER.warning(
            "trial %s lifecycle invariant violation(s) [witness mode]: %s",
            self.trial_id,
            "; ".join(violations),
        )
        sink = context.get("anomaly_sink")
        if sink is not None:
            try:
                with Path(sink).open("a", encoding="utf-8") as handle:
                    handle.write(
                        json.dumps(
                            {
                                "observed_at": datetime.now(tz=UTC).isoformat(),
                                "trial_id": str(self.trial_id),
                                "status": self.status,
                                "violations": violations,
                            },
                            sort_keys=True,
                        )
                        + "\n"
                    )
            except OSError:  # the witness must never become an abort path
                LOGGER.exception("anomaly sink %s unwritable; violation logged only", sink)
        return self


__all__ = [
    "ProductionGateId",
    "ProductionPreset",
    "ProductionTrialEnvelope",
    "ProductionTrialStatus",
]
