from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TamaraDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    course: str | None = None
    module: str | None = None
    scope: str | None = None
    target_workflow: str | None = None
    payload_in: dict[str, Any] = Field(default_factory=dict)
