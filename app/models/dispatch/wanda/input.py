from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WandaDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    script: str | None = None
    capability: str | None = None
    voice_id: str | None = None
    payload_in: dict[str, Any] = Field(default_factory=dict)
