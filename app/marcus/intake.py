"""App-namespace Marcus intake helpers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.orchestrator.write_api import append_event


class PrePacketSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: str = Field(..., min_length=1)
    source_ref: str = Field(..., min_length=1)
    operator_prompt: str = Field(..., min_length=1)
    normalized_payload: dict[str, Any] = Field(default_factory=dict)


def extract_pre_packet(state: Any) -> PrePacketSnapshot:
    bundle = getattr(state, "input_bundle", {})
    snapshot = PrePacketSnapshot.model_validate(
        {
            "run_id": getattr(state, "run_id", "unknown-run"),
            "source_ref": bundle.get("source_ref", "unknown-source"),
            "operator_prompt": bundle.get("operator_prompt", ""),
            "normalized_payload": dict(bundle),
        }
    )
    event = {
        "event_type": "pre_packet_snapshot",
        "actor": "Marcus",
        "snapshot": snapshot.model_dump(mode="json"),
    }
    append_event(state, event)
    return snapshot


__all__ = ["PrePacketSnapshot", "extract_pre_packet"]
