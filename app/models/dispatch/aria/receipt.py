from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class AriaDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    aria_storyline_spec: dict[str, Any] | None = None
