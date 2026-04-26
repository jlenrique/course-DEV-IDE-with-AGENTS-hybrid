from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class CdDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    cd_directive: dict[str, Any] | None = None
