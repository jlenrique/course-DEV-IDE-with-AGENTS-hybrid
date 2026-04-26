from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CdDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    experience_profile_request: str | None = None
    payload_in: dict[str, Any] = Field(default_factory=dict)
