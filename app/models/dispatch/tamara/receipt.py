from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class TamaraDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    tamara_design_spec: dict[str, Any] | None = None
