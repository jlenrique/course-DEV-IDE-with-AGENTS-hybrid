from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class VeraDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    vera_finding: dict[str, Any] | None = None
