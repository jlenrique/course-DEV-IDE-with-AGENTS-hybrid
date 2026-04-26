from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class MiraDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    mira_prompt_set: dict[str, Any] | None = None
