from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class EnriqueDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    enrique_audio: dict[str, Any] | None = None
