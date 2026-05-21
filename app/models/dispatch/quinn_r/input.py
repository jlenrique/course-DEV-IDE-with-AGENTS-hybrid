from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QuinnRDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    gate_phase: str = Field(default="post-composition")
    artifact_paths: list[str] = Field(default_factory=list)
    payload_in: dict[str, Any] = Field(default_factory=dict)
