from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EnriqueDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    script: str | None = None
    voice_id: str | None = None
    mode: str | None = None
    payload_in: dict[str, Any] = Field(default_factory=dict)
