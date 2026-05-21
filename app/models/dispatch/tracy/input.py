from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TracyDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    brief: str | None = None
    payload_in: dict[str, Any] = Field(default_factory=dict)
