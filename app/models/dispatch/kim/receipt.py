from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class KimDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    kim_checklist: dict[str, Any] | None = None
