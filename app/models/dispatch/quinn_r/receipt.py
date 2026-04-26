from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class QuinnRDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    quinn_r_review: dict[str, Any] | None = None
