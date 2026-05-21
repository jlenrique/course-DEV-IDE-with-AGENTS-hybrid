from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class WandaDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    wanda_audio: dict[str, Any] | None = None
