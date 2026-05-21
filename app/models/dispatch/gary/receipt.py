from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class GaryDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    generation_id: str | None = None
    status: str | None = None
    gary_slide_output: list[dict[str, Any]] | None = None
