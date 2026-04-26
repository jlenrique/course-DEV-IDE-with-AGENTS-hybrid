from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IreneDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    pass_phase: str = Field(default="pass-2")
    payload_in: dict[str, Any] = Field(default_factory=dict)
