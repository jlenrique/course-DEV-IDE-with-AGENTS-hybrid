from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class DesmondDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    desmond_handoff: dict[str, Any] | None = None
