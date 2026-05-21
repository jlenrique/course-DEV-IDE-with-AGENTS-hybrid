from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VeraDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    artifact_path: str | None = None
    source_of_truth_path: str | None = None
    payload_in: dict[str, Any] = Field(default_factory=dict)
