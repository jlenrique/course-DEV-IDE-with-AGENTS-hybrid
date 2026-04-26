from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DesmondDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    payload_in: dict[str, Any] = Field(default_factory=dict)
