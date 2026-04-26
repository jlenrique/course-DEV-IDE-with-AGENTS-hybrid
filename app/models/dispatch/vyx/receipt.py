from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class VyxDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    vyx_storyboard: dict[str, Any] | None = None
